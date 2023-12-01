import time
import json
import logging
from typing import Optional, Callable, List, Dict, Generator
from openai import OpenAI, OpenAIError
from core.parser import FunctionDefinitionParser

logger = logging.getLogger(__name__)


class AssistantManager:
    def __init__(self, api_key, assistant_id, model="gpt-4-1106-preview", functions: Optional[List[Callable]] = None):
        """
        Initialize the AssistantManager with the necessary OpenAI parameters.

        Args:
            api_key (str): API key for OpenAI.
            assistant_id (str): Identifier for the specific assistant.
            model (str): The model version to be used, default is 'gpt-4-1106-preview'.

        Raises:
            ValueError: If any required parameters are missing or invalid.
        """
        if not api_key or not assistant_id:
            raise ValueError("API key and Assistant ID are required")

        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.model = model
        self.function_parser = FunctionDefinitionParser()  # Initialize the parser first
        self.functions = self._parse_functions(functions)  # Then use it in _parse_functions
        self.func_mapping = self._create_func_mapping(functions)

        # Unpacking the generator here
        self.tools = [
            {"type": "code_interpreter"},
            {"type": "retrieval"},
            *self.functions  # Unpack the generator
        ]

    def _parse_functions(self, functions: Optional[List[Callable]]) -> Generator[Dict, None, None]:
        """Yields each 'python function' as a JSON-serializable dict."""
        if functions is not None:
            for func in functions:
                yield self.function_parser.convert_function_to_json_schema(func)

    def _create_func_mapping(self, functions: Optional[List[Callable]]) -> Dict[str, Callable]:
        """Creates a mapping between the function names and function definitions."""
        if functions is None:
            return {}
        return {func.__name__: func for func in functions}

    def debug_tools(self):
        print(self.tools)

    def create_thread(self):
        """
        Create a new conversation thread.

        Returns:
            Thread: The newly created thread object.

        Raises:
            OpenAIError: If the API call fails.
        """
        try:
            thread = self.client.beta.threads.create()
            return thread
        except OpenAIError as e:
            logger.error(f"Failed to create thread: {e}")
            raise

    def _add_message_to_thread(self, thread_id, role, content, file_ids=None):
        """
        Add a message to a specified thread.

        Args: thread_id (str): The ID of the thread to create a message for. role (str): The role of the entity that
        is creating the message. Currently only user is supported. content (str): The content of the message.
        file_ids (List[str] | None): A list of File IDs that the message should use. There can be a maximum of 10
        files attached to a message. Useful for tools like retrieval and code_interpreter that can access and use files.

        Raises:
            OpenAIError: If the API call fails.
        """
        if file_ids is None:
            file_ids = []
        try:
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=content,
                file_ids=file_ids
            )
        except OpenAIError as e:
            logger.error(f"Failed to add message to thread {thread_id}: {e}")
            raise

    def _run_assistant(self, thread_id, instructions):
        """
        Run the assistant on the specified thread with given instructions.

        Args:
            thread_id (str): The ID of the thread.
            instructions (str): Instructions for the assistant.

        Returns:
            Run: The run object initiated by the assistant.

        Raises:
            OpenAIError: If the API call fails.
        """
        try:
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                model=self.model,
                instructions=instructions,
                tools=self.tools
            )
            return run
        except OpenAIError as e:
            logger.error(f"Failed to run assistant on thread {thread_id}: {e}")
            raise

    def cancel_run(self, run_id, thread_id):
        """
        Cancel a run.

        Args:
            run_id (str): The ID of the run.
            thread_id (str): The ID of the thread.

        Raises:
            OpenAIError: If the API call fails.
        """
        try:
            self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
        except OpenAIError as e:
            logger.error(f"Failed to cancel run {run_id} on thread {thread_id}: {e}")
            raise

    def _wait_for_run_completion(self, run_id, thread_id, check_interval=3, max_wait_time=10):
        """
        Wait for a run to complete, checking its status periodically.

        Args: run_id (str): The ID of the run. thread_id (str): The ID of the thread.
        check_interval (int): Time in seconds to wait between status checks. Default is 5 seconds.
        max_wait_time (int | None): Maximum time in seconds to wait for the run to complete. If None, wait indefinitely.

        Returns:
            Messages: Messages from the completed run.

        Raises:
            OpenAIError: If the API call fails or the maximum wait time is exceeded.
        """
        start_time = time.time()
        while True:
            try:
                run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                current_time = time.time()

                logger.debug(f"Run status: {run_status.status}")

                if run_status.status == 'completed':
                    return self._retrieve_thread_messages(thread_id)
                elif run_status.status == 'requires_action':
                    logger.debug("Processing required tool calls.")
                    required_actions = run_status.required_action.submit_tool_outputs.model_dump()
                    logger.debug(f"Required actions: {required_actions}")
                    tool_outputs = self._handle_tool_call(required_actions)
                    logger.debug(f"Tool outputs: {tool_outputs}")

                    # Submitting tool outputs back to the assistant
                    self.client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread_id,
                        run_id=run_id,
                        tool_outputs=tool_outputs
                    )
                elif max_wait_time and (current_time - start_time) > max_wait_time:
                    error_msg = f"Maximum wait time exceeded for run {run_id}"
                    logger.warning(error_msg)
                    raise TimeoutError(error_msg)
                elif run_status.status not in ["queued", "in_progress"]:
                    logger.warning(f"Run {run_id} ended with status: {run_status.status}")
                    break

                time.sleep(check_interval)
            except OpenAIError as e:
                logger.error(f"Error while waiting for run completion: {e}")
                raise

    def _handle_tool_call(self, required_actions):
        """
        Handles tool calls made by the OpenAI Assistant.

        Args:
            required_actions: Actions required as indicated by the OpenAI Assistant.

        Returns:
            List of tool outputs to submit back to the Assistant.
        """
        tool_outputs = []
        for action in required_actions["tool_calls"]:
            func_name = action['function']['name']
            arguments = json.loads(action['function']['arguments'])

            if func_name in self.func_mapping:
                output = self._call_function(func_name, arguments)
                # Convert output to JSON string if it's a dictionary
                if isinstance(output, dict):
                    output = json.dumps(output)
                tool_outputs.append({
                    "tool_call_id": action['id'],
                    "output": output
                })
            else:
                raise ValueError(f"Unknown function: {func_name}")

        return tool_outputs

    def _call_function(self, func_name: str, args: Dict):
        """
        Calls the actual function when invoked in _handle_tool_call.

        Args:
            func_name: The name of the function to call.
            args: Arguments for the function.

        Returns:
            The result of the function call.
        """
        try:
            logger.debug(f"Calling function '{func_name}' with arguments: {args}")
            func = self.func_mapping.get(func_name)
            if func:
                result = func(**args)
                logger.debug(f"Function '{func_name}' returned: {result}")
                return result
            else:
                raise ValueError(f"Function {func_name} not implemented")
        except Exception as e:
            logger.error(f"Error in calling function {func_name} with arguments: {args}, error: {e}", exc_info=True)
            raise

    def _retrieve_thread_messages(self, thread_id):
        """
        Retrieve all messages from a specified thread.

        Args:
            thread_id (str): The ID of the thread.

        Returns:
            List[Message]: A list of messages from the thread.

        Raises:
            OpenAIError: If the API call fails.
        """
        try:
            messages = self.client.beta.threads.messages.list(thread_id)
            return messages
        except OpenAIError as e:
            logger.error(f"Failed to retrieve messages from thread {thread_id}: {e}")
            raise

    def get_assistant_response(self, instructions, user_message, file_ids=None, thread_id=None, check_interval=5,
                               max_wait_time=None):
        """
        Send a message, run the assistant, and retrieve the response.

        Args:
            instructions (str): Instructions for the assistant.
            user_message (str): The user's message to add to the thread.
            file_ids (List[str] | None): A list of File IDs that the message should use.
            thread_id (str | None): The ID of the thread. If None, a new thread is created.
            check_interval (int): Time in seconds to wait between status checks. Default is 5 seconds.
            max_wait_time (float | None): Maximum time in seconds to wait for the run to complete. If None, wait indefinitely.

        Returns:
            List of Messages: The list of messages after the assistant has completed the run.

        Raises:
            OpenAIError: If any step in the process fails.
        """
        try:
            if thread_id is None:
                thread = self.create_thread()
                thread_id = thread.id

            self._add_message_to_thread(thread_id=thread_id, role="user", content=user_message, file_ids=file_ids)
            run = self._run_assistant(thread_id=thread_id, instructions=instructions)

            return self._wait_for_run_completion(thread_id=thread_id, run_id=run.id, check_interval=check_interval,
                                                 max_wait_time=max_wait_time)
        except OpenAIError as e:
            logger.error(f"Failed to get assistant response: {e}")
            raise
