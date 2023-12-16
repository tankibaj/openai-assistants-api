import logging
from core.assistant import AssistantManager
import config
import functions.weather as weather
import functions.web_browsing as browser
import functions.kubernetes_changelog as kubernetes_changelog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

system_prompt = """You are an AI assistant with access to websearch and server functions.

The websearch function empowers you for real-time web search and information retrieval, particularly for current and 
relevant data from the internet in response to user queries, especially when such information is beyond your training 
data or when up-to-date information is essential. Always include the source URL for information fetched from the web.

The functions enables you to fetch information about weather, kubernetes_changelog etc etc.

All your responses should be in a human-readable format.
"""

assistant = AssistantManager(
    api_key=config.openai_api_key,
    assistant_id=config.openai_assistant_id,
    functions=[
        weather.get_weather,
        browser.text_search,
        kubernetes_changelog.query_by_version,
    ]
)


def display_thread_messages(messages):
    for message in messages.data:
        role = message.role
        content = message.content[0].text.value
        print(f"{role.capitalize()}: {content}")


def main(thread_id):
    response = assistant.get_assistant_response(
        thread_id=thread_id,
        instructions=system_prompt,
        # file_ids=["file_ckt30hTJn1q2f2j1Nz8Z6y1Y"],
        # user_message="remember x = 56"
        # user_message="what is value of x?"
        # user_message="What are breaking changes in Kubernetes v1.25.0?"
        # user_message="What the latest version of the Kubernetes?"
        user_message="What should I consider before upgrading from Kubernetes 1.27 to Kubernetes 1.28?"
    )
    # -- Print messages
    display_thread_messages(response)


if __name__ == '__main__':
    # -- Create thread
    # thread = assistant.create_thread()
    # print(thread)

    thread_id = config.assistant_thread_id  # "thread_mSJztCaNdLVr9Svad57mEZFV"

    # -- Delete thread
    # thread = assistant.delete_thread(thread_id)
    # print(thread)

    # -- Retrieve thread messages
    # response = assistant._retrieve_thread_messages(thread_id)
    # display_thread_messages(response)

    # -- Get assistant response
    main(thread_id)

    # Cancel a run
    # assistant.cancel_run(run_id="run_Uz5DCdnR5papdGqrJCRtuX4a", thread_id)

    # -- Debug tools schema
    # assistant.debug_tools()
