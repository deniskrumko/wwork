import locale
import sys
from datetime import datetime

from colors import yellow, red, green
from entries import Commands, Entry
from exceptions import CommandNotFound, FileDoesNotExist
from files import WorkLog
from messages import messages
from settings import user_settings
from utils import (
    __empty__,
    __unknown__,
    register_command,
    worklog_required,
    yes_no_input,
)

DATE_FORMAT = '%d-%m-%Y'
TIME_FORMAT = '%H:%M'
DATE_TIME_FORMAT = '%d %B %Y, %H:%M'


class WWork:
    """Main class for wwork CLI."""

    def __init__(self):
        """Initialize class instance."""
        self.args = sys.argv[1:]
        self.now = datetime.now()
        self.__worklog = None

    def execute_command(self):
        if self.args:
            command = self.args[0]
            if command not in register_command.registry:
                command = __unknown__
        else:
            command = __empty__

        method_name = register_command.registry.get(command)
        if not method_name:
            raise CommandNotFound(command)

        return getattr(self, method_name)()

    # Commands
    # ========================================================================

    @register_command('start')
    def start(self) -> WorkLog:
        """Start new work day."""
        log = WorkLog.objects.create(date=self.current_date)
        entry = Entry(command=Commands.START, time=self.current_time)
        return log.add_and_save(entry)

    @worklog_required
    @register_command(__unknown__)
    def log(self, task: str = None, log: str = None) -> WorkLog:
        """Log event to file."""
        task = task or self.extract_task()
        log = log or self.extract_log()
        entry = Entry(
            command=Commands.WORK,
            time=self.get_time_shift(),
            task=task,
            log=log,
        )
        return self.worklog.add_and_save(entry)

    @worklog_required
    @register_command(__empty__)
    def show(self):
        """Show current day progress."""
        print('\n' + self.local_current_time * yellow + '\n')

        for entry in self.worklog.entries:
            entry.pretty_print(task_length=self.worklog.max_task_length)

    @worklog_required
    @register_command('edit', 'e')
    def edit(self):
        """Edit entries."""
        for index, entry in enumerate(self.worklog.entries, 1):
            entry.pretty_print(
                task_length=self.worklog.max_task_length,
                prefix=(f'[{index}]' + ' ' * 6)[:6] * green,
            )

        msg = messages['select_entry']
        actions = f'{"e" * yellow}dit / {"m" * green}ove / {"d" * red}elete'
        input(f'\n{msg} ({actions})\n>>> ')

    # Helper methods
    # ========================================================================

    @property
    def worklog(self) -> WorkLog:
        """Get work log for current day."""
        if not self.__worklog:
            try:
                self.__worklog = WorkLog.objects.get(date=self.current_date)
            except FileDoesNotExist:
                warning_msg = yellow * messages['file_not_found']
                if yes_no_input(warning_msg):
                    self.__worklog = self.start()

        return self.__worklog

    def extract_task(self):
        return 'MRPL-147'

    def extract_log(self):
        return 'log'

    def get_time_shift(self):
        last_entry_time = None
        for entry in self.worklog.entries:
            if not last_entry_time:
                import ipdb; ipdb.set_trace(context=8)  # FIXME: Breakpoint
                last_entry_time = entry.time
                continue

        self.current_time

    # Properties
    # ========================================================================

    @property
    def current_date(self) -> str:
        return self.now.strftime(DATE_FORMAT)

    @property
    def current_time(self) -> str:
        return self.now.strftime(TIME_FORMAT)

    @property
    def local_current_time(self) -> str:
        language = user_settings.get_language()
        locale.setlocale(locale.LC_TIME, language)
        return self.now.strftime(DATE_TIME_FORMAT)


if __name__ in ('main', '__main__'):
    WWork().execute_command()
