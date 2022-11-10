from locations import City, Country, test_example_countries_and_cities

def create_cities_countries_from_CSV(path_to_csv: str) -> None:
    """
    Reads a CSV file given its path and creates instances of City and Country for each line.
    """
    # read raw file content
    with open(path_to_csv, encoding="utf8") as f:
        raw = f.read()

    # parse data
    data = parse_raw_csv(raw)

    # register data to countries and cities
    for record in data["records"]:
        # register country if not exists in registry
        if not (record["country"] in Country.countries):
            Country(record["country"], record["iso3"])
        
        # register city
        City(record["city_ascii"], record["lat"], record["lng"], record["country"], record["capital"], record["id"])

def parse_row(raw_row: str, deliminater: str = ",") -> list[str]:
    """
    Takes in a string containing a raw csv row, parse into a list of strings
    Use the deliminater argument to override default deliminater of comma
    if a cell is surrounded with quotes, deliminater is treated as literals
    if double quote appered in a cell, double quote is treated as quote literal escape
    return the result in list of strings
    """
    cells = []
    # parse line by line
    in_quote = False
    cell_item = ""
    i = 0
    while i < len(raw_row):
        char = raw_row[i]

        # check if cell starts with 3 quotes
        if not cell_item and i + 2 < len(raw_row):
            if raw_row[i:i+3] == '"""':
                cell_item += '"'
                in_quote = True
                i += 3
                continue


        # check if quote is quote escape
        if (i + 1) != len(raw_row):
            next_char = raw_row[i + 1]
            if char == '"' and next_char == '"':
                cell_item += '"'
                i += 2
                continue

            # check if cell quote ends by checking leading deliminater
            if in_quote and char == '"' and next_char == deliminater:
                in_quote = False
                cells.append(cell_item)
                cell_item = ""
                i += 2
                continue


        # check if cell starts with quotes
        if char == '"' and not cell_item:
            in_quote = True
            i += 1
            continue
        
        # check if cell quote ends by checking end of line
        if in_quote and char == '"' and (i + 1) == len(raw_row):
            in_quote = False
            cells.append(cell_item)
            cell_item = ""
            i += 1
            continue

        # check for deliminater outside quote
        if not in_quote and char == deliminater:
            cells.append(cell_item)
            cell_item = ""
            i += 1
            continue
        
        cell_item += char

        i += 1
    
    # check if last cell has item
    if cell_item:
        cells.append(cell_item)

    return cells

def parse_raw_csv(raw_csv: str) -> dict:
    """
    Takes in a string containing the raw csv, seraialize into a dict with records (like a json)
    Applicable to all purpose csv where the first line contains column name / field name
    return the result in dict
    The content of the result dict has 2 fields:
     * "column_names": a list of string containing column names ordered from left to right
     * "records": a list of dict containing row records, where each dict has a key of column name and value of string value in that column
    """

    rows = raw_csv.splitlines()
    # check if nothing to parse
    if not rows:
        return {}
    
    column_names = parse_row(rows[0])
    data_rows = rows[1:]
    data_cells = [parse_row(data_row) for data_row in data_rows]

    result = {
        "column_names": column_names,
        "records": []
    }

    for row in data_cells:
        record = {}
        for i in range(len(row)):
            cell = row[i]
            column = column_names[i]
            record[column] = cell
        result["records"].append(record)
        record = {}

    return result


if __name__ == "__main__":
    create_cities_countries_from_CSV("worldcities_truncated.csv")
    for i in Country.countries:
        print(i)
        for j in Country.countries[i].cities:
            print(f"->\t{j}")