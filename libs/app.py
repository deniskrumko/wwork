from clint import arguments

commands_registry = {}


def register(*keys, default=False, empty_args=False):
    """Method to register command in app."""
    def decorator(function):
        for key in keys:
            assert not commands_registry.get(key), \
                f'Command "{key}" already registered!'
            commands_registry[key] = function.__name__
        if default:
            commands_registry['__default__'] = function.__name__
        if empty_args:
            commands_registry['__empty_args__'] = function.__name__
        return function
    return decorator


class Application(object):
    def __init__(self):
        """Initialization method."""
        self.arguments = arguments.Args()
        self.flags = self.arguments.flags
        self.not_flags = self.arguments.not_flags

        self.command = self.not_flags[0] if self.not_flags else None
        self.extra = self.not_flags[1:] if self.not_flags else None

        self.default_command = commands_registry.get('__default__')
        self.empty_args_command = commands_registry.get('__empty_args__')

    def run(self):
        """Method to execute CLI application.

            1. If there are no arguments - call "__empty_args__" command if it
               exists.

            2. If requested command is in `commands_registry` - call method
               linked to this command.

            3. If requested command is not in `commands_registry` - call
               "__default__" command method if it exists.

        """
        if not self.command:
            if not self.empty_args_command:
                exit('\nRegister "empty args" command in your app!')
            method_name = self.empty_args_command
        elif self.command in commands_registry:
            method_name = commands_registry[self.command]
        else:
            if not self.default_command:
                exit('\nRegister default command in your app!')
            method_name = self.default_command

        return getattr(self, method_name)()
