import os

from colorama import Fore, init

init(convert=True)

FOLDER_LOCATION: str = os.path.abspath(os.getcwd()).replace("\\", "/")


class Colors:
    HEADER = Fore.MAGENTA
    OKBLUE = Fore.BLUE
    OKCYAN = Fore.CYAN
    OKGREEN = Fore.GREEN
    WARNING = Fore.YELLOW
    FAIL = Fore.RED
    ENDC = Fore.RESET
    BOLD = Fore.LIGHTBLACK_EX
