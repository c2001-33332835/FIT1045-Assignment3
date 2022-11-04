from abc import ABC, abstractmethod
from typing import Callable
from ColorStr import parse
import os


class UserInterface(ABC):
    clear: Callable[[], None]
    os_name: str
    
    def __init__(self):
        self.os_name = os.name
        if self.os_name in ("nt", "dos", "ce"):
            self.clear = self.__clear_screen_windows
        elif self.os_name == "posix":
            self.clear = self.__clear_screen_unix
        else:
            self.clear = self.__clear_screen_fallback

    def __clear_screen_unix(self) -> None:
        os.system("clear")

    def __clear_screen_windows(self) -> None:
        os.system("cls")

    def __clear_screen_fallback(self) -> None:
        print("\n")

    def set_cursor(self, y: int, x: int):
        try:
            assert y >= 0
            assert x >= 0
            print(f"\033[{y};{x}H")
        except AssertionError:
            raise ValueError(f"Unable to set cursor at {y}, {x}")

    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def wait_for_interact(self) -> any:
        pass

class SimpleMenuUserInterface(UserInterface):
    options: dict[int, str]
    title: str | None
    description: str | None
    color: str
    allow_undo: bool
    input_err: str | None
    undo_prompt: str

    def __init__(self, options: dict[int, str],
                title: str | None = None, description: str | None = None,
                color: str = "C", allow_undo: bool = True,
                undo_prompt: str = "(Press Ctrl-C to undo previous step)") -> None:
        super().__init__()
        self.options = options
        self.title = title
        self.description = description
        self.color = color
        self.allow_undo = allow_undo
        self.input_err = None
        self.undo_prompt = undo_prompt

    def display(self) -> None:
        self.clear()
        if self.title:
            print(parse(f"§4§{self.color}{self.title}§0"))
            # print("-" * len(self.title))
        if self.description:
            lines = self.description.splitlines()
            lines = [parse(f"  " + i) for i in lines]
            print("\n".join(lines))
        
        print("")
        
        keys = [str(i) for i in self.options.keys()]
        longest_key = max(len(i) for i in keys)

        print("  Please select by typing a number and hit Enter:")
        if self.allow_undo and self.undo_prompt:
            print(f"  {self.undo_prompt}")
        for i in self.options.keys():
            val = self.options[i]
            space_padding = " " * (longest_key - len(str(i)))
            print(f"  {i}{space_padding} - {val}")

        print("")

    def wait_for_interact(self) -> int | None:
        while True:
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))
            try:
                raw = input(parse(f"  §{self.color}>§0 "))
                val = int(raw)
                assert val in self.options.keys(), "You have entered an option not in the list"
                return val
            except ValueError:
                self.input_err = "You must enter a numerical number"
                self.display()
            except AssertionError as e:
                self.input_err = str(e)
                self.display()
            except KeyboardInterrupt:
                if self.allow_undo:
                    return None
                self.display()

class ProgressedMenuUserInterface(UserInterface):
    options: dict[int, str]
    progress: list[str]
    current_progress_index: int
    title: str | None
    description: str | None
    color: str
    allow_undo: bool
    input_err: str | None
    past_color: str
    future_color: str
    current_color: str
    breadcrumbs_color: str
    undo_prompt: str

    def __init__(self, options: dict[int, str],
                 progress: list[str], current_progress_index: int,
                 title: str | None = None, description: str | None = None,
                 color: str = "C", allow_undo: bool = True,
                 past_color: str = "W", future_color: str = "w", current_color: str = "G",
                 breadcrumbs_color: str = "w", undo_prompt: str = "(Press Ctrl-C to undo previous step)") -> None:
        super().__init__()
        self.options = options
        self.progress = progress
        self.current_progress_index = current_progress_index
        self.title = title
        self.description = description
        self.color = color
        self.allow_undo = allow_undo
        self.input_err = None
        self.past_color = past_color
        self.future_color = future_color
        self.current_color = current_color
        self.breadcrumbs_color = breadcrumbs_color
        self.undo_prompt = undo_prompt

    def __form_breadcrumbs(self) -> str:
        breadcrumb_elements = []
        for i in range(len(self.progress)):
            if i < self.current_progress_index:
                breadcrumb_elements.append(f"§{self.past_color}{self.progress[i]}§0")
            elif i == self.current_progress_index:
                breadcrumb_elements.append(f"§4§{self.current_color}[{self.progress[i]}]§0")
            else:
                breadcrumb_elements.append(f"§{self.future_color}{self.progress[i]}§0")

        message = f" §{self.breadcrumbs_color}->§0 ".join(breadcrumb_elements)
        return parse(message)

    def display(self) -> None:
        self.clear()

        print(self.__form_breadcrumbs())

        print("")
        if self.title:
            total_steps = len(self.progress)
            current_step = self.current_progress_index + 1
            print(parse(f"§4§{self.color}{self.title} ({current_step}/{total_steps})§0"))
        if self.description:
            lines = self.description.splitlines()
            lines = [parse(f"  " + i) for i in lines]
            print("\n".join(lines))
        
        print("")
        
        keys = [str(i) for i in self.options.keys()]
        longest_key = max(len(i) for i in keys)

        print("  Please select by typing a number and hit Enter:")
        if self.allow_undo and self.undo_prompt:
            print(f"  {self.undo_prompt}")
        for i in self.options.keys():
            val = self.options[i]
            space_padding = " " * (longest_key - len(str(i)))
            print(f"  {i}{space_padding} - {val}")

        print("")

    def wait_for_interact(self) -> int | None:
        while True:
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))
            try:
                raw = input(parse(f"  §{self.color}>§0 "))
                val = int(raw)
                assert val in self.options.keys(), "You have entered an option not in the list"
                return val
            except ValueError:
                self.input_err = "You must enter a numerical number"
                self.display()
            except AssertionError as e:
                self.input_err = str(e)
                self.display()
            except KeyboardInterrupt:
                if self.allow_undo:
                    return None
                self.display()

class ValueInputBox(UserInterface):
    title: str | None
    description: str | None
    validator: Callable[[str], tuple[bool, str]] | None
    color: str
    allow_undo: bool
    prompt: str
    undo_prompt: str

    def __init__(self, title: str, validator: Callable[[str], tuple[bool, str]] | None = None,
                 description: str | None = None, color: str = "C", allow_undo: bool = True,
                 prompt: str = "Please enter a value", undo_prompt: str = "(Press Ctrl-C to undo previous step)") -> None:
        self.title = title
        self.validator = validator
        self.description = description
        self.color = color
        self.allow_undo = allow_undo
        self.prompt = prompt
        self.undo_prompt = undo_prompt

    def display(self) -> None:
        self.clear()
        if self.title:
            print(parse(f"§4§{self.color}{self.title}§0"))
        if self.description:
            lines = self.description.splitlines()
            lines = [parse(f"  " + i) for i in lines]
            print("\n".join(lines))
        
        print("  " + self.prompt)
        if self.allow_undo and self.undo_prompt:
            print(f"  {self.undo_prompt}")

    def wait_for_interact(self) -> any:
        while True:
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))
            try:
                raw = input(parse(f"  §{self.color}>§0 "))
                valid, err_msg = self.validator(raw)
                assert valid, err_msg
                return raw
            except AssertionError as e:
                self.input_err = str(e)
                self.display()
            except KeyboardInterrupt:
                if self.allow_undo:
                    return None
                self.display()
