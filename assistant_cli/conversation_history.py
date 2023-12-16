import json
import os
import datetime
import readline


class ConversationHistory:
    def __init__(self, history_dir, history_file_format="%Y-%m-%d_history.json"):
        self.history_dir = history_dir
        self.history_file_format = history_file_format
        self.last_user_input = None

    def get_history_file_path(self):
        """ Get the file path for today's history file. """
        today = datetime.datetime.now().strftime(self.history_file_format)
        return os.path.join(self.history_dir, today)

    def load_history(self):
        """ Load history from the current day's file into readline. """
        history_file = self.get_history_file_path()
        if os.path.exists(history_file):
            with open(history_file, 'r') as file:
                history = json.load(file)
                return history
        return []

    def load_history_into_readline(self):
        """ Load user inputs from the history file into readline for arrow key navigation. """
        history = self.load_history()
        for entry in history:
            if entry["user"]:  # Ensure there is a user input to add
                readline.add_history(entry["user"])

    def update_history(self, assistant_response):
        """ Update the history JSON file with the latest conversation pair. """
        if self.last_user_input is None and assistant_response is None:
            return  # Do nothing if both user input and assistant response are None

        history = self.load_history()
        history_file = self.get_history_file_path()

        # Append the new conversation pair to the history
        history.append({"user": self.last_user_input, "assistant": assistant_response})
        self.last_user_input = None  # Reset the last user input

        with open(history_file, 'w') as file:
            json.dump(history, file, indent=4)

    def set_last_user_input(self, user_input):
        """ Set the last user input. """
        self.last_user_input = user_input
