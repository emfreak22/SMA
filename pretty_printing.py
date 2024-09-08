def print_green(text):
    BOLD_UNDERLINE_GREEN = "\033[1;4;32m"
    RESET = "\033[0m"
    print(f"{BOLD_UNDERLINE_GREEN}{text}{RESET}")


def print_red(text):
    RED = "\033[31m"
    RESET = "\033[0m"
    print(f"{RED}{text}{RESET}")


def print_blue(text):
    BOLD_UNDERLINE_ELECTRIC_BLUE = "\033[1;4;94m"
    RESET = "\033[0m"
    print(f"{BOLD_UNDERLINE_ELECTRIC_BLUE}{text}{RESET}")


def print_golden(text):
    BOLD_UNDERLINE_GOLDEN = "\033[1;4;33m"
    RESET = "\033[0m"
    print(f"{BOLD_UNDERLINE_GOLDEN}{text}{RESET}")
