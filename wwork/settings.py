from colors import red
from exceptions import FileDoesNotExist
from files import Settings
from messages import LANGUAGES, messages

user_settings = None


def init_settings():
    """Initialize user settings."""
    global user_settings

    try:
        user_settings = Settings.objects.get()
    except FileDoesNotExist:
        print(f'\n{messages["select_language"].all_variants}\n')

        for index, language in enumerate(LANGUAGES, 1):
            print(f'{index}. {language[1]}')

        try:
            result = int(input('>>> '))
            if not (0 < result <= len(LANGUAGES)):
                raise ValueError
        except ValueError:
            exit(red * messages['wrong_variant'].all_variants)

        user_settings = Settings.objects.create()
        user_settings.set_language(LANGUAGES[result - 1][0])
        user_settings.save()
