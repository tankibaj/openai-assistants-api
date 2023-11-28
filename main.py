import logging
from core.assistant import AssistantManager
import config

logging.basicConfig(level=logging.INFO)
logging = logging.getLogger(__name__)


def main():
    assistant = AssistantManager(api_key=config.openai_api_key, assistant_id=config.openai_assistant_id)

    # thread = assistant.create_thread()
    # print(thread)

    response = assistant.get_assistant_response(
        thread_id="thread_ckt30hTLdRycKOc1NIj1KJZb",
        instructions="You are a personal math tutor. When asked a math question, write and run code to answer the "
                     "question.",
        # file_ids=["file_ckt30hTJn1q2f2j1Nz8Z6y1Y"],
        # user_message="I need to solve the equation `3x + 11 = 14`. Can you help me?"
        # user_message="remember x = 56"
        user_message="what is value of x?"
    )

    for message in response.data:
        role = message.role
        content = message.content[0].text.value
        print(f"{role.capitalize()}: {content}")


if __name__ == '__main__':
    main()
