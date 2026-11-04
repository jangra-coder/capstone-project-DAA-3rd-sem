# generate_data.py
# Makes random parcels and roads for testing with bigger inputs.
# If this file is run directly, it saves a medium dataset in the data folder.

import csv
import os
import random


def make_points(count):
    # Depot + delivery points C1, C2, C3 ...
    points = ["Depot"]
    for i in range(1, count + 1):
        points.append("C" + str(i))
    return points


def make_roads(points, extra_roads):
    roads = []
    used = set()   # pairs of places which already have a road

    # first connect every point with any one point before it
    # this makes sure that every point can be reached from the depot
    for i in range(1, len(points)):
        j = random.randint(0, i - 1)
        roads.append((points[j], points[i], random.randint(1, 20)))
        used.add((points[j], points[i]))

    # then add some extra random roads (skip if the two places already have a road)
    for i in range(extra_roads):
        a, b = random.sample(points, 2)
        if (a, b) not in used and (b, a) not in used:
            roads.append((a, b, random.randint(1, 20)))
            used.add((a, b))

    return roads


def make_parcels(count, points):
    parcels = []
    for i in range(1, count + 1):
        parcel = {
            "id": "P" + str(i),
            "dest": random.choice(points[1:]),   # any point except the depot
            "weight": random.randint(1, 10),
            "priority": random.randint(1, 10),
            "deadline": random.randint(1, 12),
        }
        parcels.append(parcel)
    return parcels


def save_parcels(parcels, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["parcel_id", "destination", "weight", "priority", "deadline"])
        for p in parcels:
            writer.writerow([p["id"], p["dest"], p["weight"], p["priority"], p["deadline"]])


def save_roads(roads, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["from", "to", "distance"])
        for road in roads:
            writer.writerow(road)


if __name__ == "__main__":
    random.seed(10)   # same data every time we run this file

    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    points = make_points(12)
    roads = make_roads(points, 12)
    parcels = make_parcels(40, points)

    save_parcels(parcels, os.path.join(folder, "parcels_medium.csv"))
    save_roads(roads, os.path.join(folder, "roads_medium.csv"))

    print("Saved data/parcels_medium.csv -->", len(parcels), "parcels")
    print("Saved data/roads_medium.csv   -->", len(points) - 1, "delivery points,", len(roads), "roads")
