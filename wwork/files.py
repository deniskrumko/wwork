import shelve
from pathlib import Path

import exceptions
from entries import Entry
from utils import classproperty, debugger

BASE_PATH = Path(__file__).parent.absolute()
STORAGE_PATH = BASE_PATH.joinpath('storage')

Path(STORAGE_PATH).mkdir(exist_ok=True)


class FileManager:
    """Class for managing ``File`` objects."""

    def __init__(self, folder, model):
        """Initialize class instance."""
        self.model = model
        self.base_path = STORAGE_PATH.joinpath(folder or '')
        Path(self.base_path).mkdir(exist_ok=True)

    def get(self, *args, **kwargs):
        """Get model instance."""
        file_path = self.get_file_path(*args, **kwargs)
        if not self.check_file_exists(file_path):
            raise exceptions.FileDoesNotExist(file_path)

        return self.model(file_path=file_path)

    def create(self, *args, **kwargs):
        """Create model instance."""
        file_path = self.get_file_path(*args, **kwargs)
        if self.check_file_exists(file_path):
            raise exceptions.FileAlreadyExists(file_path)

        return self.model(file_path=file_path)

    def check_file_exists(self, path: Path) -> bool:
        """Check if file exists or not."""
        return path.is_file()

    def get_file_path(self, *args, **kwargs):
        """Get result file path."""
        filename = self.model.get_file_name(*args, **kwargs)
        return self.base_path.joinpath(filename)


class File:
    folder = None

    def __init__(self, file_path: Path):
        """Initialize class instance."""
        self.file_path = file_path
        self._data = {}
        self.read()

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.file_path.name}>'

    @debugger
    def read(self):
        with shelve.open(self.file_path._str) as db:
            for key, value in db.items():
                self._data[key] = value

    @debugger
    def save(self):
        with shelve.open(self.file_path._str) as db:
            for key, value in self._data.items():
                db[key] = value

    @classproperty
    def objects(cls):
        return FileManager(cls.folder, cls)

    @classmethod
    def get_file_name(cls, *args, **kwargs):
        raise NotImplementedError


class WorkLog(File):
    folder = 'logs'

    def __init__(self, *args, **kwargs):
        """Initialize class instance."""
        super().__init__(*args, **kwargs)
        self._data.setdefault('entries', [])
        self.max_task_length = len(max(
            self._data['entries'],
            key=lambda x: len(x['task'] or '')
        )['task'] or '')

    @property
    def entries(self):
        """Get log entries."""
        return [
            Entry.from_json(value)
            for value in self._data['entries']
        ]

    @classmethod
    def get_file_name(cls, date):
        """Get file name."""
        return f'{date}.ww'

    def add(self, entry: Entry):
        """Add entry to log."""
        if not isinstance(entry, Entry):
            raise ValueError('entry must be ``Entry`` instance')

        self._data['entries'].append(entry.to_json())

    def add_and_save(self, entry: Entry):
        """Add entry to log and save it."""
        self.add(entry=entry)
        self.save()


class Settings(File):

    @classmethod
    def get_file_name(cls):
        """Get file name."""
        return 'settings.ww'

    def get_language(self):
        return self._data['language']

    def set_language(self, language):
        self._data['language'] = language
