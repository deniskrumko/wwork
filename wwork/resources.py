from enum import Enum


class Command(Enum):
    # Private commands
    EMPTY = '__empty__'
    LOG = '__log__'

    # Public commands
    START = 'start'
    FINISH = 'finish'
    INFO = 'info'
    EDIT = 'edit'
    UNDO = 'undo'
    PAUSE = 'pause'
    HELP = 'help'


class LogType(Enum):
    CURRENT = 'current'
    FILL = 'fill'
    INCREMENT = 'increment'
    EXACT = 'exact'


class TaskType(Enum):
    EXACT = '__exact__'
    EMPTY = '__empty__'


class EditAction(Enum):
    TIME = 'time'
    TASK = 'task'
    MESSAGE = 'msg'
    DELETE = 'del'


TIME_FORMAT = '%H:%M'
DATE_FORMAT = '%Y-%m-%d'
