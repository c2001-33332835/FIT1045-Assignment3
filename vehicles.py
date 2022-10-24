from abc import ABC, abstractmethod
from math import ceil, inf

from locations import CapitalType, City, Country
from locations import create_example_countries_and_cities
# from city_country_csv_reader import create_cities_countries_from_CSV

class Vehicle(ABC):
    """
    A Vehicle defined by a mode of transportation, which results in a specific duration.
    """

    @abstractmethod
    def compute_travel_time(self, departure: City, arrival: City) -> float:
        """
        Returns the travel duration of a direct trip from one city
        to another, in hours, rounded up to an integer.
        Returns math.inf if the travel is not possible.
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Returns the class name and the parameters of the vehicle in parentheses.
        """
        pass


class CrappyCrepeCar(Vehicle):
    """
    A type of vehicle that:
        - Can go from any city to any other at a given speed.
    """

    speed: int

    def __init__(self, speed: int) -> None:
        """
        Creates a CrappyCrepeCar with a given speed in km/h.
        """
        self.speed = speed

    def compute_travel_time(self, departure: City, arrival: City) -> float:
        """
        Returns the travel duration of a direct trip from one city
        to another, in hours, rounded up to an integer.
        """
        d = departure.distance(arrival)
        return ceil(d / self.speed)


    def __str__(self) -> str:
        """
        Returns the class name and the parameters of the vehicle in parentheses.
        For example "CrappyCrepeCar (100 km/h)"
        """
        return f"CrappyCrepeCar ({self.speed} km/h)"


class DiplomacyDonutDinghy(Vehicle):
    """
    A type of vehicle that:
        - Can travel between any two cities in the same country.
        - Can travel between two cities in different countries only if they are both "primary" capitals.
        - Has different speed for the two cases.
    """

    in_country_speed: int
    between_primary_speed: int

    def __init__(self, in_country_speed: int, between_primary_speed: int) -> None:
        """
        Creates a DiplomacyDonutDinghy with two given speeds in km/h:
            - one speed for two cities in the same country.
            - one speed between two primary cities.
        """
        self.in_country_speed = in_country_speed
        self.between_primary_speed = between_primary_speed

    def compute_travel_time(self, departure: City, arrival: City) -> float:
        """
        Returns the travel duration of a direct trip from one city
        to another, in hours, rounded up to an integer.
        Returns math.inf if the travel is not possible.
        """
        in_country = departure.country == arrival.country
        # check if impossible
        if not in_country and (
            departure.capital_type != CapitalType.primary or
            arrival.capital_type != CapitalType.primary
        ):
            return inf
        d = departure.distance(arrival)
        return ceil(d / (self.in_country_speed if in_country else self.between_primary_speed))

    def __str__(self) -> str:
        """
        Returns the class name and the parameters of the vehicle in parentheses.
        For example "DiplomacyDonutDinghy (100 km/h | 200 km/h)"
        """
        return f"DiplomacyDonutDinghy ({self.in_country_speed} km/h | {self.between_primary_speed} km/h)"


class TeleportingTarteTrolley(Vehicle):
    """
    A type of vehicle that:
        - Can travel between any two cities if the distance is less than a given maximum distance.
        - Travels in fixed time between two cities within the maximum distance.
    """

    travel_time: int
    max_distance: int

    def __init__(self, travel_time:int, max_distance: int) -> None:
        """
        Creates a TarteTruck with a distance limit in km.
        """
        self.travel_time = travel_time
        self.max_distance = max_distance

    def compute_travel_time(self, departure: City, arrival: City) -> float:
        """
        Returns the travel duration of a direct trip from one city
        to another, in hours, rounded up to an integer.
        Returns math.inf if the travel is not possible.
        """
        d = departure.distance(arrival)
        if d >= self.max_distance:
            return inf
        return self.travel_time

    def __str__(self) -> str:
        """
        Returns the class name and the parameters of the vehicle in parentheses.
        For example "TeleportingTarteTrolley (5 h | 1000 km)"
        """
        return f"TeleportingTarteTrolley ({self.travel_time} h | {self.max_distance} km)"


# def create_example_vehicles() -> list[Vehicle]:
#     """
#     Creates 3 examples of vehicles.
#     """
#     return [CrappyCrepeCar(200), DiplomacyDonutDinghy(100, 500), TeleportingTarteTrolley(1, 500)]


# if __name__ == "__main__":
#     create_cities_countries_from_CSV("worldcities_truncated.csv")

#     # australia = Country.countries["Australia"]
#     # melbourne = australia.get_city("Melbourne")
#     # canberra = australia.get_city("Canberra")
#     # japan = Country.countries["Japan"]
#     # tokyo = japan.get_city("Tokyo")

#     # vehicles = create_example_vehicles()

#     # for vehicle in vehicles:
#     #     for from_city, to_city in [(melbourne, canberra), (tokyo, canberra), (tokyo, melbourne)]:
#     #         print("Travelling from {} to {} will take {} hours with {}".format(from_city, to_city, vehicle.compute_travel_time(from_city, to_city), vehicle))

#     # print(list(filter(lambda x : "fr" in x.lower(), list(Country.countries.keys()))))

#     france = Country.countries["France"]
#     paris = france.get_city("Paris")
#     bordeaux = france.get_city("Bordeaux")
#     print(list(filter(lambda x : "" in x.lower(), list([city.name for city in france.cities]))))

#     # print(paris.distance(bordeaux))