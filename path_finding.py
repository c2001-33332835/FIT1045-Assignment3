import city_country_csv_reader
from locations import City, Country
from trip import Trip
from vehicles import Vehicle, create_example_vehicles
from networkx import dijkstra_path
from networkx import Graph as NetworkXGraph
from networkx.exception import NetworkXNoPath
from math import inf

def plot_graph_for_vehicle(vehicle: Vehicle) -> NetworkXGraph:
    """
    Plot a weighted graph.
    Takes in a vehicle.
    All cities will be plotted as Nodes and
    the travel time between all possible cities will be plotted as weighted edges.
    If the travel is impossible between any 2 cities for that vehicle, no edge for that 2 cities will be plotted
    Return the graph as networkx.Graph.
    """
    graph = NetworkXGraph()
    # plot node
    cities = list(City.cities.values())
    for city in cities:
        graph.add_node(city.city_id)
    
    n = len(cities)

    # get possible edges
    for i in range(n - 1):
        for j in range(i + 1, n):
            source = cities[i]
            destination = cities[j]

            # if edge impossible, next iteration
            if weight := vehicle.compute_travel_time(source, destination) == inf:
                continue
            
            graph.add_edge(source.city_id, destination.city_id, weight=weight)

    return graph

def find_shortest_path(vehicle: Vehicle, from_city: City, to_city: City) -> Trip:
    """
    Returns a shortest path between two cities for a given vehicle using the Dijkstra Algorithm,
    or None if there is no path.
    """

    # plot graph
    graph = plot_graph_for_vehicle(vehicle)
    
    try:
        # find path using the Dijkstra Algorithm
        path = dijkstra_path(graph, from_city.city_id, to_city.city_id)
        
        # create trip
        trip = Trip(from_city)
        for city_id in path[1:]:
            trip.add_next_city(City.cities[city_id])
        
        return trip

    except NetworkXNoPath:
        return None

if __name__ == "__main__":
    city_country_csv_reader.create_cities_countries_from_CSV("worldcities_truncated.csv")

    vehicles = create_example_vehicles()

    australia = Country.countries["Australia"]
    melbourne = australia.get_city("Melbourne")
    japan = Country.countries["Japan"]
    tokyo = japan.get_city("Tokyo")

    for vehicle in vehicles:
        print("The shortest path for {} from {} to {} is {}".format(vehicle, melbourne, tokyo, find_shortest_path(vehicle, melbourne, tokyo)))
