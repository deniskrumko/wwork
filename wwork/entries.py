from colors import green, no_color
from messages import messages
from exceptions import EntryCommandNotFound

__all__ = ('Entry',)


class Commands:
    START = 'start'
    WORK = 'work'
    PAUSE = 'pause'
    PAUSE_END = 'pause_end'


commands_config = {
    Commands.START: (messages['start_work'], green),
    Commands.WORK: (None, no_color),
}


class Entry:

    def __init__(self, command, time, task=None, log=None):
        """Initialize class instance."""
        if command not in commands_config:
            raise EntryCommandNotFound(command)

        self.__command = command
        self.__time = time
        self.__task = task
        self.__log = log

    def __repr__(self):
        return f'{self.__time} ({self.__command}): {self.__task} {self.__log}'

    def pretty_print(self, task_length=9, prefix=''):
        default_message, color = commands_config[self.__command]
        placeholder = '*' * task_length
        margin = task_length + 3
        time = self.__time
        log = (self.__log or default_message) * color
        task = ((self.__task or placeholder) + ' ' * margin)[:margin]
        print(f'{prefix}{time}   {task}{log}')

    def to_json(self):
        return {
            'command': self.__command,
            'time': self.__time,
            'task': self.__task,
            'log': self.__log,
        }

    @classmethod
    def from_json(cls, data):
        return cls(
            command=data.get('command'),
            time=data.get('time'),
            task=data.get('task'),
            log=data.get('log'),
        )

    @property
    def task(self):
        return self.__task
