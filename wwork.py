import config
import os
from datetime import datetime, timedelta
from pathlib import Path

from clint.textui import colored, indent, puts

from libs import app


class WWorkApp(app.Application):
    STORAGE_RELATIVE_PATH = '/storage/'
    COLORS = {
        'blu': ('\x1b[34m\x1b[22m', '\x1b[39m\x1b[22m'),
        'gre': ('\x1b[32m\x1b[22m', '\x1b[39m\x1b[22m'),
        'red': ('\x1b[31m\x1b[22m', '\x1b[39m\x1b[22m'),
        'yel': ('\x1b[33m\x1b[22m', '\x1b[39m\x1b[22m'),
    }

    def __init__(self, *args, **kwargs):
        """Initialization method."""
        super().__init__(*args, **kwargs)
        self._file = None
        self.previous = None

        for flag in self.flags.all:
            if flag and flag.startswith('-y'):
                self.previous = -flag.count('y')

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

    @app.register('time')
    def count_time(self):
        if len(self.extra) != 1:
            self.exit('Incorrect command format')

        value = float(self.extra[0])
        remaining = 8.0 - value
        self.print(
            f'{value} is {int(value // 1)} hours and '
            f'{int(value % 1 * 60)} minutes'
        )
        self.print(
            f'Remaining time is {int(remaining // 1)} hours and '
            f'{int(remaining % 1 * 60)} minutes'
        )

    @app.register(default=True)
    def log_task(self, task=None, msg=None):
        """Command to log your work (default command).

        Example:
            ww JIRA-1012 I did something interesting
            ww 1024 Jira code can be skipped
            ww Standup

        """
        if len(set(self.command)) == 1:
            self.exit('Probably, you won\'t log task with one symbol...')

        assert self.file
        assert self.not_on_pause

        change_time = 0

        for word in tuple(self.extra):
            if word.startswith('+'):
                change_time = int(word[1:])
                self.extra.remove(word)

        if task:
            string = f'{task}: '
        elif self.command.split('-')[-1].isdigit():
            string = f'{config.DEFAULT_JIRA_CODE}-{self.command}: '
        elif self.command.split('.')[-1].isdigit():
            a, b = self.command.split('.')
            string = f'{a}-{b}: '
        else:
            string = f'{config.MAIN_TASK_CODE}: {self.command} '

        msg = msg or ' '.join(self.extra)

        string += msg

        if not string.endswith(('.', '!', '?', ')', '(')):
            string = string.strip() + '.'

        result = self.write('w', string, change_time=change_time)

        self.print(result)
        self.print('<gre>Task is logged ✓</gre>', pre='')

    @app.register(empty_args=True)
    def main_screen(self):
        """Command to show main app screen.

        Example:
            ww       # main screen for current day

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
            if self.previous is not None:
                formatted = self.date.strftime('%B %d, %A')
                self.print(f'<yel>DATE: {formatted}</yel>')
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

    @app.register('st', 'stand', 'standup')
    def standup(self):
        self.log_task(task='RND-4', msg='[STANDUP]')

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
        return self.storage_dir + self.get_date(delta=self.previous) + '.txt'

    @property
    def date(self):
        return self.get_date(delta=self.previous, as_string=False)

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

    def get_date(self, delta=None, as_string=True):
        date = datetime.now()

        if delta is not None:
            date += timedelta(days=delta)

        return date.strftime(config.DATE_FORMAT) if as_string else date

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

    def write(self, code, msg, new_file=False, change_time=False):
        """Write line with time and message to file."""
        if change_time:
            last_time_str = self.file[-1][2:7]
            last_time = datetime.strptime(last_time_str, config.TIME_FORMAT)
            last_time += timedelta(minutes=change_time)
            task_time = last_time.strftime(config.TIME_FORMAT)
            self.print(
                f'Modified time +{change_time} minutes: {task_time}',
                color=colored.yellow, pre='\n'
            )
        else:
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
