import abc
import asyncio
import importlib.util
import inspect
import os
from argparse import ArgumentParser
from typing import List, Type, Dict

from settings.config import COMMAND_DIR


class BaseCommand:
    """Необхлдимо задать command"""
    command: str

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Тут пишутся все передаваемые аргументы"""
        pass

    @abc.abstractmethod
    async def handle(self, *args, **kwargs) -> None:
        raise NotImplementedError("Subclasses must implement handle method")


class CommandControl:
    _classes: List[Type[BaseCommand]]
    _command: Dict[str, BaseCommand] = {}
    _parser: ArgumentParser
    _cmd: str

    def __init__(self, parser: ArgumentParser, **kwargs):
        self._parser = parser
        self._classes = self._get_class_in_folder()
        self._command = {cls.command: cls() for cls in self._classes}

        self._init_subparsers()

    def _get_class_in_folder(self) -> List[Type[BaseCommand]]:
        """Берет классы из папки BASE_DIR/tinkoff_app/commands"""
        _classes = []

        for filename in os.listdir(COMMAND_DIR):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                module_path = os.path.join(COMMAND_DIR, filename)

                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Ensure the class is defined in the module, not imported, and is a subclass of base_class
                    if obj.__module__ == module_name and issubclass(obj, BaseCommand) and obj is not BaseCommand:
                        _classes.append(obj)

        return _classes

    def parse_command(self):
        """выполняет команду в найденных классах команд
        Возвращает Fase если команда не задана"""
        args = self._parser.parse_args()
        self._cmd = args.command
        if self._cmd is None:
            return False
        if self._cmd not in self._command.keys():
            self._parser.print_help()
            raise ValueError('Command not found')
        self._make_command(**vars(args))
        return True

    def _init_subparsers(self):
        """Инициализирует аргументы"""
        subparsers = self._parser.add_subparsers(dest='command')
        for cmd, cls in self._command.items():
            parser = subparsers.add_parser(cmd)
            cls.add_arguments(parser=parser)

    def _make_command(self, *args, **kwargs):
        asyncio.run(self._command[self._cmd].handle(args=args, kwargs=kwargs))
