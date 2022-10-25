from vehicles import Vehicle, CrappyCrepeCar, DiplomacyDonutDinghy, TeleportingTarteTrolley
from vehicles import create_example_vehicles
from locations import City, Country
from locations import create_example_countries_and_cities
from math import inf


class Trip():
    """
    Represents a sequence of cities.
    """

    sequence: list[City]

    def __init__(self, departure: City) -> None:
        """
        Initialises a Trip with a departure city.
        """
        self.sequence = [departure]

    def add_next_city(self, city: City) -> None:
        """
        Adds the next city to this trip.
        """
        self.sequence.append(city)

    def total_travel_time(self, vehicle: Vehicle) -> float:
        """
        Returns a travel duration for the entire trip for a given vehicle.
        Returns math.inf if any leg (i.e. part) of the trip is not possible.
        """

        total_time = 0
        for i in range(len(self.sequence) - 1):
            source = self.sequence[i]
            destination = self.sequence[i + 1]
            time = vehicle.compute_travel_time(source, destination)
            if time == inf:
                return inf
            total_time += time

        return total_time


    def find_fastest_vehicle(self, vehicles: list[Vehicle]) -> tuple[Vehicle, float]:
        """
        Returns the Vehicle for which this trip is fastest, and the duration of the trip.
        If there is a tie, return the first vehicle in the list.
        If the trip is not possible for any of the vehicle, return (None, math.inf).
        """
        travel_times = [self.total_travel_time(vehicle) for vehicle in vehicles]
        minimum = min(travel_times)
        for i in range(len(vehicles)):
            if travel_times[i] == minimum:
                return vehicles[i], minimum

    def __str__(self) -> str:
        """
        Returns a representation of the trip as a sequence of cities:
        City1 -> City2 -> City3 -> ... -> CityX
        """

        # convert each city into string, and join them using an arrow symbol
        return " -> ".join(str(i) for i in self.sequence)


def create_example_trips() -> list[Trip]:
    """
    Creates examples of trips.
    """

    #first we create the cities and countries
    create_example_countries_and_cities()

    australia = Country.countries["Australia"]
    melbourne = australia.get_city("Melbourne")
    sydney = australia.get_city("Sydney")
    canberra = australia.get_city("Canberra")
    japan = Country.countries["Japan"]
    tokyo = japan.get_city("Tokyo")

    #then we create trips
    trips = []

    for cities in [(melbourne, sydney), (canberra, tokyo), (melbourne, canberra, tokyo), (canberra, melbourne, tokyo)]:
        trip = Trip(cities[0])
        for city in cities[1:]:
            trip.add_next_city(city)

        trips.append(trip)

    return trips


if __name__ == "__main__":
    vehicles = create_example_vehicles()
    trips = create_example_trips()

    for trip in trips:
        vehicle, duration = trip.find_fastest_vehicle(vehicles)
        print("The trip {} will take {} hours with {}".format(trip, duration, vehicle))