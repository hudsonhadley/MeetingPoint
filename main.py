import csv
import sys

import pandas as pd
from shapely.geometry import Point
import plotly.express as px
import geopy.distance as dist

from math import sqrt
from random import uniform, randint


def fitness_test(generation_points, test_points):
    scores = []
    for child in generation_points:
        average_distance = total_average_distance(child, test_points)

        difference = maximum_displacement(child, test_points)

        scores.append(average_distance + difference)

    return scores


def maximum_displacement(child, test_points):
    distances = []
    for point in test_points:
        distances.append(dist.distance([child.x, child.y], [point.x, point.y]).km)

    return max(distances) - min(distances)


def total_average_distance(child, test_points):
    distances = []
    for point in test_points:
        distances.append(dist.distance([child.x, child.y], [point.x, point.y]).km)

    return sum(distances) / len(distances)


def merge(parents, population_size, mutation_rate):
    children = []

    for i in range(population_size):
        new_child_x = parents[randint(0, len(parents) - 1)].x
        new_child_y = parents[randint(0, len(parents) - 1)].y

        try:
            new_child_x += uniform(-mutation_rate, mutation_rate)
        except ValueError:
            pass

        try:
            new_child_y += uniform(-mutation_rate, mutation_rate)
        except ValueError:
            pass


        children.append(Point([new_child_x, new_child_y]))

    return children


df = pd.read_csv("cities.csv")

coords = [Point(xy) for xy in zip(df['Latitude'], df['Longitude'])]

generations = 300
population = 300

best_point = None
best_score = sys.maxsize
for generation_count in range(generations):

    if generation_count == 0:
        generation = [Point(uniform(-90, 90), uniform(-90, 90)) for _ in range(population)]

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
print(f"Best Average Distance: {total_average_distance(best_point, coords)}")
print(f"Best Maximum Difference: {maximum_displacement(best_point, coords)}")

for index in range(len(coords)):
    print(f"{df["Name"][index]}: {dist.geodesic([best_point.x, best_point.y], [coords[index].x, coords[index].y])}")


coords.append(best_point)
df.loc[len(df.index)] = ['Meeting Point', 'somewhere', 'zz', best_point.x, best_point.y]

fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', hover_name="Name")
fig.update_geos(visible=True, resolution=50, scope='usa',
                showcountries=True, countrycolor='Black',
                showsubunits=True, subunitcolor='Brown')

fig.update_layout(
    autosize=True,
    geo=dict(
        center=dict(
            lat=best_point.x,
            lon=best_point.y
        ),
        scope='usa',
        projection_scale=2
    )
)

fig.show()
