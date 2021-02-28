from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from colors import blue, green, red, yellow
from resources import TIME_FORMAT, Command, LogType, TaskType


@dataclass
class LogEntry:
    """Class for storaging logs."""

    command: Command
    command_time: time
    log_type: LogType
    log_message: str
    task_type: TaskType
    task_value: str

    def __sub__(self, value) -> timedelta:
        """Subtract two entries and get difference in time."""
        if not isinstance(value, LogEntry):
            raise TypeError(f'Cannot subtract ``{type(value)}`` from ``LogEntry``.')

        return (
            datetime.combine(date.min, self.command_time)
            - datetime.combine(date.min, value.command_time)
        )

    def shift_command_time(self, shift: timedelta):
        """Shift `command_time` for provided timedelta."""
        shifted_time = datetime.combine(date.min, self.command_time) + shift
        self.command_time = shifted_time.time()

    def get_printable(self, use_colors: bool = True, highligh_fields: dict = None) -> str:
        """Get printable string for entry."""
        color = None
        fields = {'time': None, 'task': None, 'msg': None}
        max_task_length = 11  # TODO: To settings
        special_commands = {Command.START: green, Command.PAUSE: yellow}

        # Get time
        fields['time'] = self.command_time.strftime(TIME_FORMAT)

        # Get task
        fields['task'] = self.task_value or '---'
        if self.command in special_commands:
            fields['task'] = self.command.name

        # Get spacing BEFORE coloring
        spacing = ' ' * (max_task_length - len(fields['task']))

        # Highlight empty task with red
        if use_colors and not highligh_fields and fields['task'] == '---':
            fields['task'] = fields['task'] * red

        # Get message
        fields['msg'] = self.log_message or ''

        # Use single fields coloring
        if highligh_fields:
            for field_name, value in fields.items():
                if field_name in highligh_fields:
                    fields[field_name] = value * highligh_fields[field_name]

        # Highlight that value is filler
        if self.log_type == LogType.FILL:
            color = blue
            fields['msg'] += ' 🔵'

        # Get result string
        result_message = f'  {fields["time"]}  {fields["task"]}{spacing}{fields["msg"]}'

        # Color whole string with one color
        color = special_commands.get(self.command, color)
        if use_colors and not highligh_fields and color:
            result_message *= color

        return result_message

    # Properties

    @property
    def colored_value(self) -> str:
        """Get colored value."""
        return self.get_printable(use_colors=True)

    @property
    def uncolored_value(self) -> str:
        """Get uncolored value."""
        return self.get_printable(use_colors=False)

    @property
    def command_time_str(self):
        """Get command time as string."""
        return self.command_time.strftime(TIME_FORMAT)
