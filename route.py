# route.py
# Graph part of the project.
# build_graph             -> makes adjacency list from the list of roads
# dijkstra                -> shortest distance from one place to all other places
# get_path                -> gives the actual path (list of places) using previous[]
# nearest_neighbour_route -> TSP approximation for the full delivery route

INF = float("inf")


def build_graph(roads):
    # graph is stored as an adjacency list
    # example : graph["A"] = [("B", 1), ("C", 5)]
    graph = {}
    for start, end, distance in roads:
        if start not in graph:
            graph[start] = []
        if end not in graph:
            graph[end] = []

        # roads are two way, so add the road on both sides
        graph[start].append((end, distance))
        graph[end].append((start, distance))
    return graph


def dijkstra(graph, source):
    dist = {}
    previous = {}
    for place in graph:
        dist[place] = INF
        previous[place] = None
    dist[source] = 0

    visited = set()

    while len(visited) < len(graph):
        # pick the unvisited place with the smallest distance
        current = None
        for place in graph:
            if place not in visited:
                if current is None or dist[place] < dist[current]:
                    current = place

        # smallest distance is infinity means the remaining places can't be reached
        if dist[current] == INF:
            break

        visited.add(current)

        # check all roads from current place and update the distance if shorter
        for neighbour, distance in graph[current]:
            new_dist = dist[current] + distance
            if new_dist < dist[neighbour]:
                dist[neighbour] = new_dist
                previous[neighbour] = current

    return dist, previous


def get_path(previous, source, target):
    # walk back from target to source using previous[]
    path = []
    place = target
    while place is not None:
        path.append(place)
        place = previous[place]
    path.reverse()

    # if path does not start from source then target is not reachable
    if path[0] != source:
        return []
    return path


def get_stops(selected_parcels):
    # delivery points of the selected parcels (each point only once)
    stops = []
    for p in selected_parcels:
        if p["dest"] not in stops:
            stops.append(p["dest"])
    return stops


def shortest_paths_from(graph, places):
    # run dijkstra from every place in the list
    # all_dist["A"]["B"] = shortest distance from A to B
    all_dist = {}
    all_prev = {}
    for place in places:
        dist, previous = dijkstra(graph, place)
        all_dist[place] = dist
        all_prev[place] = previous
    return all_dist, all_prev


def nearest_neighbour_route(depot, stops, all_dist):
    route = [depot]
    total = 0
    current = depot
    not_visited = stops[:]   # copy, so the original list is not changed

    while len(not_visited) > 0:
        # find the nearest stop from the current place
        nearest = not_visited[0]
        for stop in not_visited:
            if all_dist[current][stop] < all_dist[current][nearest]:
                nearest = stop

        total = total + all_dist[current][nearest]
        route.append(nearest)
        not_visited.remove(nearest)
        current = nearest

    # at the end the van comes back to the depot
    total = total + all_dist[current][depot]
    route.append(depot)

    return route, total
