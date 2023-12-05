import logging
from core.assistant import AssistantManager
import config
import functions.weather as weather
import functions.web_browsing as browser

logging.basicConfig(level=logging.INFO)
logging = logging.getLogger(__name__)

assistant = AssistantManager(
    api_key=config.openai_api_key,
    assistant_id=config.openai_assistant_id,
    functions=[
        weather.get_weather,
        browser.text_search,
    ]
)


def display_thread_messages(messages):
    for message in messages.data:
        role = message.role
        content = message.content[0].text.value
        print(f"{role.capitalize()}: {content}")


def main():
    response = assistant.get_assistant_response(
        thread_id="thread_BbFoFrOGpw7hpFCjoE6zlJNh",
        instructions="You are a personal math tutor. When asked a math question, write and run code to answer the "
                     "question.",
        # file_ids=["file_ckt30hTJn1q2f2j1Nz8Z6y1Y"],
        # user_message="I need to solve the equation `3x + 11 = 14`. Can you help me?"
        # user_message="remember x = 56"
        # user_message="what is value of x?"
        user_message="What is 20% of 700000?"
    )
    # -- Print messages
    display_thread_messages(response)


if __name__ == '__main__':
    # -- Create thread
    # thread = assistant.create_thread()
    # print(thread)

    # -- Delete thread
    # thread = assistant.delete_thread(thread_id="thread_ckt30hTLdRycKOc1NIj1KJZb")
    # print(thread)

    # -- Retrieve thread messages
    # response = assistant._retrieve_thread_messages(thread_id="thread_ckt30hTLdRycKOc1NIj1KJZb")
    # display_thread_messages(response)

    # -- Get assistant response
    main()

    # Cancel a run
    # assistant.cancel_run(run_id="run_Uz5DCdnR5papdGqrJCRtuX4a", thread_id="thread_ckt30hTLdRycKOc1NIj1KJZb")

    # -- Debug tools schema
    # assistant.debug_tools()
