from city_country_csv_reader import create_cities_countries_from_CSV
from locations import create_example_countries_and_cities
from trip import Trip, create_example_trips
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


def determine_limiting_coordinates(trip: Trip) -> tuple[tuple[float]]:
    """
    Given a trip, determines the coordinate at the lowest left and top right corner to frame the points
    Returns a tuple of float containing the lat and lng respectivly.
    """
    limiting_coord_llcrnr: list[float, float] = None
    limiting_coord_urcrnr: list[float, float] = None
    for i in trip:
        if (not limiting_coord_llcrnr) and (not limiting_coord_urcrnr):
            limiting_coord_llcrnr = list(i.coordinate)
            limiting_coord_urcrnr = list(i.coordinate)
            continue

        if i.coordinate[0] < limiting_coord_llcrnr[0]:
            limiting_coord_llcrnr[0] = i.coordinate[0]
        if i.coordinate[1] < limiting_coord_llcrnr[1]:
            limiting_coord_llcrnr[1] = i.coordinate[1]
        if i.coordinate[0] > limiting_coord_urcrnr[0]:
            limiting_coord_urcrnr[0] = i.coordinate[0]
        if i.coordinate[1] > limiting_coord_urcrnr[1]:
            limiting_coord_urcrnr[1] = i.coordinate[1]

    # add margins to limiting coords
    limiting_coord_llcrnr = [i-5 for i in limiting_coord_llcrnr]
    limiting_coord_urcrnr = [i+5 for i in limiting_coord_urcrnr]

    # checking coordinate delta
    dlat = abs(limiting_coord_llcrnr[0] - limiting_coord_urcrnr[0])
    dlng = abs(limiting_coord_llcrnr[1] - limiting_coord_urcrnr[1])

    # add margin to latitude if not enough 50
    if dlat < 50:
        delta_margin_lat = (50 - dlat) / 2
        limiting_coord_llcrnr[0] -= delta_margin_lat
        limiting_coord_urcrnr[0] += delta_margin_lat

    # add margin to longitude if not enough 50
    if dlng < 50:
        delta_margin_lng = (50 - dlng) / 2
        limiting_coord_llcrnr[1] -= delta_margin_lng
        limiting_coord_urcrnr[1] += delta_margin_lng

    return tuple(limiting_coord_llcrnr), tuple(limiting_coord_urcrnr)


def plot_trip(trip: Trip, projection = 'robin', line_width=2, colour='b') -> None:
    """
    Plots a trip on a map and writes it to a file.
    Ensures a size of at least 50 degrees in each direction.
    Ensures the cities are not on the edge of the map by padding by 5 degrees.
    The name of the file is map_city1_city2_city3_..._cityX.png.
    """
    # print(limiting_coord_llcrnr, limiting_coord_urcrnr)
    limiting_coord_llcrnr, limiting_coord_urcrnr = determine_limiting_coordinates(trip)

    # setup mercator map projection.
    m = Basemap(llcrnrlon=limiting_coord_llcrnr[1], llcrnrlat=limiting_coord_llcrnr[0],
                urcrnrlon=limiting_coord_urcrnr[1], urcrnrlat=limiting_coord_urcrnr[0],
                lat_0=45, lon_0=-45,
                resolution='l', projection=projection)

    # plot line graph
    for i in trip.trip_pair():
        m.drawgreatcircle(i[0].coordinate[1], i[0].coordinate[0],
                        i[1].coordinate[1], i[1].coordinate[0],
                        linewidth=line_width, color=colour)
        
    m.drawcoastlines()
    m.fillcontinents()
    m.drawstates()
    filename = "map_" + "_".join(i.name for i in trip) + ".png"
    plt.savefig(filename)
    plt.close()


if __name__ == "__main__":
    from trip import Trip
    from locations import City, Country
    from city_country_csv_reader import create_cities_countries_from_CSV
    
    create_cities_countries_from_CSV("worldcities_truncated.csv")

    australia = Country.countries["Australia"]
    japan = Country.countries["Japan"]
    malaysia = Country.countries["Malaysia"]
    us = Country.countries["United States"]
    ru = Country.countries["Russia"]

    melb = australia.get_city("Melbourne")
    tokyo = japan.get_city("Tokyo")
    osaka = japan.get_city("Osaka")
    kul = malaysia.get_city("Kuala Lumpur")
    newy = us.get_city("New York")
    rostov = ru.get_city("Rostov")

    # t = Trip(melb)
    t = Trip(osaka)
    # t.add_next_city(osaka)
    t.add_next_city(tokyo)
    t.add_next_city(kul)
    t.add_next_city(newy)

    # plot_trip(t, projection="merc")
    plot_trip(t, projection="robin")