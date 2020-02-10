LANGUAGE_RU = 'ru_RU'
LANGUAGE_EN = 'en_US'
LANGUAGES = (
    (LANGUAGE_RU, 'Русский 🇷🇺'),
    (LANGUAGE_EN, 'English 🇬🇧'),
)


class Message:
    """Class for human readable messages."""

    def __init__(self, en: str, ru: str):
        """Initialize class instance."""
        self.__data = {
            LANGUAGE_EN: en,
            LANGUAGE_RU: ru,
        }

    def __str__(self) -> str:
        """String representation."""
        return self.__msg

    @property
    def __msg(self) -> str:
        """Get translated message."""
        from settings import user_settings

        try:
            language = user_settings.get_language()
            return self.__data[language]
        except KeyError:
            raise ValueError('No translation to requested language')

    # Public methods

    def format(self, *args, **kwargs) -> str:
        """Format string."""
        return self.__msg.format(*args, **kwargs)

    def get(self, language):
        """Get message with specific language."""
        return self.__data[language]

    @property
    def all_variants(self):
        """Get message with all variants."""
        return ' / '.join(self.get(language[0]) for language in LANGUAGES)


messages = {
    'file_not_found': Message(
        en='File not found. Create new one and start work day?',
        ru='Файл не найден. Создать новый файл и начать рабочий день?'
    ),
    'start_work': Message(
        en='Start of the work day',
        ru='Начало рабочего дня',
    ),
    'pause': Message(
        en='Pause start',
        ru='Начало перерыва',
    ),
    'pause_end': Message(
        en='Pause end',
        ru='Конец перерыва',
    ),
    'base_folder_not_found': Message(
        en='Main directory was not found: {}',
        ru='Корневой каталог не найден: {}',
    ),
    'select_language': Message(
        en='Select language',
        ru='Выберите язык',
    ),
    'wrong_variant': Message(
        en='Wrong variant',
        ru='Неправильный вариант',
    ),
    'select_entry': Message(
        en='Select entry and action',
        ru='Выберите запись и действие',
    ),
}
