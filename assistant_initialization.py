from core.assistant import AssistantManager
import config
import logging
import functions.weather as weather
import functions.web_browsing as browser
import functions.kubernetes_changelog as kubernetes_changelog
from functions.github_release_notes import get_latest_version
from functions.github_release_notes import get_release_notes


log_level = getattr(logging, config.log_level.upper(), "WARNING")
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

system_prompt = """You are an AI assistant with access to websearch and server functions.

The websearch function empowers you for real-time web search and information retrieval, particularly for current and 
relevant data from the internet in response to user queries, especially when such information is beyond your training 
data or when up-to-date information is essential. Always include the source URL for information fetched from the web.

The functions enables you to fetch information about weather, kubernetes_changelog etc etc.

All your responses should be in a human-readable format. If possible, include the source URL for information fetched.
"""

thread_id = config.assistant_thread_id

assistant = AssistantManager(
    api_key=config.openai_api_key,
    assistant_id=config.openai_assistant_id,
    functions=[
        weather.get_weather,
        browser.text_search,
        kubernetes_changelog.query_by_version,
        get_latest_version,
        get_release_notes
    ]
)
