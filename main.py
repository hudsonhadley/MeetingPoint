import csv
import sys

import pandas as pd
from shapely.geometry import Point
import plotly.express as px
import geopy.distance as dist

from get_coordinates import get_coordinate, get_address

from random import uniform, randint


def fitness_test(generation_points, test_points):
    scores = []
    for child in generation_points:
        distances = []
        for point in test_points:
            distances.append(dist.distance([child.x, child.y], [point.x, point.y]).km)

        average_distance = sum(distances) / len(distances)

        difference = max(distances) - min(distances)

        scores.append(average_distance + difference)

    return scores


def merge(parents, population_size, mutation_rate):
    children = []

    for i in range(population_size):
        new_child_x = parents[randint(0, len(parents) - 1)].x
        new_child_y = parents[randint(0, len(parents) - 1)].y

        new_child_x += uniform(-mutation_rate, mutation_rate)
        new_child_y += uniform(-mutation_rate, mutation_rate)

        new_child_x = ((new_child_x + 90) % 179) - 90
        new_child_y = ((new_child_y + 180) % 359) - 180

        children.append(Point([new_child_x, new_child_y]))

    return children


df = pd.read_csv("cities.csv")

# Load the coordinates from the cities
coords = [get_coordinate(row[0], row[1], row[2]) for row in zip(df["City"], df["State"], df["Country"])]

df["Latitude"] = [coord.x for coord in coords]
df["Longitude"] = [coord.y for coord in coords]

generations = 200
population = 200

best_point = None
best_score = sys.maxsize
for generation_count in range(generations):

    if generation_count == 0:
        generation = [Point(uniform(-90, 90), uniform(-180, 180)) for _ in range(population)]

    else:
        generation = merge(generation[:5], population, 2)

    sorted_generations = list(zip(generation, fitness_test(generation, coords)))
    sorted_generations.sort(key=lambda x: x[1])

    generation = [i[0] for i in sorted_generations]

    if sorted_generations[0][1] < best_score:
        best_point = Point([generation[0].x, generation[0].y])
        best_score = sorted_generations[0][1]

        print(f"Generation {generation_count}: ({generation[0].x}, {generation[0].y})")

print()
print(f"Best Point: ({best_point.x}, {best_point.y})")

address = get_address(best_point.x, best_point.y)
df.loc[len(df.index)] = ["Meeting Point", address[0], address[1], address[2], best_point.x, best_point.y]

coords.append(best_point)

name_and_distance = [{"Name": df["Name"][index],
                      "Distance": dist.geodesic([best_point.x, best_point.y], [coords[index].x, coords[index].y])}
                     for index in range(len(coords) - 1)]

name_and_distance.sort(key=lambda x: x["Distance"])

for index in range(len(coords) - 1):
    print(f"{name_and_distance[index]["Name"]}: {name_and_distance[index]["Distance"]}")

fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', hover_name="Name",
                     hover_data=[df["City"], df["State"]],
                     fitbounds="locations")
fig.update_geos(visible=True,
                showcountries=True, countrycolor='Black',
                showsubunits=True, subunitcolor='Brown',
                projection_type="orthographic")

fig.show()
