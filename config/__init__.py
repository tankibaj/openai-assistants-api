import os
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
openai_assistant_id = os.getenv('OPENAI_ASSISTANT_ID')
openweathermap_key = os.getenv("OPENWEATHERMAP_KEY")
kubernetes_changelog_db_host = os.getenv("KUBERNETES_CHANGELOG_DB_HOST")
kubernetes_changelog_db_port = os.getenv("KUBERNETES_CHANGELOG_DB_PORT")
kubernetes_changelog_db_name = os.getenv("KUBERNETES_CHANGELOG_DB_NAME")
kubernetes_changelog_db_user = os.getenv("KUBERNETES_CHANGELOG_DB_USER")
kubernetes_changelog_db_password = os.getenv("KUBERNETES_CHANGELOG_DB_PASSWORD")
assistant_thread_id = os.getenv("ASSISTANT_THREAD_ID")
history_dir = os.getenv("HISTORY_DIR", "./")
