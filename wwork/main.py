import re
import sys
from copy import copy
from datetime import date, datetime, time, timedelta
from typing import Union

from colors import green, printer, red
from entries import LogEntry
from files import LogFile
from resources import DATE_FORMAT, TIME_FORMAT, Command, EditAction, LogType, TaskType
from utils import cached_property, register, single_choice_input, yes_no_input


class WWork:
    """Class for work management."""

    def __init__(self, *args, **kwargs):
        """Initialize class instance."""
        self.args = sys.argv[1:]

        # Command related
        self.command: Command = None
        self.go_back: int = 0

        # Task related
        self.task_type: TaskType = None
        self.task_value: str = None

        # Log related
        self.log_message: str = None
        self.log_type: LogType = None
        self.log_type_value: Union[int, time] = None

    def run(self):
        """Run command processing."""
        # Parse CLI arguments
        self.parse_command()

        # Find function for command
        func_name = register._func_registry.get(self.command)
        if not func_name:
            raise ValueError(f'Command "{self.command.name}" is not registered!')

        # Check log types limitations
        available_log_types = register._log_type_registry.get(func_name)
        if available_log_types is not None and self.log_type not in available_log_types:
            return printer(
                f'\n<r>Command "{self.command.value}" does not support '
                f'log type "{self.log_type.value}"</r>',
            )

        # Call command handler
        getattr(self, func_name)()

    # COMMANDS
    # ========================================================================

    @register(Command.EMPTY)
    def show(self):
        """Show logged entries."""
        if not self.log_file.exists:
            return printer(f'\n<r>File for date {self.current_date_str} does not exist</r>')

        for i, entry in enumerate(self.log_file.logs):
            printer(('\n' if i == 0 else '') + entry.colored_value)

    @register(Command.START, log_types=[LogType.CURRENT, LogType.EXACT], file_exists=False)
    def start(self):
        """Start new work day.

        Creates initial entry and shows welcome message.
        """
        self.add_entry_and_save()

        if self.current_time.hour < 12:
            welcome_msg = 'Good morning! 🌝'
        elif self.current_time.hour < 18:
            welcome_msg = 'Good day! 💫'
        else:
            welcome_msg = 'Good evening! 🌚'

        printer(
            f'\n<g>{welcome_msg}</g>\n'
            f'\nToday is <g>{self.current_date_str}</g> and it\'s <g>{self.current_time_str}</g>',
        )

    @register(Command.PAUSE, log_types=[LogType.CURRENT, LogType.EXACT])
    def pause(self):
        """Start or stop pause in work."""
        PAUSE_START, PAUSE_END = 'Pause started', 'Pause finished'
        is_finished = self.log_file.logs[-1].log_message == PAUSE_START

        self.log_message = PAUSE_END if is_finished else PAUSE_START
        entry = self.add_entry_and_save()

        if entry:
            duration_msg = f' ({self.log_file.last_command_duration} min.)' if is_finished else ''
            printer(f'\n{self.log_message} at <y>{entry.command_time_str}</y>{duration_msg}')

    @register(Command.FINISH)
    def finish(self):
        print('FINISH')
        # TODO: Округление - публикация в джиру

    @register(Command.EDIT)
    def edit(self):
        """Edit entries."""
        count: int = len(self.log_file.logs)

        # Show all entries with numbers
        for i, entry in enumerate(self.log_file.logs, 1):
            pre = ('\n' if i == 1 else '') + ('  ' if i < 10 else ' ')
            printer(f'{pre}<y>[{i}]</y>{entry.colored_value}')

        # Get user command
        actions = list(action.value for action in EditAction)
        printer(
            f'\nEnter command like: <y>number</y> <g>{"/".join(actions)}</g> <b>value</b>\n>>> ',
            end='',
        )

        # Match user input
        command_pattern: str = f'(?P<number>\d+) (?P<action>{"|".join(actions)}) ?(?P<value>.*)?$'
        match = single_choice_input(
            check=lambda x: re.match(command_pattern, x),
            is_digit=False,
            return_checked=True,
        )

        # Find entry by selected number
        try:
            selected_entry_number: int = int(match['number']) - 1
            entry: LogEntry = self.log_file.logs[selected_entry_number]
        except IndexError:
            printer(f'\n<r>Incorrect entry number: {match["number"]}. Please, try again.</r>')
            return self.edit()

        new_entry: LogEntry = copy(entry)
        action: EditAction = EditAction(match['action'])
        value: str = match['value']

        to_save: bool = False
        to_delete: bool = False

        # Change entry time
        if action == EditAction.TIME:
            if entry.log_type == LogType.FILL:
                return printer('\n<r>You can\'t change time for log type "FILL"</r>')

            try:
                new_time = datetime.strptime(':'.join([value[:2], value[-2:]]), TIME_FORMAT).time()
                new_entry.command_time = new_time
            except Exception:
                return printer(
                    f'\n<r>Incorrect time format: {value}. '
                    'Must match HH:MM or HHMM format. Please, try again.</r>',
                )

        # Change entry task
        elif action == EditAction.TASK:
            if entry.command != Command.LOG:
                return printer(
                    f'\n<r>Can\'t change task for command of type "{entry.command.name}". '
                    'Please, try again.</r>',
                )
            new_entry.task_value = value

        # Change entry message
        elif action == EditAction.MESSAGE:
            if entry.command != Command.LOG:
                return printer(
                    f'\n<r>Can\'t change message for command of type "{entry.command.name}". '
                    'Please, try again.</r>',
                )
            new_entry.log_message = value

        # Delete entry
        elif action == EditAction.DELETE:
            to_delete = True
            if entry.command == Command.START:
                if yes_no_input('You about to delete <r>FILE FOR THIS DAY</r>! Are you sure?'):
                    if yes_no_input('File <r>WILL BE DELETED</r> right now. Okay?'):
                        self.log_file.terminate()
                        return printer(f'\nFile <y>{self.log_file._path}</y> was deleted')

        # Show "before -> after" entries and let user decide
        if action == EditAction.DELETE:
            printer(f'\n<r>{entry.uncolored_value}</r>')
            action_msg = 'Agree to delete this entry?'
        else:
            printer(f'\n{entry.get_printable(highligh_fields={action.value: red})}')
            printer(f'{new_entry.get_printable(highligh_fields={action.value: green})}')
            action_msg = f'Agree to change <g>{action.value}</g>?'

        # Ask user to agree with changes
        if yes_no_input(action_msg):
            self.log_file.logs[selected_entry_number] = new_entry
            to_save = True

        # Shift time for entries
        if (
            to_save
            and (selected_entry_number + 1) != count
            and action in [EditAction.TIME, EditAction.DELETE]
            and entry.log_type != LogType.FILL  # Filler is not shifted
        ):
            shift_time: timedelta = (
                self.log_file.logs[selected_entry_number - 1] - entry
                if to_delete else new_entry - entry
            )

            for entry in self.log_file.logs[selected_entry_number + 1:]:
                entry.shift_command_time(shift=shift_time)

            shifted = len(self.log_file.logs[selected_entry_number + 1:])
            printer(f'\n<g>{shifted} commands</g> were also shifted in time')

        # Delete entry from logs
        if to_delete:
            self.log_file.logs.pop(selected_entry_number)

        # Save all changes to file
        if to_save:
            self.log_file.save()

        return printer('\n<g>Saved</g> ✅' if to_save else '\n<r>Declined</r> ⛔️')

    @register(Command.UNDO)
    def undo(self):
        """Delete last command in entries."""
        last_log = self.log_file.logs[-1]
        if last_log.command in [Command.LOG, Command.PAUSE]:
            printer(f'\n<r>{last_log.uncolored_value}</r>')
            if yes_no_input('Delete this command?'):
                self.log_file.logs.pop()
                self.log_file.save()
        else:
            printer(f'\n<y>{last_log.colored_value}</y>')
            printer(f'Can\'t delete log of type "{last_log.command.value}"')

    @register(Command.LOG)
    def log_work(self):
        """Log command to file."""
        entry = self.add_entry_and_save()
        if entry:
            printer(f'\n<g>{entry.uncolored_value}</g>\n\nTask is logged 👍')

    # METHODS
    # ========================================================================

    def add_entry(self) -> LogEntry:
        """Add new entry to logs of current file.

        TODO: Probably delete this method and use only `add_entry_and_save`.
        """
        if self.log_file.exists and self.command_time < self.log_file.last_time:
            return printer(
                f'\nLast command time is <g>{self.log_file.last_time_str}</g>, '
                f'but you\'re trying to log <r>{self.command_time_str}</r>',
            )

        return self.log_file.add_entry(
            command=self.command,
            command_time=self.command_time,
            log_type=self.log_type,
            log_message=self.log_message,
            task_type=self.task_type,
            task_value=self.task_value,
        )

    def add_entry_and_save(self) -> LogEntry:
        """Add new entry and save file."""
        entry = self.add_entry()
        self.log_file.save()
        return entry

    def parse_command(self):
        """Parse CLI arguments."""
        first = self.args[0] if self.args else ''
        last = self.args[-1] if self.args else ''
        exclude = set()

        # 1. Determine `go back` parameter

        # Example: ww edit yyyyyy --> 5 days back
        match = re.match('[Yy]+$', last)
        if match:
            self.go_back = match.end()

        # Example: ww edit y10 --> 10 days back
        match = re.match('[Yy](?P<count>\d+)$', last)
        if match:
            self.go_back = int(match['count'])

        if self.go_back:
            exclude.add(last)

        # 2. Determine command

        # Example: ww --> show main screen
        # Example (2): ww y --> show main screen for yesterday file
        if not [v for v in self.args if v not in exclude]:
            self.command = Command.EMPTY
            return

        # Example: ww start / ww finish / ww pause / ww edit
        for command in Command:
            if command.value == first or (len(first) == 1 and command.value[0] == first):
                self.command = command

        # Example: ww 1234 something --> means `log that`
        if not self.command:
            self.command = Command.LOG

        # 3. Determine log mode

        # Example: ww start 1030 --> start at 10:30
        if len(last) == 4 and last.isdigit():
            self.log_type = LogType.EXACT
            self.log_type_value = datetime.strptime(
                ':'.join([last[:2], last[-2:]]), TIME_FORMAT,
            ).time()

        # Example: ww mrpl1234 something +35 --> add 35 minutes to last
        if last.startswith('+') and last[1:].isdigit():
            self.log_type = LogType.INCREMENT
            self.log_type_value = int(last[1:])

        # Example: ww mrpl1234 something fill --> fill whole day
        if last == LogType.FILL.value:
            self.log_type = LogType.FILL

        # Example: ww mrpl1234 something --> use current time
        if not self.log_type:
            self.log_type = LogType.CURRENT
        else:
            exclude.add(last)

        # 4. Determine task

        # Example: ww 1234 something --> task MRPL-1234 as MRPL is default
        if first.isdigit():
            self.task_type = TaskType.EXACT
            self.task_value = f'{self.default_project}-{first}'
        # Example: ww st +30 --> `st` is a shortcut for `standup`
        elif first in self.shortcuts:
            self.task_type = TaskType.EXACT
            self.task_value = self.shortcuts[first][0]
            if self.shortcuts[first][1]:
                # Shortcut can also defint log message
                self.log_message = self.shortcuts[first][1]
        # Example: ww rnd1234 something --> task RND-1234 as RND in available
        # Alternative: ww rnd-1234 / ww RND.1234 / ww rNd_1234
        else:
            match = re.match(r'(?P<project>[A-Za-z]+)(?:\-|\_|\.|)(?P<number>\d+)$', first)
            if match:
                self.task_type = TaskType.EXACT
                self.task_value = f'{match["project"].upper()}-{match["number"]}'

        # Example: ww something --> task is unknown
        if not self.task_type:
            self.task_type = TaskType.EMPTY
        else:
            exclude.add(first)

        # 5. Determine log message

        if self.command == Command.LOG and not self.log_message:
            self.log_message = ' '.join(v for v in self.args if v not in exclude)

    # PROPERTIES
    # ========================================================================

    @cached_property
    def current_date(self) -> date:
        """Get current date for command (may be shifted by `go_back` option)."""
        return datetime.now().date() - timedelta(days=self.go_back)

    @cached_property
    def current_date_str(self) -> str:
        """Get current date as string."""
        return self.current_date.strftime(DATE_FORMAT)

    @cached_property
    def current_time(self) -> time:
        """Get current time (only hours and minutes)."""
        return datetime.now().time().replace(microsecond=0, second=0)

    @cached_property
    def current_time_str(self) -> time:
        """Get current time as string."""
        return self.current_time.strftime(TIME_FORMAT)

    @cached_property
    def log_file(self) -> LogFile:
        """Get current date log file."""
        return LogFile(self.current_date_str)

    @cached_property
    def command_time(self) -> time:
        """Get command time."""
        if not self.log_type:
            raise ValueError('Log type is not defined!')

        if self.log_type == LogType.CURRENT:
            return self.current_time

        if self.log_type == LogType.EXACT:
            if not isinstance(self.log_type_value, time):
                raise TypeError('Log type value must be a `time` instance!')
            return self.log_type_value

        if self.log_file.last_time is None:
            raise ValueError(f'Cannot support log type {self.log_type} as file has no last time!')

        if self.log_type == LogType.FILL:
            return self.log_file.last_time

        if self.log_type == LogType.INCREMENT:
            return (
                datetime.combine(date.today(), self.log_file.last_time)
                + timedelta(minutes=self.log_type_value)
            ).time()

    @cached_property
    def command_time_str(self) -> str:
        """Get command time as string."""
        return self.command_time.strftime(TIME_FORMAT)

    @property
    def default_project(self) -> str:
        # TODO: settings
        return 'MRPL'

    @property
    def shortcuts(self) -> dict:
        # TODO: settings
        return {
            'st': ('RND-8', '[STANDUP]'),
            'help': ('RND-4', None),
        }


def main():
    """Run application."""
    WWork().run()


if __name__ == '__main__':
    main()
