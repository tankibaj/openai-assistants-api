from assistant_initialization import assistant
from assistant_initialization import system_prompt
import config


thread_id = config.assistant_thread_id


def display_thread_messages(messages):
    for message in messages.data:
        role = message.role
        content = message.content[0].text.value
        print(f"{role.capitalize()}: {content}")


def main(thread_id, system_prompt=system_prompt, user_message="", file_ids=None):
    response = assistant.get_assistant_response(
        thread_id=thread_id,
        instructions=system_prompt,
        user_message=user_message,
        file_ids=file_ids
    )
    # -- Print messages
    display_thread_messages(response)


if __name__ == '__main__':
    # -- Create thread
    # thread = assistant.create_thread()
    # print(thread)

    # -- Delete thread
    # thread = assistant.delete_thread(thread_id)
    # print(thread)

    # -- Retrieve thread messages
    # response = assistant._retrieve_thread_messages(thread_id)
    # display_thread_messages(response)

    # -- Get assistant response
    # query = "What is the weather in Lagos?"
    query = "What is the cutoff date for your training data, and can you access real-time information?"
    # query = "What are breaking changes in Kubernetes v1.25.0"
    # query = "What should I consider before upgrading from Kubernetes 1.27 to Kubernetes 1.28?"
    # query = "What the latest version of the Kubernetes?"
    # query = "What is the weather in Berlin?"
    main(thread_id, system_prompt=system_prompt, user_message=query)

    # Cancel a run
    # assistant.cancel_run(run_id="run_Uz5DCdnR5papdGqrJCRtuX4a", thread_id)

    # -- Debug tools schema
    # assistant.debug_tools()
