from __future__ import annotations

import sys

try:
    # try to import with ColorStr module
    from user_interface_base import *
except ModuleNotFoundError as e:
    # if module not found, prompt the user to install
    print("Some modules are not found, please install all modules stated in the requirements.txt")
    print("Maybe execute pip install -r requirements.txt")
    sys.exit(1)

# display message first
MessageBox("Navigation System - Loading", "The Navigation System is now initializing. \nPlease hold on", "",
            hide_options=True).display()

# some of these imports takes some time to process, it is better to show a message before importing them.
from city_country_csv_reader import create_cities_countries_from_CSV
from vehicles import Vehicle, CrappyCrepeCar, DiplomacyDonutDinghy, TeleportingTarteTrolley
from path_finding import find_shortest_path
from locations import City, Country
from map_plotting import plot_trip
from trip import Trip
from time import sleep
from math import inf
import os

class NavigationSystem:
    """
    The model class for the Navigation system, singleton.
    holds the information about the vehicles and trips the system has
    the instance static attribute holds the instance of this class
    use get_instance() to get an universal instance of this class
    """
    vehicles: list[Vehicle]
    trips: list[Trip]
    instance: NavigationSystem = None
    default_source_file: str = "worldcities_truncated.csv"

    def get_instance() -> NavigationSystem:
        """
        To get the static instance of this class,
        initialize one if there is none.
        """

        if not NavigationSystem.instance:
            NavigationSystem.instance = NavigationSystem()

        return NavigationSystem.instance

    def __init__(self) -> None:
        """
        Initialize the field
        Creates container for vehicles and trips (list)
        If an instance has already been created before, throw an exception.
        """
        
        if NavigationSystem.instance:
            raise Exception("An instance has already being created. Use get_instance() instead")
        
        NavigationSystem.instance = self

        self.vehicles = []
        self.trips = []

    def initialise_data(self, file_path: str | None = None) -> None:
        """
        Initializes data by reading csv.
        Takes in an optional file_path parameter to specify the file to be read
        if the file_path is None, the default file is being read
        """
        if not file_path:
            file_path = NavigationSystem.default_source_file
        create_cities_countries_from_CSV(file_path)
    
    def create_example_entities(self) -> None:
        """
        Adds example vehicles and trips to this system.
        initialise_data() has to be called before using this function
        and cities such as Tokyo, Kuala Lumpur, Melbourne, Canberra, Paris and Bern
        has to be defined in the City list.
        """

        # add example vehicles
        self.vehicles += [CrappyCrepeCar(200), DiplomacyDonutDinghy(100, 500), TeleportingTarteTrolley(3, 2000)]

        # add example trips
        australia = Country.countries["Australia"]
        japan = Country.countries["Japan"]
        malaysia = Country.countries["Malaysia"]
        switzerland = Country.countries["Switzerland"]
        france = Country.countries["France"]

        tokyo = japan.get_city("Tokyo")
        kuala_lumpur = malaysia.get_city("Kuala Lumpur")
        melbourne = australia.get_city("Melbourne")
        canberra = australia.get_city("Canberra")
        paris = france.get_city("Paris")
        bern = switzerland.get_city("Bern")

        trip1 = Trip(melbourne)
        trip1.add_next_city(kuala_lumpur)
        trip1.add_next_city(tokyo)
        self.trips.append(trip1)

        trip2 = Trip(melbourne)
        trip2.add_next_city(paris)
        trip2.add_next_city(bern)
        self.trips.append(trip2)

        trip3 = Trip(melbourne)
        trip3.add_next_city(canberra)
        trip3.add_next_city(kuala_lumpur)
        self.trips.append(trip3)

class LocationSelectionMenu(SimpleMenuUserInterface):
    """
    The UI menu for selecting a single city.
    A search box is being provided. When a city name is being entered,
    it is being matched with the city list. When multiple city is matched,
    user will be able to select one.
    """

    def __init__(self, title: str, description: str, undo_prompt: str, allow_undo: bool = True) -> None:
        """
        initialize a simple menu interface.
        """

        options = {1: "[Reset Filter...]"}

        super().__init__(options, title, description=description, undo_prompt=undo_prompt)

    def validate_filter_value(raw: str) -> tuple[bool, str]:
        """
        Validate search box value, where the search has to be 3 chars or above when trimmed.
        Returns a tuple of the result in boolean and the error message in string if applicable.
        """
        
        try:
            trimmed = raw.strip()
            assert trimmed, "Filter value cannot be empty"
            assert len(trimmed) >= 3, "Filter value has to be 3 characters or above"
            return True, ""
        except AssertionError as e:
            return False, str(e)

    def get_filter(self, err_msg: str | None = None) -> str:
        """
        Defines a search box and search for city.
        The chars user entered will then be returned as string.
        takes in an error message, which will be displayed together with the search box
        """

        search_box =  ValueInputBox("Search City", LocationSelectionMenu.validate_filter_value,
                             prompt="Please enter a city name to search the city",
                             undo_prompt="(Press Ctrl-C to go back)")
        
        search_box.input_err = err_msg
        return search_box.execute()

    def execute(self) -> City | None:
        """
        Executes this UI element. Returns a city the user selected.
        None is returned if the user choose to cancel.
        """
        
        filter_empty_err = None
        while True:
            city_filter = self.get_filter(err_msg = filter_empty_err)

            # if filter is canceled, return None
            if not city_filter:
                return
            
            cities = list(City.cities.values())
            filtered = list(filter(lambda city: city_filter.lower() in str(city).lower(), cities))

            # if only one city is found, return that city
            if len(filtered) == 1:
                return filtered[0]

            # if no city is found, display the search box again and display an error message.
            if not filtered:
                filter_empty_err = f"'{city_filter}' is not found. Please check the spelling, or try another city."
                continue

            filter_empty_err = None

            # display the multiple choice of cities
            self.options = {
                1: "[Search again...]"
            }

            for i in range(len(filtered)):
                self.options[i + 2] = str(filtered[i])

            self.display()
            option = self.wait_for_interact()

            # if user selected reset filter, display search box again.
            if option == 1:
                continue

            # if the user cancels the search, return None
            if not option:
                return

            # return the city user selected
            return filtered[option - 2]

class MainMenu(SimpleMenuUserInterface):
    """
    The UI menu for the main menu.
    User can choose to manage vehicles and trips, or exit the system.
    """
    
    def __init__(self) -> None:
        """
        initialize a simple menu interface.
        """
        
        options = {
            1: "Manage Vehicles",
            2: "Manage Trips",
            3: "Exit",
        }

        description = "Welcome to the Navigation System\n"\
                    + "Please select an item from the menu to start"

        super().__init__(options, title="Navigation System - Main Menu", description=description, undo_prompt="")

    def execute(self) -> None:
        """
        Executes this UI element until exit is selected.
        """

        while True:
            # display and wait for user input
            self.display()
            option = self.wait_for_interact()

            if option in self.options.keys():
                self.input_err = None

            # open menu when corresponding option is selected
            if option == 1:
                # open vehicle menu
                ManageVehiclesMenu().execute()
                continue

            if option == 2:
                # open trip menu
                ManageTripsMenu().execute()

            # if exit or ctrl-c, exit the program
            if not option or option == 3:
                print(parse(f"\n§{self.color}Exiting. Thank you for using the Navigation System.§0\n"))
                return

class ManageVehiclesMenu(SimpleMenuUserInterface):
    """
    The UI menu for managing vehicles.
    The user will be able to add new vehicles or manage current available vehicles.
    """

    def __init__(self) -> None:
        """
        initialize a simple menu interface.
        """

        system = NavigationSystem.get_instance()
        options = {}
        options[1] = "[Add Vehicle...]"

        for i in range(len(system.vehicles)):
            options[i + 2] = str(system.vehicles[i])
        
        if len(options) > 1:
            description = "To get started, select a vehicle from the menu below,\n"\
                        + "or select 'Add Vehicle...' to add a custom vehicle"
        else:
            description = "There is no vehicles yet.\n"\
                        + "Please select 'Add Vehicle...' to add a custom vehicle"

        undo_prompt = "(Press Ctrl-C to go back to Main Menu)"

        super().__init__(options, title="Manage Vehicles", description=description, undo_prompt=undo_prompt)

    def execute(self) -> None:
        """
        Executes this UI element until back is selected using Ctrl-C.
        """

        while True:
            # Update options and display
            self.__init__()
            self.display()
            option = self.wait_for_interact()

            # if ctrl c is pressed, return
            if not option:
                return

            # if add vehicle is selected, run the add vehicle menu
            if option == 1:
                AddVehicleVehicleTypeMenu().execute()
                continue

            # or else enter vehicle details page for the specific vehicle selected by the user
            vehicle = NavigationSystem.get_instance().vehicles[option - 2]
            SpecificVehicleMenu(vehicle, option - 2).execute()

class SpecificVehicleMenu(SimpleMenuUserInterface):
    """
    The UI menu for viewing vehicles details.
    The user will be able to delete this vehicle.
    """
    
    vehicle: Vehicle
    index: int

    def __init__(self, vehicle: Vehicle, index: int) -> None:
        """
        takes in the vehicle and the index of that vehicle.
        initialize a simple menu interface and assign the parameters to attributes.
        """
        
        self.vehicle = vehicle
        self.index = index

        options = {
            1: "Delete this vehicle",
            2: "Go back"
        }

        description = f"You are now viewing: {vehicle} \n\n"\
                    + "To delete this vehicle, select 'Delete this vehicle'\n"\
                    + "select 'Go back' or Ctrl-C to go back"

        super().__init__(options, title="Manage Vehicles", description=description, undo_prompt="")

    def execute(self) -> None:
        """
        Executes this UI element until back or delete is selected.
        """

        self.display()
        option = self.wait_for_interact()

        # if delete is selected, delete the vehicle in system
        if option == 1:
            del NavigationSystem.get_instance().vehicles[self.index]

class AddVehicleVehicleTypeMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new vehicle.
    This menu belongs to a series of UI which makes up the Add vehicle wizard
    This is the first step of the wizard.
    The user will be able to choose what kind of vehicle they want.
    """
    
    options: dict[int, str] = {
        1: "CrappyCrepeCar",
        2: "DiplomacyDonutDinghy",
        3: "TeleportingTarteTrolley",
    }

    def __init__(self) -> None:
        """
        initialize a progressed menu interface.
        """

        progress = ["Select Vehicle Type", "Confirm Vehicle", "Customise Parameters"]

        description = "All vehicles in this system has to be derived from one of the 3 vehicles shown below.\n"\
                    + "Select one to see descriptions."

        undo_prompt = "(Press Ctrl-C to discard this new vehicle)"

        super().__init__(AddVehicleVehicleTypeMenu.options, progress, 0,
                         title="Create a Vehicle", description=description, undo_prompt=undo_prompt)

    def execute(self) -> None:
        """
        Executes this UI element until back is selected by ctrl c, or the next step returns true
        """

        while True:
            self.display()
            option = self.wait_for_interact()

            # if ctrl c is selected, return
            if not option:
                return
            
            # if if the next step of the wizard returned true, exit
            if AddVehicleDescriptionMenu(AddVehicleVehicleTypeMenu.options[option]).execute():
                return

class AddVehicleDescriptionMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new vehicle.
    This menu belongs to a series of UI which makes up the Add vehicle wizard
    This is the second step of the wizard.
    The user will be able to view a description
    of the vehicle they have chosen from the previous step.
    """
    
    vehicle_type: str
    
    descriptions: dict[str, str] = {
        "CrappyCrepeCar"         : "The CrappyCrepeCar is a flying car that can travel between any two cities in the world, but moves pretty slowly.",
        "DiplomacyDonutDinghy"   : "The DiplomacyDonutDinghy is a small boat which is licensed to travel on diplomatic hyperlanes. \n"\
                                 + "So it moves extra fast between capital cities. \n"\
                                 + "It can also travel between any two cities in the same country. \n"\
                                 + "However, it can only move from one country to another via their capitals.",
        "TeleportingTarteTrolley": "The TeleportingTarteTrolley is a trolley bus that can teleport between any two cities if they are close enough, \n"\
                                 + "regardless of countries. \n"\
                                 + "Because teleportation technology is still in its infancy, \n"\
                                 + "it takes time to program and execute a blink between two cities."
    }
    
    def __init__(self, vehicle_type: str) -> None:
        """
        takes in a vehicle_type as string
        initialize a progressed menu interface.
        """

        self.vehicle_type = vehicle_type

        options = {
            1: "Confirm",
            2: "Choose again",
        }

        progress = ["Select Vehicle Type", "Confirm Vehicle", "Customise Parameters"]

        undo_prompt = "(Press Ctrl-C to go back to previous step)"

        super().__init__(options, progress, 1, title="Create a Vehicle",
                         description=AddVehicleDescriptionMenu.descriptions[vehicle_type],
                         undo_prompt=undo_prompt)

    def execute(self) -> bool:
        """
        Executes this UI element.
        Returns False if back is selected.
        Returns True if this the next step returned True.
        The boolean return value is to determine if the reason of return is wizard being competed,
        or if it got discard.
        """

        while True:
            self.display()
            option = self.wait_for_interact()

            # return False if back or ctrl c
            if not option or option == 2:
                return False

            # if the next step returns true, return true 
            if AddVehicleAttributeMenu(self.vehicle_type).execute():
                return True

class AddVehicleAttributeMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new vehicle.
    This menu belongs to a series of UI which makes up the Add vehicle wizard
    This is the third step of the wizard.
    The user will be able to customize the parameters of the selected vehicle type,
    and save the vehicle to the list.
    """
    vehicle_type: str
    vehicle_parameters: dict[str, list[str]] = {
        "CrappyCrepeCar": ["speed"],
        "DiplomacyDonutDinghy": ["speed_internal", "speed_external"],
        "TeleportingTarteTrolley": ["timeout", "distance_limit"],
    }
    options: dict[str, dict[int, str]] = {
        "CrappyCrepeCar": {
            1: "Speed of this CrappyCrepeCar (km/h)"
        },
        "DiplomacyDonutDinghy": {
            1: "Speed with in country (km/h)",
            2: "Speed across countries (km/h)"
        },
        "TeleportingTarteTrolley": {
            1: "Travel time for this TeleportingTarteTrolley (hour)",
            2: "Maximum distance this TeleportingTarteTrolley can travel (km)"
        },
    }

    def __init__(self, vehicle_type: str):
        """
        takes in a vehicle_type as string
        initialize a progressed menu interface.
        """

        self.vehicle_type = vehicle_type
        progress = ["Select Vehicle Type", "Confirm Vehicle", "Customise Parameters"]

        description = f"Customise the parameters of this new {vehicle_type}\n"\
                    + "All parameters has to be specified before confirming this vehicle.\n"\
                    + "Choose a parameter to start specifying."

        undo_prompt = "(Press Ctrl-C to go back to previous step)"

        options = dict(AddVehicleAttributeMenu.options[vehicle_type])
        for i in options.keys():
            options[i] += parse(" §R§1(Not specified)§0")
        options[len(options) + 1] = "Confirm"
        options[len(options) + 1] = "Go back to previous step"

        super().__init__(options, progress, 2, title="Create a Vehicle", description=description, undo_prompt=undo_prompt)

    def validate_positive_integer(raw: str) -> tuple[bool, str]:
        """
        Validates if an input is positive integer.
        Returns a boolean value as result, and an error message as string if applicable.
        """
        
        try:
            # try to convert raw input to int
            raw = int(raw)
            # check for positivity
            assert raw > 0, "Please enter a non-zero positive integer."
            return True, ""
        except ValueError:
            return False, "Please enter an integer"
        except AssertionError as e:
            return False, str(e)

    def execute(self) -> bool:
        """
        Executes this UI element.
        Returns False if back is selected.
        Returns True if the user confirms the vehicle.
        The boolean return value is to determine if the reason of return is wizard being competed,
        or if it got discard.
        """

        # get the parameters required by this vehicle type
        vehicle_parameters = AddVehicleAttributeMenu.vehicle_parameters[self.vehicle_type]
        parameters = {}  # dict stores parameters entered by user
        while True:
            self.display()
            option = self.wait_for_interact()

            # if user selects back or ctrl c, return False
            if not option or option == len(self.options):
                return False

            # if user selects confirm
            if option == len(self.options) - 1:
                # check if all parameters for this vehicle are specified
                if len(parameters) != len(vehicle_parameters):
                    self.input_err = "Please make sure all unspecified parameters are specified before confirming"
                    continue

                # create the vehicle
                if self.vehicle_type == "CrappyCrepeCar":
                    vehicle = CrappyCrepeCar(parameters["speed"])
                elif self.vehicle_type == "DiplomacyDonutDinghy":
                    vehicle = DiplomacyDonutDinghy(parameters["speed_internal"], parameters["speed_external"])
                else:
                    vehicle = TeleportingTarteTrolley(parameters["timeout"], parameters["distance_limit"])

                # add vehicle
                NavigationSystem.get_instance().vehicles.append(vehicle)

                # show success message
                MessageBox("Information", "Vehicle has been added to your list.", "Confirm").execute()

                return True
            
            # Define a input box for user to enter parameters
            title = ""
            prompt = ""
            undo_prompt = "(Press Ctrl-C to cancel)"
            if self.vehicle_type == "CrappyCrepeCar":
                title = "Speed of this vehicle"
                prompt = "Please enter a speed in km/h. Only positive integers are allowed."
            elif self.vehicle_type == "DiplomacyDonutDinghy":
                if option == 1:
                    title = "Speed traveling within country"
                elif option == 2:
                    title = "Speed traveling across countries"
                prompt = "Please enter a speed in km/h. Only positive integers are allowed."
            else:
                if option == 1:
                    title = "Time duration to travel"
                    prompt = "Please enter a time duration in hours. Only positive integers are allowed."
                elif option == 2:
                    title = "Maximum distance to travel"
                    prompt = "Please enter a distance in km. Only positive integers are allowed."

            # show input box and get return value
            result = ValueInputBox(title=title, prompt=prompt, undo_prompt=undo_prompt,
                                   validator=AddVehicleAttributeMenu.validate_positive_integer).execute()

            # if user cancelled the input box
            if not result:
                continue

            # store the user entered value and update the option to show specified instead of not specified
            parameters[vehicle_parameters[option - 1]] = int(result)
            self.options[option] = AddVehicleAttributeMenu.options[self.vehicle_type][option] + parse(" §G(Specified)§0")

class ManageTripsMenu(SimpleMenuUserInterface):
    """
    The UI menu for managing trips.
    The user will be able to plan a new trip or manage current available trips.
    """
    
    def __init__(self) -> None:
        """
        initialize a simple menu interface.
        """

        # define the options for this menu
        system = NavigationSystem.get_instance()
        options = {}
        options[1] = "[Plan a New Trip...]"

        # add trips to the options list
        for i in range(len(system.trips)):
            options[i + 2] = str(system.trips[i])
        
        # define description depends on whether trip menu is empty or not
        if len(options) > 1:
            description = "To get started, select a trip from the menu below,\n"\
                        + "or select 'Plan a New Trip...' to plan a custom trip"
        else:
            description = "There is no trips yet.\n"\
                        + "Please select 'Plan a New Trip...' to add a custom vehicle"

        # define an undo prompt
        undo_prompt = "(Press Ctrl-C to go back to Main Menu)"

        super().__init__(options, title="Manage Trips", description=description, undo_prompt=undo_prompt)

    def execute(self) -> None:
        """
        Executes this UI element until back is selected using Ctrl-C.
        """
        
        while True:
            self.__init__()
            self.display()
            option = self.wait_for_interact()

            # if ctrl-c is pressed, return
            if not option:
                return

            # if new trip is selected
            if option == 1:
                # check if there is any vehicle in system, if not, show error message
                system = NavigationSystem.get_instance()
                if not system.vehicles:
                    message = "There are no vehicles in this system yet.\n"\
                            + "Atleast one vehicle is required to plan a trip.\n"\
                            + "Please go to the vehicle management menu and add a vehicle."
                    MessageBox("Warning", message, "Confirm", color="R").execute()
                    continue

                # execute the add trip menu
                AddTripPlanMenu().execute()
                continue

            # if a trip is selected, show trip detail menu
            system = NavigationSystem.get_instance()
            trip = system.trips[option - 2]
            SpecificTripMenu(trip, option - 2).execute()

class AddTripPlanMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new trip.
    This menu belongs to a series of UI which makes up the Add trip wizard
    This is the first step of the wizard.
    The user will be able to choose automatic calculate or manually add trip.
    """

    options: dict[int, str] = {
        1: "Automatic Calculate Trip (Recommended)",
        2: "Manually Add Cities (Advanced)",
    }

    def __init__(self) -> None:
        """
        initialize a progressed menu interface.
        """

        # define progress
        progress = ["Plan Type", "Choose Locations" , "Choose Vehicle", "Confirm Trip"]

        # define description
        description = "Select automatic if you wish to automatically calculate the the shortest path to the destination\n"\
                    + "Or select manual to manually add cities between the departure and the destination"

        # define undo prompt
        undo_prompt = "(Press Ctrl-C to discard this new trip)"

        super().__init__(AddTripPlanMenu.options, progress, 0,
                         title="Plan a New Trip", description=description, undo_prompt=undo_prompt)

    def execute(self) -> None:
        """
        Executes this UI element until back is selected by ctrl c, or the next step returns true
        """
        
        while True:
            self.display()
            option = self.wait_for_interact()

            # If ctrl c, return
            if not option:
                return
            
            # If automatic is selected, run the automatic menu, return if the menu returned true
            if option == 1:
                if AddTripAutomaticMenu().execute():
                    return True
                continue
            
            # If manual is selected, run the manual menu, return if the menu returned true
            if option == 2:
                if AddTripManualMenu().execute():
                    return True
                continue

class AddTripAutomaticMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new trip.
    This menu belongs to a series of UI which makes up the Add trip wizard
    This is the second step (For automatic) of the wizard.
    The user will be able to select a departure and arrival location for their trip.
    """

    departure: City | None
    arrival: City | None
    options: dict[int, str] = {
        1: "Select Departure Location",
        2: "Select Arrival Location",
    }

    def __init__(self) -> None:
        """
        initialize a progressed menu interface.
        """

        self.departure = None
        self.arrival = None

        # define processes
        progress = ["Plan Type", "Choose Locations" , "Choose Vehicle", "Confirm Trip"]

        # define description
        description = "Please select the departure and the arrival location"\
                    + "Please specify both locations before entering the next step."

        # define undo prompt
        undo_prompt = "(Press Ctrl-C to go to previous step)"

        # define departure and arrival options and add not specified wording after the label
        options = dict(AddTripAutomaticMenu.options)
        for i in options.keys():
            options[i] += parse(" §R§1(Not Specified)§0")

        # add next and go back options at the end
        options[3] = "Next"
        options[4] = "Go back to previous step"

        super().__init__(options, progress, 1,
                         title="Plan a New Trip", description=description, undo_prompt=undo_prompt)

    def execute(self) -> bool:
        """
        Executes this UI element.
        Returns False if back is selected.
        Returns True if this the next step returned True.
        The boolean return value is to determine if the reason of return is wizard being competed,
        or if it got discard.
        """

        while True:
            self.display()
            option = self.wait_for_interact()

            # if back or ctrl c is selected, return False
            if not option or option == 4:
                return False
            
            # if departure city is selected, use LocationSelectMenu to let the user input a city
            if option == 1:
                self.input_err = None
                self.departure = LocationSelectionMenu(title="Set Departure City", 
                                                       description="Search and select a departure city by entering the city name",
                                                       undo_prompt="(Press Ctrl-C to go back)").execute()

            # if arrival city is selected, use LocationSelectMenu to let the user input a city
            if option == 2:
                self.input_err = None
                self.arrival = LocationSelectionMenu(title="Set Departure City", 
                                                     description="Search and select a departure city by entering the city name",
                                                     undo_prompt="(Press Ctrl-C to go back)").execute()

            # if confirm is selected, create trip and pass to next step
            if option == 3:
                # check if both departure and arrival is specified
                if self.departure and self.arrival:
                    trip = Trip(self.departure)
                    trip.add_next_city(self.arrival)
                    # execute the next step
                    if AddTripVehicleSelectionMenu(trip, "automatic").execute():
                        return True
                    continue

                # if not, show error message
                self.input_err = "Please make sure departure and arrival location are specified before confirming"
                continue

            # if departure is specified, change (not specified) text to the city name
            if self.departure:
                self.options[1] = AddTripAutomaticMenu.options[1] + parse(f" §G({self.departure})§0")

            # if arrival is specified, change (not specified) text to the city name
            if self.arrival:
                self.options[2] = AddTripAutomaticMenu.options[2] + parse(f" §G({self.arrival})§0")

class AddTripManualMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new trip.
    This menu belongs to a series of UI which makes up the Add trip wizard
    This is the second step (For manual) of the wizard.
    The user will be able to select a series of city to manually plot a trip,
    either one by one, or all at once.
    """
    
    trip: Trip | None

    def __init__(self) -> None:
        """
        initialize a progressed menu interface.
        """

        self.trip = None

        # define progress
        progress = ["Plan Type", "Choose Locations" , "Choose Vehicle", "Confirm Trip"]

        # define description
        description = "Please manually add the cities, either one by one using the append option \n"\
                    + "or enter all city at once using the 'Enter Comma Separated City Names' option.\n"\
                    + "To remove a city form the trip, enter the numbering associated to that city. \n"\
                    + "Please specify both locations before entering the next step."

        # define undo_prompt
        undo_prompt = "(Press Ctrl-C to go to previous step)"

        # get menu options dynamically calculated by get_options()
        options = self.get_options()

        super().__init__(options, progress, 1,
                         title="Plan a New Trip", description=description, undo_prompt=undo_prompt)

    def get_options(self) -> dict[int, str]:
        """
        Compost an dynamic option list consisting add options, confirm option, go back option
        and the list of cities added, where the departure and arrival is marked.
        """
        
        # define and add the first 2 options
        options = {
            1: "[Append a Single City to Trip...]",
            2: "[Enter 'Comma Separated' City Names...]"
        }
        
        # add cities to option list
        if self.trip:
            for i in range(len(self.trip.sequence)):
                city = self.trip[i]
                option_text = parse(f"§{self.color}|§0 ") + str(city)

                # if this is the first city, add departure text at the end
                if i == 0:
                    option_text += parse(" §B[Departure]§0")
                    
                # if this is the last city, add arrival text at the end
                elif i == len(self.trip.sequence) - 1:
                    option_text += parse(" §B[Arrive]§0")
                options[i + 3] = option_text

        # append confirm and go back option at the end of option list
        options[len(options) + 1] = "Confirm"
        options[len(options) + 1] = "Go back to previous step"

        return options

    def validate_comma_separated_cities(raw: str) -> tuple[bool, str]:
        """
        takes in a string
        every term of the string is separated by comma ','
        validates every-term has more than 3 chars
        return the result as a boolean, and a string as an error message if applicable 
        """
        
        try:
            trimmed = raw.strip()
            
            # check for empty value
            assert bool(trimmed), "Value cannot be empty"
            splitted = trimmed.split(",")

            # check for all term has more than 3 letters
            splitted = [i.strip() for i in splitted]
            assert all(len(i) > 2 for i in splitted), "Every filter term has to be more than 3 letters"
            return True, ""
        except AssertionError as e:
            return False, str(e)

    def get_comma_separated_cities(self) -> list[City]:
        """
        Define a input box, gether the comma separated city names and convert them into a cities
        returns the result as a list of cities
        """

        # define input box
        prompt_box = ValueInputBox("Add a List of Cities", 
                                    validator=AddTripManualMenu.validate_comma_separated_cities,
                                    prompt="Please enter a series of city names separated with comma ','",
                                    undo_prompt="(Press Ctrl-C to go back)")
        while True:
            raw = prompt_box.execute()

            # if user canceled, return nothing
            if not raw:
                return []

            # get list of city from user input
            raw_splitted = raw.split(",")
            success = True
            result = []
            for i in raw_splitted:
                # for every term, find the corresponding city
                i = i.strip()
                filtered = list(filter(lambda city: i.lower() in str(city).lower(), City.cities.values()))
                
                # if city is not found, break and show error message
                if not filtered:
                    success = False
                    prompt_box.input_err = f"Cannot find the following city: '{i}'"
                    break
                
                result.append(filtered[0])
                
            # return result if all city are found
            if success:
                return result

    def execute(self) -> bool:
        """
        Executes this UI element.
        Returns False if back is selected.
        Returns True if this the next step returned True.
        The boolean return value is to determine if the reason of return is wizard being competed,
        or if it got discard.
        """

        while True:
            self.options = self.get_options()
            self.display()
            option = self.wait_for_interact()

            # if back selected or ctrl c, return False
            if not option or option == len(self.options):
                return False
            
            # if confirm is selected, pass the trip to next step and execute next step
            if option == len(self.options) - 1:
                # if less than 2 cities are selected, show error message
                if not self.trip or len(self.trip.sequence) < 2:
                    self.input_err = "You need at least 2 cities to create a trip (Departure and Arrival City)"
                    continue

                # if next step returns true, return true
                if AddTripVehicleSelectionMenu(self.trip, "manual").execute():
                    return True

                continue

            self.input_err = None

            # if append single city is selected, use LocationSelectionMenu to get city from user
            if option == 1:
                city = LocationSelectionMenu(title="Append a City",
                                             description="Search and select a departure city by entering the city name",
                                             undo_prompt="(Press Ctrl-C to go back)").execute()

                # if user cancelled, no city is added
                if not city:
                    continue

                # add city to trip, if trip is not yet defined, define and add
                if not self.trip:
                    self.trip = Trip(city)
                    continue

                self.trip.add_next_city(city)
                continue

            # if append multiple city is selected, use get_comma_separated_cities() to get list of cities from user
            if option == 2:
                cities = self.get_comma_separated_cities()
                # add cities to trip, if trip is not defined, define and add
                if not self.trip:
                    self.trip = Trip(None)
                    self.trip.sequence = cities
                    continue

                self.trip.sequence += cities
                continue

            # if a city is selected, the city will be removed from the trip
            if len(self.trip.sequence) == 1:
                self.trip = None
                continue
            
            selected_city_index = option - 3
            del self.trip.sequence[selected_city_index]

class AddTripVehicleSelectionMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new trip.
    This menu belongs to a series of UI which makes up the Add trip wizard
    This is the third step of the wizard.
    The user will be able to select a vehicle to plan their trip.
    """

    trip: Trip
    trip_type: str

    def __init__(self, trip: Trip, trip_type: str) -> None:
        """
        takes in a trip and a trip type (manual or automatic)
        initialize a progressed menu interface.
        """

        self.trip: Trip = trip
        self.trip_type = trip_type

        # define progress
        progress = ["Plan Type", "Choose Locations" , "Choose Vehicle", "Confirm Trip"]

        # define description
        description = "Select a vehicle to complete this trip"

        # define undo_prompt
        undo_prompt = "(Press Ctrl-C to go to previous step)"

        # get a list of vehicles to form an menu option list
        system = NavigationSystem.get_instance()
        options = {}
        for i in range(len(system.vehicles)):
            options[i + 1] = str(system.vehicles[i])

        # add go back option to the option list
        options[len(system.vehicles) + 1] = "Go back to previous step"

        super().__init__(options, progress, 2,
                         title="Plan a New Trip", description=description, undo_prompt=undo_prompt)

    def execute(self) -> bool:
        """
        Executes this UI element.
        Returns False if back is selected.
        Returns True if this the next step returned True.
        The boolean return value is to determine if the reason of return is wizard being competed,
        or if it got discard.
        """
        
        while True:
            self.display()
            option = self.wait_for_interact()

            # if back or ctrl-c, return False
            if not option or option == len(self.options):
                return False
            
            # get selected vehicle
            system = NavigationSystem.get_instance()
            vehicle = system.vehicles[option - 1]
            
            # execute the next step, if the next step returns true, return true
            if AddTripConfirmTripMenu(self.trip, self.trip_type, vehicle).execute():
                return True

class AddTripConfirmTripMenu(ProgressedMenuUserInterface):
    """
    The UI menu for adding a new trip.
    This menu belongs to a series of UI which makes up the Add trip wizard
    This is the fourth step of the wizard.
    The user will be able to view and confirm the planned trip.
    """
    
    trip: Trip
    trip_type: str
    vehicle: Vehicle

    def __init__(self, trip: Trip, trip_type: str, vehicle: Vehicle) -> None:
        """
        takes in a trip and a trip type (manual or automatic),
        and a vehicle user selected from the previous step.
        initialize a progressed menu interface.
        """

        self.trip = trip
        self.trip_type = trip_type
        self.vehicle = vehicle

        # define progress
        progress = ["Plan Type", "Choose Locations" , "Choose Vehicle", "Confirm Trip"]

        # define description
        description = ""

        # define undo_prompt
        undo_prompt = "(Press Ctrl-C to go to previous step)"

        # define options
        options = {
            1: "Confirm",
            2: "Go back to previous step"
        }

        super().__init__(options, progress, 3,
                         title="Plan a New Trip", description=description, undo_prompt=undo_prompt)

    def execute(self) -> bool:
        """
        Executes this UI element.
        Returns False if back is selected.
        Returns True if this the next step returned True.
        The boolean return value is to determine if the reason of return is wizard being competed,
        or if it got discard.

        If the trip_type is automatic, a message is shown while the trip is being generated,
        and if the trip cannot be generated for the selected vehicle, an error message will be shown.
        """
        
        while True:
            # print a message for waiting
            print(parse(f"  §{self.color}[Ctrl-C to cancel]\n  §3Please hold on while the trip is being generated ... §0"))

            try:
                # generate trip if automatic, listen for ctrl-c to cancel
                if self.trip_type == "automatic":
                    calculated_trip = find_shortest_path(self.vehicle, self.trip[0], self.trip[1])
                    
                    # show an error message if the vehicle selected is not capable for this trip
                    if not calculated_trip:
                        warning = "The vehicle you have selected is not capable for this trip.\nPlease select another vehicle or modify the trip."
                        MessageBox("Warning", warning, "Confirm", color="R").execute()
                        return False

                    # save generated trip
                    self.trip = calculated_trip

                trip_time = self.trip.total_travel_time(self.vehicle)
            except KeyboardInterrupt:
                return False

            # update description to show trip details
            self.description = "The trip you have planned is:\n"\
                             + parse(f" * Trip sequence: §{self.color}{self.trip}§0 \n")\
                             + parse(f" * Planned using: §{self.color}{self.vehicle}§0\n")\
                             + f" * Travel time using: "
            
            # during manual mode
            # if trip is impossible for the selected vehicle, show warning message, but does not stop user from saving
            if trip_time == inf:
                self.description += parse("§RImpossible§0\n\n")\
                                 +  parse("§RNote that this trip is impossible for selected vehicle, but you still can add this to your list.§0")
            else:
                self.description += parse(f"§{self.color}{trip_time} Hour(s)§0")

            self.display()
            option = self.wait_for_interact()

            # if the user selected cancel, or ctrl-c, return False
            if not option or option == 2:
                return False
            
            # if confirm, save the trip and show a success message
            if option == 1:
                system = NavigationSystem.get_instance()
                system.trips.append(self.trip)

                MessageBox("Information", "Trip has been added to your list.", "Confirm").execute()

                return True

class SpecificTripMenu(SimpleMenuUserInterface):
    """
    The UI menu for viewing trip details.
    The user will be able to perform various actions, including
    export to image, simulation, find fastest vehicle and delete trip.
    """
    
    trip: Trip
    trip_index: int

    def __init__(self, trip: Trip, trip_index: int) -> None:
        """
        takes in the trip and the index of that trip.
        initialize a simple menu interface.
        """

        # pre-initialize the fields
        super().__init__({})
        self.trip = trip
        self.trip_index = trip_index

        # define options
        options = {
            1: "Export this trip to image (PNG)",
            2: "Simulate this trip",
            3: "Find fastest vehicle for this trip",
            4: "Delete this trip",
            5: "Go back"
        }

        # define title
        title = "Manage Trips"

        # define description
        description = "You are now viewing the following trip:\n"\
                    + parse(f"§{self.color}{self.trip}§0\n")\
                    + "You can simulate this trip, export this trip to PNG\n"\
                    + "or you can also find the fastest vehicle for this trip."

        # define undo_prompt
        undo_prompt = "(Press Ctrl-C to go back)"

        super().__init__(options, title=title, description=description,
                         undo_prompt=undo_prompt)

    def execute(self) -> None:
        """
        Executes this UI element until back or delete is selected.
        """

        while True:
            self.display()
            option = self.wait_for_interact()
            system = NavigationSystem.get_instance()
            
            # if go back or ctrl-c, return
            if not option or option == 5:
                return
            
            # if export trip, plot and export as png. Then shows a success message with file path
            if option == 1:
                plot_trip(self.trip, projection="merc")
                filename = "map_" + "_".join(i.name for i in self.trip) + ".png"
                export_message = parse(f"This trip has been exported to the following file:\n'§{self.color}{filename}§0'")
                MessageBox("Export trip to PNG", export_message, "Confirm").execute()
                continue

            # if simulation, execute the simulation menu
            if option == 2:
                SimulationVehicleSelection(self.trip).execute()

            # if find fastest vehicle is selected
            if option == 3:
                vehicles = system.vehicles
                # if system has no vehicle, show error message
                if not vehicles:
                    message = "There are no vehicles in this system yet.\n"\
                            + "Please go to the vehicle management menu and add a vehicle."
                    MessageBox("Warning", message, "Confirm", color="R").execute()
                    continue

                # find the fastest vehicle
                vehicle, time = self.trip.find_fastest_vehicle(vehicles)

                # if no vehicle can complete the trip, show error message
                if not vehicle:
                    message = "All vehicles are not suitable for this trip.\n"\
                            + "Maybe add a vehicle or try another trip?"
                    MessageBox("Warning", message, "Confirm", color="R").execute()
                    continue
                    
                # show detail of fastest vehicle and required time
                message = "The fastest vehicle for this trip is:\n"\
                        + parse(f"Vehicle: §{self.color}{vehicle}§0\n")\
                        + parse(f"Time required: §{self.color}{time} Hour(s)§0")
                MessageBox("Information", message, "Confirm").execute()
                continue

            # if delete is selected, delete the trip
            if option == 4:
                del system.trips[self.trip_index]
                return

class SimulationVehicleSelection(SimpleMenuUserInterface):
    """
    The UI menu for selecting a vehicle for simulation.
    The user will be able to select a vehicle to simulate the selected trip.
    """
    
    trip: Trip
    capable_vehicles: list[Vehicle]

    def __init__(self, trip: Trip) -> None:
        """
        takes in the trip to simulate.
        initialize a simple menu interface, 
        and filter out all vehicles capable for this trip.
        """

        super().__init__({})
        self.trip = trip

        # filter out all capable vehicles
        all_vehicles = NavigationSystem.get_instance().vehicles
        self.capable_vehicles = list(filter(lambda vehicle: trip.total_travel_time(vehicle) != inf, all_vehicles))

        # define and add option list with vehicles
        options = {}
        for i in range(len(self.capable_vehicles)):
            options[i + 1] = self.capable_vehicles[i]
        
        # add go back option to the end
        options[len(options) + 1] = "Back to previous step"

        # define title
        title = "Simulate Trip"

        # define description
        description = "To simulate the following trip:\n"\
                    + "You have to select a vehicle.\n"\
                    + parse(f"§{self.color}{self.trip}§0\n")\
                    + "Note: Only vehicles capable of this trip are being shown."

        # define undo_prompt
        undo_prompt = "(Press Ctrl-C to go back)"

        super().__init__(options, title=title, description=description,
                         undo_prompt=undo_prompt)

    def execute(self) -> None:
        """
        Executes this UI element until back is selected, simulation is done.
        or no capable vehicles are found
        """

        # if no capable vehicles found, show error message and return
        if not self.capable_vehicles:
            message = "No vehicle is capable for this trip\n"\
                    + "Please select another trip or add a new vehicle"
            MessageBox("Warning", message, "Confirm", color="R").execute()
            return

        self.display()
        option = self.wait_for_interact()

        # if go back or ctrl-c, return
        if not option or option == len(self.options):
            return

        # get selected vehicle and execute the simulation interface
        vehicle = self.capable_vehicles[option - 1]
        SimulationInterface(self.trip, vehicle).execute()

class SimulationInterface(UserInterface):
    """
    The UI menu for simulating a trip with a vehicle.
    The user will be able to see the trip being done by the vehicle in time ratio of 1hr to 100ms.
    """

    trip: Trip
    vehicle: Vehicle
    current_iteration: int
    current_index: int
    current_trip: tuple[City, City] | None
    current_trip_total_time: int
    current_trip_iteration: int
    color: str
    title: str
    required_time: int
    started: bool

    def __init__(self, trip: Trip, vehicle: Vehicle) -> None:
        """
        takes in the trip and the vehicle to simulate.
        initialize from a abstract user interface class.
        """

        self.trip = trip
        self.vehicle = vehicle
        self.current_iteration = 0
        self.current_index = 0
        self.current_trip = None
        self.current_trip_iteration = 0
        self.current_trip_total_time = 0
        self.color = "C"
        self.title = "Trip simulation"
        self.required_time = self.trip.total_travel_time(vehicle)
        self.started = False
        super().__init__()

    def display(self) -> None:
        """
        Display the UI element to screen without clearing the screen.
        """
        
        # display title and description
        print(parse(f"§4§{self.color}Simulating Trip§0"))
        print("  You are simulating the following trip")
        print(parse(f"  * Trip: §{self.color}{self.trip}§0"))
        print(parse(f"  * Vehicle: §{self.color}{self.vehicle}§0"))
        print(parse(f"  * Ratio: §{self.color}1 Hour : 100 ms§0"))
        print(parse(f"  * Required time: §{self.color}{self.required_time}hr | {self.required_time/10}s§0"))
        print("  Press Ctrl-C to exit this simulation")
        print("")

        # get progress percentage
        current_percentage = 0
        total_percentage = 0
        if self.started:
            # get percentage for total simulation
            total_percentage = 1
            if self.required_time != 0:
                total_percentage = (self.current_iteration + 1) / self.required_time
            
            # get percentage for current city
            current_percentage = 1
            if self.current_trip_total_time != 0:
                current_percentage = (self.current_trip_iteration + 1) / self.current_trip_total_time

        # render progress bar
        progress_bar_length = 40
        fill_length = int(progress_bar_length * total_percentage)
        blank_length = progress_bar_length - fill_length
        print(parse(f"[§{self.color}"), end="")
        print("#" * fill_length, end="")
        print(parse("§0"), end="")
        print("_" * blank_length, end="")
        print(f"] {int(total_percentage * 100)}%")

        print("")

        # list and render city
        i = 0
        for pair in self.trip.trip_pair():
            line = ""
            line += f"{pair[0]} -> {pair[1]}"
            if i == self.current_index:
                line = parse(f" §{self.color}* {line} {int(current_percentage * 100)}% §0")
            else:
                line = parse(f"   {line}     §0")

            print(line)
            i += 1

        # print a warning message
        print(parse("\n  §1§4§RPlease make sure your terminal size is large enough and maintain constant through out the simulation.§0"))

    def wait_for_interact(self) -> any:
        """
        Prompt the user of start and end of simulation,
        and simulate the trip
        """
        
        try:
            # display the UI and wait for user to begin
            self.clear()
            self.set_cursor(0,0)
            self.current_trip = list(self.trip.trip_pair())[0]
            self.current_trip_total_time = self.vehicle.compute_travel_time(self.current_trip[0], self.current_trip[1])
            self.display()

            input("\nPress Enter to begin simulation.")

            self.started = True
            
            # simulation iteration, each iteration is 1hr (100ms)
            for _ in range(self.required_time):
                # each iteration will re-render the UI without clearing, achieved using set_cursor()
                self.set_cursor(0,0)
                self.display()
                print("\n" + " " * (os.get_terminal_size().columns - 1))
                print("\n" + " " * (os.get_terminal_size().columns - 1))
                print("\n" + " " * (os.get_terminal_size().columns - 1))

                # simulate the iteration by waiting 0.1s
                sleep(0.1)

                # increment iteration by 1
                self.current_iteration += 1
                self.current_trip_iteration += 1

                # if the current city has over
                if self.current_trip_iteration >= self.current_trip_total_time:
                    # if there are no more city, break
                    if self.current_index == len(list(self.trip.trip_pair())) - 1:
                        break
                    
                    self.current_index += 1
                    self.current_trip = list(self.trip.trip_pair())[self.current_index]
                    self.current_trip_total_time = self.vehicle.compute_travel_time(self.current_trip[0], self.current_trip[1])
                    self.current_trip_iteration = 0

            # re-render the UI after simulation is done, and wait for user to exit
            self.current_trip_iteration = self.current_trip_total_time - 1
            self.current_iteration = self.required_time - 1
            self.set_cursor(0, 0)
            self.display()
            input("\nSimulation completed. Press Enter to exit.")

        except KeyboardInterrupt:
            # if user decided to discard the simulation, return
            return
            
    def execute(self) -> None:
        """
        Execute the UI.
        """

        self.clear()
        self.wait_for_interact()

def file_check(filename: str) -> bool:
    """
    Checks if a given file exists and readable.
    Returns the result as boolean
    """

    return os.path.isfile(filename) and os.access(filename, os.R_OK)

def main() -> int:
    """
    Initialize the system, check file readability and return an exit code of 1 if error.
    """
    try:
        file_path = None

        # get new filepath if default path is not readable
        if not file_check(NavigationSystem.default_source_file):
            description = f"Default sourcefile {NavigationSystem.default_source_file} is not found or access denied\n"\
                        + "Please provide a path or filename to a file containing the location data in CSV format.\n\n"
            path_box = ValueInputBox("Source File", lambda x: (True, "") if x.strip() else (False, "Filename cannot be empty."),
                                    description=description, prompt="Please enter a filename or path and hit enter.",
                                    undo_prompt="(Press Ctrl-C to exit program)", color="R")

            # read until filepath is valid
            while True:
                file_path = path_box.execute()
                if not file_path:
                    return
                
                if file_check(file_path):
                    break
                
                path_box.input_err = f"'{file_path}' File does not exist or access denied."

        # initialise default data 
        system = NavigationSystem.get_instance()
        system.initialise_data(file_path)  # fallbacks to default path if file_path is None.
        system.create_example_entities()

        # execute the menu to begin program's user interface
        MainMenu().execute()

        return 0

    except Exception as e:
        # if any exception happened during execution, log and exit
        sys.stderr.write(str(e) + "\n")
        return 1

if __name__ == "__main__":
    # exit with the return value of main()
    sys.exit(main())