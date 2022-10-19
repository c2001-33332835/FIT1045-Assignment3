from locations import City, Country, test_example_countries_and_cities

def create_cities_countries_from_CSV(path_to_csv: str) -> None:
    """
    Reads a CSV file given its path and creates instances of City and Country for each line.
    """
        raise NotImplementedError


if __name__ == "__main__":
    create_cities_countries_from_CSV("worldcities_truncated.csv")
    test_example_countries_and_cities()
