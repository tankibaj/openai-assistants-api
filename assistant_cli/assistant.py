import sys
import getpass
import config
import logging
from assistant_cli.conversation_history import ConversationHistory
from assistant_cli.spinning_loader import SpinningLoader

# Setting up logging
logging = logging.getLogger(__name__)

# ANSI color codes
colors = {
    "highlight": "\033[93m",  # Yellow for "Starting new conversation"
    "user_title": "\033[96m",  # Cyan for "User:"
    "user_message": "\u001b[38;5;8m",  # Light gray for user's message
    "divider": "\u001b[38;5;102m",  # Dark gray for divider
    "green": "\033[32m",  # Green for "Assistant:"
    "input": "\033[37m",  # Lighter shade for user's input text
    "response": "\u001b[38;5;255m",  # White for AI's response
    "purple": "\u001b[38;5;163m",  # Purple for loader
    "exit": "\u001b[38;5;11m",  # Bright yellow for the exit message
    "reset": "\033[0m"  # Reset to default
}


class AssistantCLI:
    def __init__(self, response_handler):
        self.history = ConversationHistory(config.history_dir)
        self.username = getpass.getuser().capitalize()
        self.response_handler = response_handler

    def _display_user_prompt(self):
        print(colors["divider"] + "┌  " + colors["reset"])
        print(colors["divider"] + "│" + colors["reset"])
        sys.stdout.write(
            colors["user_title"] + f"◇  {self.username}" + colors["reset"] + "\n" + colors["divider"] + "│  ")
        sys.stdout.flush()

    def _capture_user_input(self):
        user_input = input()
        self.history.set_last_user_input(user_input)
        return user_input

    def _print_goodbye_message(self):
        print(colors["divider"] + "│" + colors["reset"])
        print(colors["divider"] + "└  " + colors["reset"] + colors["exit"] + "Stay safe!" + colors["reset"])

    def _display_user_message(self, message):
        sys.stdout.write("\033[A\033[K")
        sys.stdout.write("\033[A\033[K")
        print(colors["user_title"] + f"◆  {self.username}" + colors["reset"])
        print(colors["divider"] + "│  " + colors["user_message"] + message + colors["reset"])
        print(colors["divider"] + "│" + colors["reset"])

    def _get_response_with_loader(self, user_input):
        loader = SpinningLoader(colors["purple"])
        loader.start()
        response = self.response_handler(user_input)
        loader.stop = True
        loader.join()
        self._clear_loader_line()
        return response

    def _display_assistant_response(self, response):
        print(colors["green"] + "◆  Assistant" + colors["reset"])
        print(colors["response"] + response + colors["reset"] + "\n")
        self.history.update_history(response)

    def _clear_loader_line(self):
        sys.stdout.write("\r\033[K")

    def run(self):
        self.history.load_history_into_readline()
        while True:
            self._display_user_prompt()
            user_input = self._capture_user_input()
            if user_input.lower() == 'exit':
                self._print_goodbye_message()
                break
            self._display_user_message(user_input)
            response = self._get_response_with_loader(user_input)
            self._display_assistant_response(response)


if __name__ == "__main__":
    def assistant_response(query):
        # Placeholder for the actual assistant's response logic
        return "Mock response to: " + query


    ai_interface = AssistantCLI(response_handler=assistant_response)
    ai_interface.run()
