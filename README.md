# Capstone Assignment – Mini-Courier Planner (Sem-3)

Rahul (2501350043) - DAA

Course: Design & Analysis of Algorithms (ETCCDA302)
Faculty: Dr. Shweta Agarwal

## About

A small courier planning system made in Python. It takes a list of parcels and a road map
of delivery points and gives two things:

- **Packing plan** - which parcels should go in the van for one trip
- **Delivery route** - in which order the van should visit the delivery points

It uses the algorithms done in the lab assessments : Merge Sort, 0/1 Knapsack (Dynamic Programming),
Dijkstra's Algorithm and Nearest Neighbour (TSP approximation).

All the algorithms are written by hand. Only Python built-in modules are used,
`matplotlib` is used only for the runtime chart.

## Project Structure

```
main.py              -> main program, runs all the steps one by one
sorting.py           -> merge sort for parcels
knapsack.py          -> 0/1 knapsack (DP) and printing of the DP table
route.py             -> graph, dijkstra, path and nearest neighbour route
generate_data.py     -> makes random parcels and roads for bigger tests
test_cases.py        -> test cases to check that the output is correct
performance_test.py  -> runtime of each step on small and big data + chart
data/                -> sample datasets (csv files)
results/             -> runtime chart
screenshots/         -> screenshots of the output
```

## How to Run

Python 3 is needed. Install matplotlib once (only needed for the chart):

```
pip install matplotlib
```

1. Run the planner on the small sample data (van capacity 20 kg):

```
python main.py
```

2. Run it on any other dataset (parcels file, roads file, van capacity):

```
python main.py data/parcels_medium.csv data/roads_medium.csv 60
```

3. Run the test cases:

```
python test_cases.py
```

4. Run the performance test (it also saves `results/runtime_chart.png`):

```
python performance_test.py
```

To make a new random medium dataset : `python generate_data.py`

---

## Phase 1 – Courier Problem Design and Planning

### Problem

The courier depot has many parcels, but the van can carry only a limited weight in one trip.
So the system has to:

1. find which parcels are more urgent (sorting)
2. choose the best parcels that fit in the van (knapsack)
3. find the shortest roads between the delivery points (dijkstra)
4. make a short route that visits all the chosen points and comes back to the depot (nearest neighbour)

### Parcel attributes

| Field       | Meaning                                              | Example |
|-------------|------------------------------------------------------|---------|
| parcel_id   | id of the parcel                                     | P1      |
| destination | delivery point of the parcel                         | C       |
| weight      | weight in kg (whole number)                          | 6       |
| priority    | how important the parcel is, 1 (low) to 10 (high)    | 8       |
| deadline    | parcel must be delivered within these many hours     | 2       |

Parcels file (`data/parcels_small.csv`):

```
parcel_id,destination,weight,priority,deadline
P1,C,6,8,2
P2,A,3,5,4
P3,E,9,9,3
...
```

### Delivery points and graph format

- The starting point is always called `Depot`. Delivery points are A to F in the small data
  and C1, C2 ... in the random data.
- Roads file has `from,to,distance` (distance in km). Roads are two way, so the map is an
  **undirected weighted graph**.
- In the program the graph is stored as an **adjacency list** (dictionary of lists):

```
graph["A"] = [("Depot", 4), ("B", 1), ("C", 5)]
```

Adjacency list is used because every place has only a few roads, so it takes less memory than
an adjacency matrix, and dijkstra can directly go through the neighbours of a place.

Roads file (`data/roads_small.csv`):

```
from,to,distance
Depot,A,4
Depot,B,2
A,B,1
A,C,5
B,C,8
B,D,10
C,D,3
C,E,2
D,E,4
D,F,6
E,F,3
```

### Algorithms selected

| Step           | Algorithm         | Why this one | Time | Space |
|----------------|-------------------|--------------|------|-------|
| Sort parcels   | Merge Sort        | always O(n log n) (quick sort can become O(n²)) and it is stable, so parcels with same deadline and priority keep their order | O(n log n) | O(n) |
| Fill the van   | 0/1 Knapsack (DP) | a parcel can't be cut, so greedy does not always give the best answer. DP gives the best answer without trying all 2^n groups | O(n × W) | O(n × W) |
| Shortest paths | Dijkstra          | all road distances are positive, and it gives the shortest distance from one place to all places | O(V²) for one source | O(V) |
| Delivery route | Nearest Neighbour | finding the best route (TSP) is NP-hard, k stops have k! orders. Nearest neighbour gives a good route very fast | O(k²) | O(k) |

n = number of parcels, W = van capacity, V = places in the map, k = stops in the route

Dijkstra is run from the Depot and from every stop (k + 1 times), so the full dijkstra step is O(k × V²).

### Design (how the steps work together)

```
   parcels.csv                                roads.csv
        |                                         |
        v                                         v
   Merge Sort                               Build graph
   (deadline, then priority)                (adjacency list)
        |                                         |
        v                                         |
   0/1 Knapsack (DP) ---> packing plan            |
        |                                         |
        | delivery points of selected parcels     |
        v                                         v
        +----------> Dijkstra (from Depot and every stop)
                                |
                                v
                     Nearest Neighbour route
                                |
                                v
                  final route + total distance
```

Why sorting is done before knapsack : the parcels go into the DP table in deadline order.
While going back in the DP table (from the last parcel to the first), a parcel is left out
whenever the same total priority can be made without it. So if two groups of parcels give the
same total priority, the parcels with earlier deadline are kept. The packing plan is also
shown in deadline order.

---

## Phase 2 – Package Prioritization and Box Filling

Output of `python main.py` (small data, capacity 20 kg):

```
============================================================
                  MINI-COURIER PLANNER
============================================================
Parcels file    : parcels_small.csv
Roads file      : roads_small.csv
Van capacity    : 20 kg
Total parcels   : 10
Delivery points : 6 (+ Depot)
Roads           : 11

------------------------------------------------------------
STEP 1 : Parcels sorted by deadline, then priority (Merge Sort)
------------------------------------------------------------
ID    Dest    Weight  Priority  Deadline
P5    F       5       7         1
P1    C       6       8         2
P7    A       4       6         2
P3    E       9       9         3
P2    A       3       5         4
P10   B       5       5         4
P6    D       8       6         5
P4    B       2       3         6
P9    C       1       2         7
P8    E       7       4         8

------------------------------------------------------------
STEP 2 : Box filling using 0/1 Knapsack (Dynamic Programming)
------------------------------------------------------------
DP table (w = weight, p = priority) :
capacity ->        0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20
no parcel          0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0
P5 (w=5,p=7)       0  0  0  0  0  7  7  7  7  7  7  7  7  7  7  7  7  7  7  7  7
P1 (w=6,p=8)       0  0  0  0  0  7  8  8  8  8  8 15 15 15 15 15 15 15 15 15 15
P7 (w=4,p=6)       0  0  0  0  6  7  8  8  8 13 14 15 15 15 15 21 21 21 21 21 21
P3 (w=9,p=9)       0  0  0  0  6  7  8  8  8 13 14 15 15 15 16 21 21 21 22 23 24
P2 (w=3,p=5)       0  0  0  5  6  7  8 11 12 13 14 15 18 19 20 21 21 21 26 26 26
P10 (w=5,p=5)      0  0  0  5  6  7  8 11 12 13 14 15 18 19 20 21 21 23 26 26 26
P6 (w=8,p=6)       0  0  0  5  6  7  8 11 12 13 14 15 18 19 20 21 21 23 26 26 26
P4 (w=2,p=3)       0  0  3  5  6  8  9 11 12 14 15 16 18 19 21 22 23 24 26 26 29
P9 (w=1,p=2)       0  2  3  5  7  8 10 11 13 14 16 17 18 20 21 23 24 25 26 28 29
P8 (w=7,p=4)       0  2  3  5  7  8 10 11 13 14 16 17 18 20 21 23 24 25 26 28 29

Packing plan for this trip :
ID    Dest    Weight  Priority  Deadline
P5    F       5       7         1
P1    C       6       8         2
P7    A       4       6         2
P2    A       3       5         4
P4    B       2       3         6

Parcels selected   : 5 out of 10
Total weight       : 20 / 20 kg
Total priority     : 29
Left for next trip : P3, P10, P6, P9, P8
```

- Sorting : P5 has the earliest deadline (1 hour) so it comes first. P1 and P7 both have
  deadline 2, so P1 comes first because of higher priority. P2 and P10 have the same deadline
  and same priority, so they stay in the same order as in the file (merge sort is stable).
- How to read the DP table : row P7 and column 15 is 21. It means using only the first three
  parcels (P5, P1, P7) with 15 kg space, the best total priority is 21 (7 + 8 + 6).
  The last cell (29) is the final answer.
- The van takes P5, P1, P7, P2, P4 = 20 kg (full) with total priority 29.
- If we fill the van greedily (highest priority first) we get P3, P1, P5 = only 24 priority.
  P3 has high priority (9) but it is heavy (9 kg), and the best group with P3 gives only 26.
  So greedy is not correct for 0/1 knapsack and DP is needed.

---

## Phase 3 – Route Maker and Graph Processing

Output of `python main.py` (continued):

```
------------------------------------------------------------
STEP 3 : Road map and shortest paths (Dijkstra)
------------------------------------------------------------
Graph as adjacency list (place --> neighbour(distance)) :
Depot  --> A(4)  B(2)
A      --> Depot(4)  B(1)  C(5)
B      --> Depot(2)  A(1)  C(8)  D(10)
C      --> A(5)  B(8)  D(3)  E(2)
D      --> B(10)  C(3)  E(4)  F(6)
E      --> C(2)  D(4)  F(3)
F      --> D(6)  E(3)

Shortest distance from Depot to every delivery point :
A      :   3 km   Depot -> B -> A
B      :   2 km   Depot -> B
C      :   8 km   Depot -> B -> A -> C
D      :  11 km   Depot -> B -> A -> C -> D
E      :  10 km   Depot -> B -> A -> C -> E
F      :  13 km   Depot -> B -> A -> C -> E -> F

------------------------------------------------------------
STEP 4 : Delivery route (Nearest Neighbour - TSP approximation)
------------------------------------------------------------
Stops to visit     : F, C, A, B
Visiting order     : Depot -> B -> A -> C -> F -> Depot

Leg 1 : Depot to B = 2 km   (Depot -> B)
Leg 2 : B to A = 1 km   (B -> A)
Leg 3 : A to C = 5 km   (A -> C)
Leg 4 : C to F = 5 km   (C -> E -> F)
Leg 5 : F to Depot = 13 km   (F -> E -> C -> A -> B -> Depot)

Full road path     : Depot -> B -> A -> C -> E -> F -> E -> C -> A -> B -> Depot
Total route length : 26 km
```

- Dijkstra finds that going to A through B (2 + 1 = 3 km) is shorter than the direct road (4 km).
- Stops are the delivery points of the selected parcels. A has two parcels (P7, P2) but it is
  visited only once.

How the nearest neighbour route is made (distances are the dijkstra shortest distances):

| Now at | Not visited stops (km)    | Nearest | km |
|--------|---------------------------|---------|----|
| Depot  | B 2, A 3, C 8, F 13       | B       | 2  |
| B      | A 1, C 6, F 11            | A       | 1  |
| A      | C 5, F 10                 | C       | 5  |
| C      | F 5                       | F       | 5  |
| F      | all visited, go to Depot  | Depot   | 13 |
|        |                           | **Total** | **26** |

For this small data, 26 km is also the best possible route (checked in `test_cases.py` by
trying every order of the stops).

---

## Phase 4 – Performance Testing and Optimization

### Test cases

Output of `python test_cases.py`:

```
============================================================
                      TEST CASES
============================================================
PASS --> Merge sort order is same as Python sorted() for 300 parcels
PASS --> Knapsack DP answer is same as brute force (20 random cases)
PASS --> Knapsack with capacity 0 selects nothing
PASS --> Knapsack with very big capacity selects all parcels
PASS --> Small dataset : knapsack picks P5, P1, P7, P2, P4 (priority 29)
PASS --> Dijkstra distances from Depot are same as hand calculation
PASS --> Dijkstra gives infinity for a place that is not connected
PASS --> Route starts and ends at Depot
PASS --> Route visits every stop exactly once
PASS --> Small dataset : total route length is 26 km
PASS --> Small dataset : nearest neighbour route is same as the best route
------------------------------------------------------------
Passed : 11   Failed : 0

Medium dataset (capacity 60 kg, 10 stops) :
Nearest neighbour route : 105 km   (time 0.0175 ms)
Best possible route     : 95 km   (time 4144.6 ms, tried every order)
Nearest neighbour is 10.5% longer than the best route
```

### Runtime of major steps

Output of `python performance_test.py` (average of 3 runs, time in milliseconds):

```
Parcels  Points  Capacity  Sorting   Knapsack   Dijkstra   NN-TSP   Total
10       6       20        0.014     0.025      0.036      0.004    0.078
50       10      50        0.062     0.262      0.146      0.007    0.476
100      20      100       0.177     1.224      0.670      0.020    2.091
500      50      500       1.014     35.529     7.978      0.157    44.678
1000     100     1000      2.180     148.893    51.625     0.485    203.183

Output of each test :
Parcels  Roads   Picked   Stops   Route length
10       8       5        4       104 km
50       19      17       9       135 km
100      38      28       17      186 km
500      96      172      49      552 km
1000     197     350      96      1201 km
```

![Runtime chart](results/runtime_chart.png)

### Comparison of the steps

- **Knapsack** takes the most time. It fills a table of (n + 1) × (W + 1) cells, and in this
  test both n and W become 10 times bigger (from 100 to 1000), so the time becomes about 100 times more.
- **Dijkstra** is second. One run is O(V²) and it runs once for every stop, so it grows fast
  when the map has more points (100 points and 96 stops in the last test).
- **Merge Sort** stays small (about 2 ms for 1000 parcels) because n log n grows slowly.
- **Nearest Neighbour** is the fastest (less than 1 ms), it only compares distances (k² work).
  Trying every order for just 10 stops took a few seconds (10! = 3628800 orders), so the
  exact TSP answer is not practical when stops increase.
- Nearest neighbour does not always give the best route. In the medium data it gave 105 km
  but the best route is 95 km (10.5% longer), because it only looks at the next nearest stop.

### Optimization ideas (for future)

1. **Dijkstra with a min-heap** (`heapq`) - picking the closest place becomes O(log V) instead of O(V),
   so one run becomes O((V + E) log V). This will help a lot for big road maps.
2. **Knapsack with a 1-D array** - only the previous row is needed, so memory can be O(W)
   instead of O(n × W) (a small extra table is needed to find which parcels were taken).
3. **Improve the route with 2-opt** - after nearest neighbour, reverse a part of the route if it
   makes the route shorter. This can reduce the extra 10.5% distance.
4. **Use distance in knapsack** - knapsack only looks at weight and priority. In the medium data
   it picks P2 (priority 1) only to fill the last 1 kg, and the van has to go to C4 for it
   (27 km leg). Distance or delivery cost can be added to the value of a parcel.
5. **Deadlines in the route** - the route is made only by distance, deadlines can also be checked
   while choosing the next stop.
6. **More than one trip** - run knapsack again on the parcels left for the next trip.

---

## Phase 5 – Result and Demonstration

### Final result (small data)

| Item             | Result                          |
|------------------|---------------------------------|
| Parcels in depot | 10                              |
| Van capacity     | 20 kg                           |
| Parcels selected | 5 (P5, P1, P7, P2, P4)          |
| Weight used      | 20 / 20 kg                      |
| Total priority   | 29                              |
| Route            | Depot -> B -> A -> C -> F -> Depot |
| Total distance   | 26 km                           |

The most urgent parcel P5 (deadline 1 hour) is in the van and the van is fully used. DP chose
the group with the highest total priority, which is better than the greedy choice (29 vs 24).
The route first goes to the closest stops (B, A, C) and then to F, which is the farthest point
(13 km from the Depot), so the way back from F is the longest part of the route.

The program also works for any other data in the same csv format, for example the medium data
(40 parcels, 12 delivery points, capacity 60 kg) gives 14 parcels with total priority 97 and
a route of 105 km.

### Screenshots

Small data - sorting, DP table and packing plan

![Sorting and knapsack](screenshots/phase2_sorting_knapsack.png)

Small data - graph, shortest paths and route

![Route](screenshots/phase3_route.png)

Medium data

![Medium data](screenshots/medium_dataset.png)

Test cases

![Test cases](screenshots/test_cases.png)

Performance test

![Performance test](screenshots/performance_test.png)

### Conclusion

This project joins four algorithms in one system. Merge sort finds the urgent parcels, 0/1 knapsack
(DP) fills the van in the best way, Dijkstra finds the shortest roads and nearest neighbour makes the
full route. Exact algorithms are used where they are fast enough, and an approximation is used for
the route because the exact TSP answer takes too much time when the number of stops increases.
