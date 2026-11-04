# main.py
# Mini-Courier Planner
# Steps :
#   1. read parcels and roads from the csv files
#   2. sort parcels by deadline using merge sort
#   3. choose the best parcels for one trip using 0/1 knapsack (DP)
#   4. find shortest paths using dijkstra
#   5. make the delivery route using nearest neighbour (TSP approximation)
#
# How to run :
#   python main.py                                     -> uses the small sample data
#   python main.py <parcels csv> <roads csv> <capacity>

import csv
import os
import sys
import time

from sorting import merge_sort
from knapsack import knapsack, print_dp_table
from route import INF, build_graph, get_path, get_stops, shortest_paths_from, nearest_neighbour_route

DEPOT = "Depot"

# folder of this file, so the data folder is found even if we run from some other folder
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


def read_parcels(filename):
    parcels = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            parcel = {
                "id": row["parcel_id"],
                "dest": row["destination"],
                "weight": int(row["weight"]),
                "priority": int(row["priority"]),
                "deadline": int(row["deadline"]),
            }
            parcels.append(parcel)
    return parcels


def read_roads(filename):
    roads = []
    with open(filename, "r") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        for row in reader:
            roads.append((row["from"], row["to"], int(row["distance"])))
    return roads


def print_heading(text):
    print()
    print("-" * 60)
    print(text)
    print("-" * 60)


def print_parcels(parcels):
    print(f"{'ID':<6}{'Dest':<8}{'Weight':<8}{'Priority':<10}{'Deadline'}")
    for p in parcels:
        print(f"{p['id']:<6}{p['dest']:<8}{p['weight']:<8}{p['priority']:<10}{p['deadline']}")


def main():
    # default input = small sample dataset
    parcels_file = os.path.join(BASE_FOLDER, "data", "parcels_small.csv")
    roads_file = os.path.join(BASE_FOLDER, "data", "roads_small.csv")
    capacity = 20

    # if files and capacity are given in the command line then use them
    if len(sys.argv) >= 3:
        parcels_file = sys.argv[1]
        roads_file = sys.argv[2]
    if len(sys.argv) >= 4:
        if not sys.argv[3].isdigit() or int(sys.argv[3]) == 0:
            print("ERROR: capacity should be a positive whole number -->", sys.argv[3])
            return
        capacity = int(sys.argv[3])

    for name in [parcels_file, roads_file]:
        if not os.path.exists(name):
            print("ERROR: File not found -->", name)
            return

    parcels = read_parcels(parcels_file)
    roads = read_roads(roads_file)
    graph = build_graph(roads)

    if DEPOT not in graph:
        print("ERROR: there is no road from Depot in", roads_file)
        return

    print("=" * 60)
    print("                  MINI-COURIER PLANNER")
    print("=" * 60)
    print("Parcels file    :", os.path.basename(parcels_file))
    print("Roads file      :", os.path.basename(roads_file))
    print("Van capacity    :", capacity, "kg")
    print("Total parcels   :", len(parcels))
    print("Delivery points :", len(graph) - 1, "(+ Depot)")
    print("Roads           :", len(roads))

    # parcel whose delivery point is not in the road map can't be delivered
    valid_parcels = []
    for p in parcels:
        if p["dest"] in graph:
            valid_parcels.append(p)
        else:
            print("WARNING: delivery point", p["dest"], "not found, so parcel", p["id"], "is skipped")
    parcels = valid_parcels

    # ---------------- STEP 1 : sorting ----------------
    t1 = time.perf_counter()
    sorted_parcels = merge_sort(parcels)
    t2 = time.perf_counter()

    print_heading("STEP 1 : Parcels sorted by deadline, then priority (Merge Sort)")
    print_parcels(sorted_parcels)

    # ---------------- STEP 2 : knapsack ----------------
    t3 = time.perf_counter()
    best, selected, dp = knapsack(sorted_parcels, capacity)
    t4 = time.perf_counter()

    print_heading("STEP 2 : Box filling using 0/1 Knapsack (Dynamic Programming)")
    if len(sorted_parcels) <= 15 and capacity <= 30:
        print("DP table (w = weight, p = priority) :")
        print_dp_table(dp, sorted_parcels, capacity)
    else:
        print("DP table is too big to print, so only the result is shown.")
        print("Table size :", len(dp), "rows x", capacity + 1, "columns")

    print()
    print("Packing plan for this trip :")
    print_parcels(selected)

    total_weight = 0
    for p in selected:
        total_weight += p["weight"]

    left_ids = []
    for p in sorted_parcels:
        if p not in selected:
            left_ids.append(p["id"])

    print()
    print("Parcels selected   :", len(selected), "out of", len(sorted_parcels))
    print("Total weight       :", total_weight, "/", capacity, "kg")
    print("Total priority     :", best)
    if len(left_ids) > 0:
        print("Left for next trip :", ", ".join(left_ids))
    else:
        print("Left for next trip : none")

    # ---------------- STEP 3 : dijkstra ----------------
    stops = get_stops(selected)

    t5 = time.perf_counter()
    all_dist, all_prev = shortest_paths_from(graph, [DEPOT] + stops)
    t6 = time.perf_counter()

    print_heading("STEP 3 : Road map and shortest paths (Dijkstra)")
    print("Graph as adjacency list (place --> neighbour(distance)) :")
    for place in graph:
        text = ""
        for neighbour, distance in graph[place]:
            text += f"{neighbour}({distance})  "
        print(f"{place:<6} --> {text.strip()}")

    print()
    print("Shortest distance from Depot to every delivery point :")
    for place in graph:
        if place == DEPOT:
            continue
        if all_dist[DEPOT][place] == INF:
            print(f"{place:<6} : not reachable")
        else:
            path = get_path(all_prev[DEPOT], DEPOT, place)
            print(f"{place:<6} : {all_dist[DEPOT][place]:>3} km   {' -> '.join(path)}")

    # ---------------- STEP 4 : nearest neighbour route ----------------
    print_heading("STEP 4 : Delivery route (Nearest Neighbour - TSP approximation)")

    # remove the stops which can't be reached from the depot
    reachable_stops = []
    for stop in stops:
        if all_dist[DEPOT][stop] == INF:
            print("WARNING:", stop, "can not be reached from Depot, so it is skipped")
        else:
            reachable_stops.append(stop)
    stops = reachable_stops

    t7 = time.perf_counter()
    route, total_km = nearest_neighbour_route(DEPOT, stops, all_dist)
    t8 = time.perf_counter()

    if len(stops) == 0:
        print("No parcel to deliver, so no route is needed.")
    else:
        print("Stops to visit     :", ", ".join(stops))
        print("Visiting order     :", " -> ".join(route))
        print()

        full_path = [DEPOT]
        for i in range(len(route) - 1):
            a = route[i]
            b = route[i + 1]
            path = get_path(all_prev[a], a, b)
            full_path += path[1:]   # first place of this path is already added
            print(f"Leg {i + 1} : {a} to {b} = {all_dist[a][b]} km   ({' -> '.join(path)})")

        print()
        print("Full road path     :", " -> ".join(full_path))
        print("Total route length :", total_km, "km")

    # ---------------- time taken ----------------
    print_heading("Time taken by each step")
    print(f"Merge Sort            : {(t2 - t1) * 1000:.4f} ms")
    print(f"0/1 Knapsack (DP)     : {(t4 - t3) * 1000:.4f} ms")
    print(f"Dijkstra              : {(t6 - t5) * 1000:.4f} ms")
    print(f"Nearest Neighbour TSP : {(t8 - t7) * 1000:.4f} ms")


if __name__ == "__main__":
    main()
