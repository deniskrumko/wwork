from functools import wraps

__unknown__ = '__unknown__'
__empty__ = '__empty__'


class classproperty:
    """Class property."""

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


def yes_no_input(message):
    """Input with yes/no variants."""
    result = input(f'\n{message} [y/n]\n>>> ')
    return result in ('y', 'yes', '1')


def worklog_required(func):
    """Decorator for requiring `current_worklog`."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(self, *args, **kwargs) if self.worklog else None
    return wrapper


def debugger(func):
    """Decorator for debugging.

    TODO: Enable dynamic disabler.

    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f'-- {self} -- {func.__name__} --')
        return func(self, *args, **kwargs)
    return wrapper


def register_command(*args):
    """Decorator for registering command."""
    registry = getattr(register_command, 'registry', None)
    if not registry:
        register_command.registry = {}

    def inner(func):
        for key in args:
            register_command.registry[key] = func.__name__

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)
        return wrapper
    return inner
