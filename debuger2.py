from assistant_initialization import assistant
from assistant_initialization import system_prompt
import config

thread_id = config.assistant_thread_id


def ask_assistant(query=None):
    response = assistant.get_assistant_response(
        thread_id=thread_id,
        instructions=system_prompt,
        user_message=query,
    )
    return response.data[0].content[0].text.value


if __name__ == "__main__":
    query = "What is the cutoff date for your training data, and can you access real-time information?"
    answer = ask_assistant(query)
    print(answer)
