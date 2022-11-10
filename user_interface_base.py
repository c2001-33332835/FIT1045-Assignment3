from abc import ABC, abstractmethod
from typing import Callable
from ColorStr import parse
import os


class UserInterface(ABC):
    """
    The abstract class for all user interfaces
    provides functions such as clear screen, set cursor and
    declare methods necessary for UI rendering
    """
    
    clear: Callable[[], None]
    os_name: str
    
    def __init__(self) -> None:
        """
        Determines the operating system type, 
        and assign clear function based on os
        """
        
        self.os_name = os.name

        # if os is windows based or dos based
        if self.os_name in ("nt", "dos", "ce"):
            self.clear = self.__clear_screen_windows

        # if os is unix-like (i.e., Linux and Mac and etc)
        elif self.os_name == "posix":
            self.clear = self.__clear_screen_unix

        # fallback for other system types
        else:
            self.clear = self.__clear_screen_fallback

    def __clear_screen_unix(self) -> None:
        """
        clear screen for unix like systems
        """

        os.system("clear")

    def __clear_screen_windows(self) -> None:
        """
        clear screen for windows or dos
        """
        
        os.system("cls")

    def __clear_screen_fallback(self) -> None:
        """
        fallback screen clear just prints a new line
        """

        print("\n")

    def set_cursor(self, y: int, x: int) -> None:
        """
        sets the cursor of terminal to a coordinate of x and y
        achieved by using the escape sequence
        """

        try:
            assert y >= 0
            assert x >= 0
            print(f"\033[{y};{x}H")
        except AssertionError:
            raise ValueError(f"Unable to set cursor at {y}, {x}")

    @abstractmethod
    def display(self) -> None:
        """
        To render the UI once
        """
        pass

    @abstractmethod
    def wait_for_interact(self) -> any:
        """
        To wait for user input for the UI.
        Value can be returned depending on UI type
        """

        pass

    @abstractmethod
    def execute(self) -> any:
        """
        An interface to execute the UI element in application level.
        Value can be returned depending on UI type
        """

        pass

class GeneralUserInterface(UserInterface):
    """
    Abstract class for common user interface types
    these interface usually consists of
    title, description, color, allow_undo, input_err and undo_prompt
    as their attributes
    """

    title: str | None
    description: str | None
    color: str
    allow_undo: bool
    input_err: str | None
    undo_prompt: str
    
    def __init__(self, title: str | None = None, description: str | None = None,
                 color: str = "C", allow_undo: bool = True, input_err: str | None = None,
                 undo_prompt: str = "") -> None:
        """
        initialize attributes from parameters
        """
        
        super().__init__()

        self.title = title
        self.description = description
        self.color = color
        self.allow_undo = allow_undo
        self.input_err = input_err
        self.undo_prompt = undo_prompt

class SimpleMenuUserInterface(GeneralUserInterface):
    """
    Abstract class for simple menu user interface.
    This user interface allow a list of options to be defined,
    user can choose from the options
    """
    
    options: dict[int, str]

    def __init__(self, options: dict[int, str],
                title: str | None = None, description: str | None = None,
                color: str = "C", allow_undo: bool = True,
                undo_prompt: str = "(Press Ctrl-C to undo previous step)") -> None:
        """
        initialize attributes from parameters
        """

        super().__init__(title=title, description=description,
                         color=color, allow_undo=allow_undo,
                         input_err=None, undo_prompt=undo_prompt)

        self.options = options

    def display(self) -> None:
        """
        Clear screen and display the UI
        """

        self.clear()

        # print title
        if self.title:
            print(parse(f"§4§{self.color}{self.title}§0"))

        # print title
        if self.description:
            lines = self.description.splitlines()
            lines = [parse(f"  " + i) for i in lines]
            print("\n".join(lines))
        
        print("")
        

        # print prompt and undo_prompt
        print("  Please select by typing a number and hit Enter:")
        if self.allow_undo and self.undo_prompt:
            print(f"  {self.undo_prompt}")

        # print options
        keys = [str(i) for i in self.options.keys()]
        longest_key = max(len(i) for i in keys)
        for i in self.options.keys():
            val = self.options[i]
            space_padding = " " * (longest_key - len(str(i)))
            print(f"  {i}{space_padding} - {val}")

        print("")

    def wait_for_interact(self) -> int | None:
        """
        Wait for user to enter a valid option
        returns result as int
        returns None if user cancels
        """
        
        while True:
            # print input error if applicable
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))

            try:
                # get user input
                raw = input(parse(f"  §{self.color}>§0 "))

                # parse to int
                val = int(raw)

                # assert value is valid option
                assert val in self.options.keys(), "You have entered an option not in the list"
                return val
            except ValueError:
                self.input_err = "You must enter a numerical number"
                self.display()
            except AssertionError as e:
                self.input_err = str(e)
                self.display()
            except KeyboardInterrupt:
                # if user press ctrl-c while undo is allowed, return None
                if self.allow_undo:
                    return None
                self.display()

class ProgressedMenuUserInterface(GeneralUserInterface):
    """
    Abstract class for progressed menu user interface.
    This user interface allow a list of options to be defined,
    user can choose from the options.
    This is suitable for wizard kind of UI,
    it prints a breadcrumb like progress bar at the top
    """
    
    options: dict[int, str]
    progress: list[str]
    current_progress_index: int
    past_color: str
    future_color: str
    current_color: str
    breadcrumbs_color: str

    def __init__(self, options: dict[int, str],
                 progress: list[str], current_progress_index: int,
                 title: str | None = None, description: str | None = None,
                 color: str = "C", allow_undo: bool = True,
                 past_color: str = "W", future_color: str = "w", current_color: str = "G",
                 breadcrumbs_color: str = "w", undo_prompt: str = "(Press Ctrl-C to undo previous step)") -> None:
        """
        initialize attributes from parameters
        """

        super().__init__(title=title, description=description,
                         color=color, allow_undo=allow_undo,
                         input_err=None, undo_prompt=undo_prompt)

        self.options = options
        self.progress = progress
        self.current_progress_index = current_progress_index
        self.past_color = past_color
        self.future_color = future_color
        self.current_color = current_color
        self.breadcrumbs_color = breadcrumbs_color

    def __form_breadcrumbs(self) -> str:
        """
        Form the breadcrumb styled progress bar
        and return as string
        """
        
        breadcrumb_elements = []
        for i in range(len(self.progress)):

            # style for past elements
            if i < self.current_progress_index:
                breadcrumb_elements.append(f"§{self.past_color} {self.progress[i]} §0")

            # style for current elements
            elif i == self.current_progress_index:
                breadcrumb_elements.append(f"§4§{self.current_color}[{self.progress[i]}]§0")

            # style for future elements
            else:
                breadcrumb_elements.append(f"§{self.future_color} {self.progress[i]} §0")

        message = f" §{self.breadcrumbs_color}->§0 ".join(breadcrumb_elements)
        return parse(message)

    def display(self) -> None:
        """
        Clear screen and display the UI
        """

        self.clear()

        # print the progress bar
        print(self.__form_breadcrumbs())

        # print title
        print("")
        if self.title:
            total_steps = len(self.progress)
            current_step = self.current_progress_index + 1
            print(parse(f"§4§{self.color}{self.title} ({current_step}/{total_steps})§0"))

        # print description
        if self.description:
            lines = self.description.splitlines()
            lines = [parse(f"  " + i) for i in lines]
            print("\n".join(lines))
        
        print("")
        
        # print prompt and undo_prompt
        print("  Please select by typing a number and hit Enter:")
        if self.allow_undo and self.undo_prompt:
            print(f"  {self.undo_prompt}")

        # print options
        keys = [str(i) for i in self.options.keys()]
        longest_key = max(len(i) for i in keys)
        for i in self.options.keys():
            val = self.options[i]
            space_padding = " " * (longest_key - len(str(i)))
            print(f"  {i}{space_padding} - {val}")

        print("")

    def wait_for_interact(self) -> int | None:
        """
        Wait for user to enter a valid option
        returns result as int
        returns None if user cancels
        """
        
        while True:
            # print input error if applicable
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))

            try:
                # get user input
                raw = input(parse(f"  §{self.color}>§0 "))

                # parse into integer
                val = int(raw)

                # assert value is valid option
                assert val in self.options.keys(), "You have entered an option not in the list"

                return val
            except ValueError:
                self.input_err = "You must enter a numerical number"
                self.display()
            except AssertionError as e:
                self.input_err = str(e)
                self.display()
            except KeyboardInterrupt:
                # if user press ctrl-c while undo is allowed, return None
                if self.allow_undo:
                    return None
                self.display()

class ValueInputBox(GeneralUserInterface):
    """
    Abstract class for a input box.
    user can enter plain text as input using this UI.
    A validator function can be specified to validate the value
    before returning
    """

    validator: Callable[[str], tuple[bool, str]] | None
    prompt: str

    def __init__(self, title: str, validator: Callable[[str], tuple[bool, str]] | None = None,
                 description: str | None = None, color: str = "C", allow_undo: bool = True,
                 prompt: str = "Please enter a value", undo_prompt: str = "(Press Ctrl-C to undo previous step)") -> None:
        """
        initialize attributes from parameters
        """

        super().__init__(title=title, description=description,
                         color=color, allow_undo=allow_undo,
                         input_err=None, undo_prompt=undo_prompt)

        self.validator = validator
        self.prompt = prompt

    def display(self) -> None:
        """
        Clear screen and display the UI
        """

        self.clear()

        # print title
        if self.title:
            print(parse(f"§4§{self.color}{self.title}§0"))

        # print description
        if self.description:
            lines = self.description.splitlines()
            lines = [parse(f"  " + i) for i in lines]
            print("\n".join(lines))
        
        # print prompt and undo_prompt
        print("  " + self.prompt)
        if self.allow_undo and self.undo_prompt:
            print(f"  {self.undo_prompt}")

    def wait_for_interact(self) -> str | None:
        """
        Wait for user to enter a valid option
        returns result as string
        returns None if user cancels
        """

        while True:
            # print input error if applicable
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))

            try:
                # get user input
                raw = input(parse(f"  §{self.color}>§0 "))

                # validate user input using validator if applicable
                if self.validator:
                    valid, err_msg = self.validator(raw)
                    assert valid, err_msg

                return raw

            except AssertionError as e:
                self.input_err = str(e)
                self.display()

            except KeyboardInterrupt:
                # if user press ctrl-c while undo is allowed, return None
                if self.allow_undo:
                    return None
                self.display()

    def execute(self) -> None:
        """
        Execute the UI element.
        """
        self.display()
        return self.wait_for_interact()

class MessageBox(GeneralUserInterface):
    """
    Abstract class for a message box.
    a list of options, one option or none can be defined.
    """

    options: list[str] | str
    default: int
    hide_options: bool
    
    def __init__(self, title: str, description: str, options: list[str] | str, 
                 color: str = "C", default: int = 0, hide_options: bool = False) -> None:
        """
        initialize attributes from parameters
        """

        super().__init__(title=title, description=description,
                         color=color, allow_undo=True,
                         input_err=None, undo_prompt="")

        self.options = options
        self.default = default
        self.hide_options = hide_options

    def display(self) -> None:
        """
        Clear screen and display the UI
        """
        
        self.clear()

        # print title and description
        print(parse(f"§4§{self.color}{self.title}§0"))
        description_lines = self.description.splitlines()
        description = "\n".join("  " + i for i in description_lines)
        print(description)
        print("")

        # if hide_options is true, dont print anything else and return
        if self.hide_options:
            return
            
        # if a list is defined, display those list
        if type(self.options) == list:
            print("  Please type a number and hit enter.")
            for i in range(len(self.options)):
                print(f"  {i+1} - {self.options[i]}")

        # if one option is defined, display that one option
        if type(self.options) == str:
            print(parse(f"  §{self.color}[§4 {self.options} (Press Enter)§0§{self.color}]§0"))

    def wait_for_interact(self) -> int | None:
        """
        Wait for user to enter a valid option
        returns result as int
        returns None if user cancels
        """
        
        # if only one option is defined, listen for enter
        if type(self.options) == str:
            try:
                input()
                return 1
            except KeyboardInterrupt:
                return None

        # if a list is defined, listen for valid input
        while True:
            if self.input_err:
                print(parse(f"  §R{self.input_err}§0"))
            try:
                raw = input(parse(f"  §{self.color}>§0 "))

                # if no option is provided, assume default
                if not raw.strip():
                    return self.default

                # parse to integer
                val = int(raw)

                # check value is valid option
                assert val > 0, "You have entered an option not in the list"
                assert val <= len(self.options), "You have entered an option not in the list"
                return val
            except ValueError:
                self.input_err = "You must enter a numerical number"
                self.display()
            except AssertionError as e:
                self.input_err = str(e)
                self.display()
            except KeyboardInterrupt:
                # if user press ctrl-c, return None
                return None
        
    def execute(self) -> int:
        """
        Execute the UI element.
        """
        
        self.display()
        return self.wait_for_interact()