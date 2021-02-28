import os
import pickle
from datetime import timedelta
from pathlib import Path
from time import time
from typing import Union

from entries import LogEntry
from resources import TIME_FORMAT


class BaseFile:
    """Base class for files."""

    root_dir = Path.home() / '.wwork'
    extension = 'ww'

    def __init__(self, file_name: str):
        """Initialize class instance."""
        self.root_dir.mkdir(exist_ok=True)

        self._path = self.root_dir / f'{file_name}.{self.extension}'
        self._data: Union[list, dict] = None

    @property
    def exists(self) -> bool:
        """Check if file exists or not."""
        return self._path.is_file()

    @property
    def data(self) -> Union[list, dict]:
        """Get file data."""
        if self._data is None:
            self.load()  # Load file only once
        return self._data

    def load(self):
        """Read file and get data."""
        if self.exists:
            with open(self._path, 'rb') as f:
                self._data = pickle.loads(f.read())
        else:
            self._data = self.create_default()

    def save(self):
        """Save data back to file."""
        if not self.exists:
            self._path.touch()

        with open(self._path, 'wb+') as f:
            f.write(pickle.dumps(self.data))

    def terminate(self):
        """Delete file itself."""
        if self.exists:
            os.remove(self._path)

    def create_default(self) -> Union[list, dict]:
        """Create default `data` value."""
        raise NotImplementedError


class LogFile(BaseFile):
    """File with log entries."""

    default_type = dict

    def create_default(self) -> dict:
        """Create default log file data."""
        return {
            'logs': [],
            'report': [],
        }

    @property
    def logs(self):
        return self.data['logs']

    @property
    def report(self):
        return self.data['report']

    def add_entry(self, **kwargs):
        """Add new log entry."""
        new_entry = LogEntry(**kwargs)
        self.logs.append(new_entry)
        return new_entry

    @property
    def last_time(self) -> time:
        """Get last log time."""
        return self.logs[-1].command_time if self.logs else None

    @property
    def last_time_str(self) -> str:
        """Get last log time (as string)."""
        return self.last_time.strftime(TIME_FORMAT)

    @property
    def last_command_duration(self) -> int:
        """Get last command duration (in minutes)."""
        if len(self.logs) < 2:
            raise ValueError('Cannot get duration if there are less than 2 commands')

        duration: timedelta = self.logs[-1] - self.logs[-2]
        return duration.seconds // 60
