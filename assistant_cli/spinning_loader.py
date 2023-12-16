import sys
import time
import threading


colors = {
    "reset": "\033[0m"  # Reset to default
}

class SpinningLoader(threading.Thread):
    """
    Loader animation class for spinning dot effect.
    """

    def __init__(self, color_code, delay=0.1):
        super().__init__()
        self.stop = False
        self.color_code = color_code
        self.delay = delay
        self.spin_sequence = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def run(self):
        while not self.stop:
            for char in self.spin_sequence:
                sys.stdout.write("\r" + self.color_code + char + " Thinking..." + colors["reset"])
                sys.stdout.flush()
                time.sleep(self.delay)
