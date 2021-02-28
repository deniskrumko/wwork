from functools import wraps
from typing import List

from colors import printer
from resources import Command, LogType


class cached_property(object):
    """Cached property decorator."""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


def safe_input(message: str = '', end='\n') -> str:
    """User input with try-except."""
    try:
        if message:
            printer(message, end=end)
        return input()
    except KeyboardInterrupt:
        printer('\n<r>Goodbye!</r>')
        exit()


def yes_no_input(message: str) -> str:
    """Input with yes/no variants."""
    result = safe_input(f'\n{message} [Y/n]\n>>> ', end='')
    return result in ('y', 'yes', '1', '')


def single_choice_input(check, is_digit: bool = True, return_checked: bool = False):
    """Input with single choice."""
    while True:
        value = safe_input()

        if is_digit:
            if not value.isdigit():
                printer(f'Value must be a digit: <r>{value}</r>\n>>> ', end='')
                continue
            value = int(value)

        checked_value = check(value)
        if not checked_value:
            printer(f'Incorrect value: <r>{value}</r>\n>>> ', end='')
            continue

        return checked_value if return_checked else value


def register(
    command: Command,
    log_types: List[LogType] = None,
    file_exists: bool = True,
):
    """Decorator for registering command."""
    registry = getattr(register, '_func_registry', None)
    if not registry:
        register._func_registry = {}

    registry = getattr(register, '_log_type_registry', None)
    if not registry:
        register._log_type_registry = {}

    def inner(func):
        register._func_registry[command] = func.__name__
        if log_types is not None:
            register._log_type_registry[func.__name__] = log_types

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not file_exists and self.log_file.exists:
                return printer('\n<r>Day already started!</r>')

            if file_exists and not self.log_file.exists:
                return printer(f'\n<r>File for date {self.current_date_str} does not exist</r>')

            return func(self, *args, **kwargs)
        return wrapper
    return inner
