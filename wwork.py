import config
import os
from datetime import datetime, timedelta
from pathlib import Path

from clint.textui import colored, indent, puts

from libs import app


class WWorkApp(app.Application):
    STORAGE_RELATIVE_PATH = '/storage/'
    PREVIOUS_DAY = ('prev', 'past', 'y')
    PREPREVIOUS_DAY = ('yy',)
    COLORS = {
        'blu': ('\x1b[34m\x1b[22m', '\x1b[39m\x1b[22m'),
        'gre': ('\x1b[32m\x1b[22m', '\x1b[39m\x1b[22m'),
        'red': ('\x1b[31m\x1b[22m', '\x1b[39m\x1b[22m'),
        'yel': ('\x1b[33m\x1b[22m', '\x1b[39m\x1b[22m'),
    }

    def __init__(self, *args, **kwargs):
        """Initialization method."""
        super().__init__(*args, **kwargs)
        self._previous = any([
            self.arguments[0] in self.PREVIOUS_DAY,
            self.arguments[-1] in self.PREVIOUS_DAY,
        ])
        self._preprevious = any([
            self.arguments[0] in self.PREPREVIOUS_DAY,
            self.arguments[-1] in self.PREPREVIOUS_DAY,
        ])
        self._file = None

    @app.register('start')
    def start(self):
        """Command to start a new perfect work day!

        Example:
            ww start       # creates file for current day
            ww start prev  # creates file for previous day

        """
        if self.file_exists():
            return self.print(
                'Day already started! <gre>Go to work now ;)</gre>'
            )

        result = self.write('s', 'Start a new work day!', new_file=True)

        self.print(result)
        self.print(f'File <gre>"{self.file_path}"</gre> has been created!')

    @app.register('end')
    def end(self):
        """Command to end this hard work day!

        Example:
            ww end

        """
        assert self.file
        assert self.not_on_pause

        result = self.write('e', 'End of the day!', new_file=False)

        # Show result
        self.print(result)
        self.print('<gre>Day finally ended!</gre>')

    @app.register('delete', 'del')
    def delete_file(self):
        """Command to delete file.

        Example:
            ww del 2018-12-31
            ww delete 2018-12-31
            ww delete 2018-12-31.txt

        """
        if not self.extra:
            self.exit('Specify date in format like 2018-12-31')

        file_date = self.extra[0].rstrip('.txt')
        file_path = self.storage_dir + file_date + '.txt'

        if not self.file_exists(path=file_path):
            self.exit(f'Error! File "{file_path}" does not exist!')

        try:
            os.remove(file_path)
        except Exception:
            self.exit(f'Error on removing file {file_path}')

        self.print(f'File "{file_path}" was <gre>successfully deleted</gre>!')

    @app.register('pause', 'p')
    def pause(self):
        """Command to end this hard work day!

        Example:
            ww end

        """
        # Enable pause
        if self.last_command != 'p':
            self.write('p', 'Pause init ╮')
            self.print('Pause is <gre>enabled</gre>. Go REST. Or EAT.')

        # Disable pause
        else:
            self.write('u', 'Pause stop ╯')
            self.print('Pause is <red>disabled</red>. Go WORK.')

            duration = self.get_duration(start=-2, end=-1)
            self.print(f'Pause duration is <yel>{duration}</yel>')

    @app.register(default=True)
    def log_task(self):
        """Command to log your work (default command).

        Example:
            ww JIRA-1012 I did something interesting
            ww 1024 Jira code can be skipped
            ww Standup

        """
        assert self.file
        assert self.not_on_pause

        if self.command.split('-')[-1].isdigit():
            msg = ' '.join(self.extra)
            string = f'{config.DEFAULT_JIRA_CODE}-{self.command}: {msg}'
        else:
            msg = ' '.join(self.extra)
            string = f'{config.MAIN_TASK_CODE}: {self.command} {msg}'

        if not string.endswith(('.', '!', '?', ')', '(')):
            string = string.strip() + '.'

        result = self.write('w', string)

        self.print(result)
        self.print('<gre>Task is logged ✓</gre>', pre='')

    @app.register(*(PREVIOUS_DAY+PREPREVIOUS_DAY), empty_args=True)
    def main_screen(self):
        """Command to show main app screen.

        Example:
            ww       # main screen for current day
            ww prev  # main screen for previous day

        """
        assert self.file

        os.system('clear')

        colors_map = {
            's': colored.green,
            'u': colored.yellow,
            'p': colored.yellow,
            'e': colored.red,
        }

        with indent(2):

            if self._previous or self._preprevious:
                self.print(f'<blu>FILE: {self.file_path}</blu>')

            # Show main table
            self.print('<blu>TIME    TASK NAME</blu>', post='\n')

            for line in self.file:
                color = colors_map.get(line[0])
                msg = (color(line[2:7]) if color else line[2:7]) + line[7:]
                self.print(msg, pre='', newline=False)

    @app.register('fc', 'from')
    def from_commit(self):
        commit_msg = os.popen('git log -1').read()

        if not commit_msg:
            self.exit('This is not a git repository')

        messages = commit_msg.split('\n')[4:]
        message = messages[0].lstrip() + '.'  # one liner usually has no dot
        self.print(message)

        self.write('w', message)

    @app.register('e', 'edit')
    def edit(self):
        editor = 'vim'
        os.system(' '.join([editor, self.file_path]))

    # Helper methods
    # ========================================================================

    def print(self, msg, color=None, pre='\n', post='', newline=True):
        """Print message in console."""
        msg = pre + msg + post

        if color:
            msg = color(msg)
        else:
            for name, data in self.COLORS.items():
                msg = msg.replace(f'<{name}>', data[0])
                msg = msg.replace(f'</{name}>', data[1])

        puts(msg, newline)

    def exit(self, msg):
        self.print(msg, color=colored.red, pre='\n', post='\n')
        exit()

    def file_exists(self, path=None):
        return Path(path or self.file_path).is_file()

    @property
    def storage_dir(self):
        return os.path.dirname(__file__) + self.STORAGE_RELATIVE_PATH

    @property
    def file_path(self):
        delta = -1 if self._previous else None
        delta = -2 if self._preprevious else delta
        return self.storage_dir + self.get_date(delta) + '.txt'

    @property
    def file(self):
        if not self._file:
            self._file = self.read_file()

        return self._file

    @property
    def last_command(self):
        return self.file[-1][0]

    @property
    def not_on_pause(self):
        if self.last_command == 'p':
            self.exit('Looks like you forgot to unpause?')

        return True

    def get_date(self, delta=None):
        date = datetime.now()

        if delta is not None:
            date += timedelta(days=delta)

        return date.strftime(config.DATE_FORMAT)

    def get_current_time(self):
        """Get current time in HH:MM format."""
        return datetime.now().strftime(config.TIME_FORMAT)

    def get_duration(self, start, end, as_string=True):
        start_str = self.file[start][2:7]
        stop_str = self.file[end][2:7]

        start_time = datetime.strptime(start_str, config.TIME_FORMAT)
        stop_time = datetime.strptime(stop_str, config.TIME_FORMAT)

        duration = (stop_time - start_time).seconds
        duration_str = str(timedelta(seconds=duration))[:-3]

        return f'{duration_str} ({start_str} - {stop_str})' \
            if as_string else duration

    def write(self, code, msg, new_file=False):
        """Write line with time and message to file."""
        task_time = self.get_current_time()
        line = '{} {}   {}\n'.format(code, task_time, msg)
        write_mode = 'w' if new_file else 'a'
        try:
            with open(self.file_path, write_mode) as f:
                f.writelines(line)
        except IOError:
            self.exit('Can not write the file: ' + self.file_path)

        return line[2:]

    def read_file(self):
        res = None
        try:
            with open(self.file_path, 'r') as f:
                res = f.readlines()
        except IOError:
            self.exit('Can not read file: ' + self.file_path)

        return res


if __name__ == '__main__':
    WWorkApp().run()
