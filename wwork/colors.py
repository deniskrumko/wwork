class Color:
    """Class for color storage."""

    def __init__(self, color_number):
        """Initialize class instance."""
        self.__color_number = color_number

    def __call__(self, value):
        """Call color.

        For example:
            Color(91)('message')

        """
        return self.__colored_value(value)

    def __mul__(self, value):
        """Multiply color color.

        For example:
            Color(91) * 'message'

        """
        return self.__colored_value(value)

    def __rmul__(self, value):
        """Right Multiply color color.

        For example:
            'message' * Color(91)

        """
        return self.__colored_value(value)

    def print(self, value):
        """Print colored value.

        For example:
            Color(91).print('message')

        """
        print(self.__colored_value(value))

    def __colored_value(self, value) -> str:
        """Get colored value."""
        if not self.__color_number:
            return value

        return f'\033[{self.__color_number}m{value}\033[00m'


# Available colors

no_color = Color(None)
red = Color(91)
green = Color(92)
yellow = Color(93)
blue = Color(94)