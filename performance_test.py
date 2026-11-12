# performance_test.py
# phase 4 - runs the program on small and big random data, notes the time of
# each step and then makes the runtime chart

import os
import random
import time

import matplotlib.pyplot as plt

from sorting import merge_sort
from knapsack import knapsack
from route import build_graph, get_stops, shortest_paths_from, nearest_neighbour_route
from generate_data import make_points, make_roads, make_parcels

DEPOT = "Depot"
RUNS = 3   # every test is run 3 times and the average time is taken

# (number of parcels, number of delivery points, van capacity in kg)
TESTS = [
    (10, 6, 20),
    (50, 10, 50),
    (100, 20, 100),
    (500, 50, 500),
    (1000, 100, 1000),
]

STEP_NAMES = ["Merge Sort", "0/1 Knapsack (DP)", "Dijkstra", "Nearest Neighbour TSP"]


def run_once(parcels, graph, capacity):
    # runs all the steps one time and returns time of each step in ms
    t1 = time.perf_counter()
    sorted_parcels = merge_sort(parcels)
    t2 = time.perf_counter()

    best, selected, dp = knapsack(sorted_parcels, capacity)
    t3 = time.perf_counter()

    stops = get_stops(selected)
    all_dist, all_prev = shortest_paths_from(graph, [DEPOT] + stops)
    t4 = time.perf_counter()

    route, total_km = nearest_neighbour_route(DEPOT, stops, all_dist)
    t5 = time.perf_counter()

    times = [(t2 - t1) * 1000, (t3 - t2) * 1000, (t4 - t3) * 1000, (t5 - t4) * 1000]
    return times, len(selected), len(stops), total_km


def draw_chart(results, filename):
    sizes = []
    for r in results:
        sizes.append(r["parcels"])

    for k in range(4):
        step_times = []
        for r in results:
            step_times.append(r["times"][k])
        plt.plot(sizes, step_times, marker="o", label=STEP_NAMES[k])

    plt.title("Runtime of major steps")
    plt.xlabel("Number of parcels")
    plt.ylabel("Time (milliseconds)")
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    print("Runtime chart saved -->", filename)
    plt.show()


def main():
    random.seed(1)   # same random data every time
    results = []

    print("=" * 80)
    print("                    PERFORMANCE TEST - MINI-COURIER PLANNER")
    print("=" * 80)
    print("Each test is run", RUNS, "times and the average time (in ms) is shown.")
    print()
    print(f"{'Parcels':<9}{'Points':<8}{'Capacity':<10}{'Sorting':<10}{'Knapsack':<11}"
          f"{'Dijkstra':<11}{'NN-TSP':<9}{'Total':<9}")

    for n, v, capacity in TESTS:
        # make a random dataset of this size
        points = make_points(v)
        roads = make_roads(points, v)
        graph = build_graph(roads)
        parcels = make_parcels(n, points)

        sum_times = [0, 0, 0, 0]
        for r in range(RUNS):
            times, picked, stops, total_km = run_once(parcels, graph, capacity)
            for k in range(4):
                sum_times[k] += times[k]

        avg_times = []
        for k in range(4):
            avg_times.append(sum_times[k] / RUNS)

        results.append({"parcels": n, "points": v, "roads": len(roads), "capacity": capacity,
                        "times": avg_times, "picked": picked, "stops": stops, "km": total_km})

        print(f"{n:<9}{v:<8}{capacity:<10}{avg_times[0]:<10.3f}{avg_times[1]:<11.3f}"
              f"{avg_times[2]:<11.3f}{avg_times[3]:<9.3f}{sum(avg_times):<9.3f}")

    print()
    print("Output of each test :")
    print(f"{'Parcels':<9}{'Roads':<8}{'Picked':<9}{'Stops':<8}{'Route length'}")
    for r in results:
        print(f"{r['parcels']:<9}{r['roads']:<8}{r['picked']:<9}{r['stops']:<8}{r['km']} km")

    print()
    folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(folder, exist_ok=True)
    draw_chart(results, os.path.join(folder, "runtime_chart.png"))


if __name__ == "__main__":
    main()
