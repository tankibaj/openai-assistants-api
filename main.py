from openai import OpenAI
import time
import config
from utils import pretty_json

# -- Create the OpenAI client
client = OpenAI(
    api_key=config.openai_api_key,
)

# -- Create a new Thread
thread = client.beta.threads.create()
pretty_json(thread)

# -- Add a message to the Thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?",
)
pretty_json(message)


# -- Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=config.openai_assistant_id,
    model="gpt-4-1106-preview",
)


def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


run = wait_on_run(run, thread)
pretty_json(run)

messages = client.beta.threads.messages.list(thread_id=thread.id)
print("Messages:")
pretty_json(messages)
