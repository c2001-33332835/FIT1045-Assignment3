from __future__ import annotations 
from enum import Enum
from geopy.distance import great_circle


class CapitalType(Enum):
    """
    The different types of capitals (e.g. "primary").
    """
    primary = "primary"
    admin = "admin"
    minor = "minor"
    unspecified = ""

    def __str__(self) -> str:
        return self.value


class Country():
    """
    Represents a country.
    """

    countries: dict[str, Country] = dict() # a dict that associates country names to instances.
    name: str
    iso3: str
    cities: list[City]

    def __init__(self, name: str, iso3: str) -> None:
        """
        Creates an instance with a country name and a country ISO code with 3 characters.
        """
        self.name = name
        self.iso3 = iso3.upper()
        self.cities = []
        Country.countries[name] = self

    def _add_city(self, city: City):
        """
        Adds a city to the country.
        """
        self.cities.append(city)

    def get_cities(self, capital_types: list[CapitalType] = None) -> list[City]:
        """
        Returns a list of cities of this country.

        The argument capital_types can be given to specify a subset of the capital types that must be returned.
        Cities that do not correspond to these capital types are not returned.
        If no argument is given, all cities are returned.
        """
        # if capital_types not specified, return a all cities
        if not capital_types:
            return self.cities

        # if capital_types specified, filter and return a list of cities
        return list(filter(lambda city: city.capital_type in capital_types, self.cities))

    def get_city(self, city_name: str) -> City:
        """
        Returns a city of the given name in this country.
        Returns None if there is no city by this name.
        If there are multiple cities of the same name, returns an arbitrary one.
        """
        cities = list(filter(lambda city: city.name == city_name, self.cities))
        if not cities:
            return None
        
        return cities[0]

    def __str__(self) -> str:
        """
        Returns the name of the country.
        """
        return self.name


class City():
    """
    Represents a city.
    """

    name: str
    cities: dict[str, City] = dict() # a dict that associates city IDs to instances.
    coordinate: tuple[float, float] # a vector for the coordinate. [0] is latitude, and [1] is longitude
    capital_type: CapitalType
    country: Country
    city_id: str

    def __init__(self, name: str, latitude: str, longitude: str, country: str, capital_type: str, city_id: str) -> None:
        """
        Initialises a city with the given data.
        """

        self.name = name
        self.coordinate = (float(latitude), float(longitude))
        self.country = Country.countries[country]
        self.city_id = city_id
        City.cities[city_id] = self

        # check if capital type is defined in enum
        if capital_type in CapitalType.__members__:
            self.capital_type = CapitalType[capital_type]
        else:
            self.capital_type = CapitalType.unspecified

        # add city to country
        self.country._add_city(self)

    def distance(self, other_city: City) -> int:
        """
        Returns the distance in kilometers between two cities using the great circle method,
        rounded up to an integer.
        """
        d = great_circle(self.coordinate, other_city.coordinate).kilometers
        return round(d)

    def __str__(self) -> str:
        """
        Returns the name of the city and the country ISO3 code in parentheses.
        For example, "Melbourne (AUS)".
        """
        return f"{self.name} ({self.country.iso3})"

    def __repr__(self) -> str:
        """
        Return a string representation of the object in comply with the python convention.
        For example, City('Melbourne', '-37.8136', '144.9631', 'Australia', 'admin', '1036533631')
        """

        params = [self.name, self.coordinate[0], self.coordinate[1], self.country.name, self.capital_type.value, self.city_id]
        params = [repr(str(param)) for param in params]

        return "City(" + (", ".join(params)) + ")"


def create_example_countries_and_cities() -> None:
    """
    Creates a few Countries and Cities for testing purposes.
    """
    australia = Country("Australia", "AUS")
    melbourne = City("Melbourne", "-37.8136", "144.9631", "Australia", "admin", "1036533631")
    canberra = City("Canberra", "-35.2931", "149.1269", "Australia", "primary", "1036142029")
    sydney = City("Sydney", "-33.865", "151.2094", "Australia", "admin", "1036074917")

    japan = Country ("Japan", "JPN")
    tokyo = City("Tokyo", "35.6839", "139.7744", "Japan", "primary", "1392685764")


def test_example_countries_and_cities() -> None:
    """
    Assuming the correct cities and countries have been created, runs a small test.
    """
    australia = Country.countries['Australia']
    canberra =  australia.get_city("Canberra")
    melbourne = australia.get_city("Melbourne")
    sydney = australia.get_city("Sydney")

    print("The distance between {} and {} is {}km".format(melbourne, sydney, melbourne.distance(sydney)))

    for city in australia.get_cities([CapitalType.admin, CapitalType.primary]):
        print("{} is a {} capital of {}".format(city, city.capital_type, city.country))


if __name__ == "__main__":
    create_example_countries_and_cities()
    test_example_countries_and_cities()