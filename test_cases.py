# test_cases.py
# Phase 4 : test cases to check that every step gives the correct output.

import os
import random
import time
from itertools import combinations, permutations

from sorting import merge_sort
from knapsack import knapsack
from route import INF, build_graph, dijkstra, get_stops, shortest_paths_from, nearest_neighbour_route
from generate_data import make_points, make_parcels
from main import BASE_FOLDER, read_parcels, read_roads

passed = 0
failed = 0


def check(name, condition):
    global passed, failed
    if condition:
        print("PASS -->", name)
        passed += 1
    else:
        print("FAIL -->", name)
        failed += 1


def brute_force_knapsack(parcels, capacity):
    # try every possible group of parcels and keep the best total priority
    best = 0
    for size in range(len(parcels) + 1):
        for group in combinations(parcels, size):
            weight = sum(p["weight"] for p in group)
            value = sum(p["priority"] for p in group)
            if weight <= capacity and value > best:
                best = value
    return best


def best_route_length(depot, stops, all_dist):
    # try every order of the stops and keep the shortest route (only for few stops)
    best = INF
    for order in permutations(stops):
        route = [depot] + list(order) + [depot]
        length = 0
        for i in range(len(route) - 1):
            length += all_dist[route[i]][route[i + 1]]
        if length < best:
            best = length
    return best


random.seed(5)
points = make_points(10)

small_parcels = read_parcels(os.path.join(BASE_FOLDER, "data", "parcels_small.csv"))
small_roads = read_roads(os.path.join(BASE_FOLDER, "data", "roads_small.csv"))
small_graph = build_graph(small_roads)

print("=" * 60)
print("                      TEST CASES")
print("=" * 60)

# Test 1 : merge sort should give the same order as python's sorted()
# (sorted() is also stable, so this also checks that equal parcels keep their order)
parcels = make_parcels(300, points)
mine = merge_sort(parcels)
python_sorted = sorted(parcels, key=lambda p: (p["deadline"], -p["priority"]))
check("Merge sort order is same as Python sorted() for 300 parcels",
      [p["id"] for p in mine] == [p["id"] for p in python_sorted])

# Test 2 : knapsack DP should give the same best value as checking all groups
all_ok = True
for t in range(20):
    group = make_parcels(random.randint(5, 12), points)
    cap = random.randint(5, 30)
    best, selected, dp = knapsack(group, cap)
    if best != brute_force_knapsack(group, cap):
        all_ok = False
    # selected parcels must fit in the van and their priority must add up to best
    if sum(p["weight"] for p in selected) > cap or sum(p["priority"] for p in selected) != best:
        all_ok = False
check("Knapsack DP answer is same as brute force (20 random cases)", all_ok)

# Test 3 : edge cases of knapsack
best, selected, dp = knapsack(small_parcels, 0)
check("Knapsack with capacity 0 selects nothing", best == 0 and len(selected) == 0)

best, selected, dp = knapsack(small_parcels, 1000)
check("Knapsack with very big capacity selects all parcels", len(selected) == len(small_parcels))

# Test 4 : small dataset answer checked by hand
sorted_small = merge_sort(small_parcels)
best, selected, dp = knapsack(sorted_small, 20)
check("Small dataset : knapsack picks P5, P1, P7, P2, P4 (priority 29)",
      best == 29 and [p["id"] for p in selected] == ["P5", "P1", "P7", "P2", "P4"])

# Test 5 : dijkstra distances on small road map (checked by hand)
dist, previous = dijkstra(small_graph, "Depot")
expected = {"Depot": 0, "A": 3, "B": 2, "C": 8, "D": 11, "E": 10, "F": 13}
check("Dijkstra distances from Depot are same as hand calculation", dist == expected)

# Test 6 : place with no road connection should get infinity
g = build_graph([("Depot", "A", 5), ("X", "Y", 2)])
dist, previous = dijkstra(g, "Depot")
check("Dijkstra gives infinity for a place that is not connected", dist["X"] == INF)

# Test 7 : route should start and end at Depot and visit each stop once
stops = get_stops(selected)
all_dist, all_prev = shortest_paths_from(small_graph, ["Depot"] + stops)
route, total = nearest_neighbour_route("Depot", stops, all_dist)
check("Route starts and ends at Depot", route[0] == "Depot" and route[-1] == "Depot")
check("Route visits every stop exactly once", sorted(route[1:-1]) == sorted(stops))

# Test 8 : total route length for small dataset (checked by hand)
check("Small dataset : total route length is 26 km", total == 26)

# Test 9 : nearest neighbour vs best route (found by trying every order of stops)
check("Small dataset : nearest neighbour route is same as the best route",
      total == best_route_length("Depot", stops, all_dist))

print("-" * 60)
print("Passed :", passed, "  Failed :", failed)

# nearest neighbour is only an approximation, so compare it on the medium dataset also
medium_parcels = read_parcels(os.path.join(BASE_FOLDER, "data", "parcels_medium.csv"))
medium_graph = build_graph(read_roads(os.path.join(BASE_FOLDER, "data", "roads_medium.csv")))
best, selected, dp = knapsack(merge_sort(medium_parcels), 60)
stops = get_stops(selected)
all_dist, all_prev = shortest_paths_from(medium_graph, ["Depot"] + stops)

t1 = time.perf_counter()
route, total = nearest_neighbour_route("Depot", stops, all_dist)
t2 = time.perf_counter()
best_total = best_route_length("Depot", stops, all_dist)
t3 = time.perf_counter()

print()
print("Medium dataset (capacity 60 kg,", len(stops), "stops) :")
print(f"Nearest neighbour route : {total} km   (time {(t2 - t1) * 1000:.4f} ms)")
print(f"Best possible route     : {best_total} km   (time {(t3 - t2) * 1000:.1f} ms, tried every order)")
print(f"Nearest neighbour is {(total - best_total) / best_total * 100:.1f}% longer than the best route")
