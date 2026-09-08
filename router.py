"""pathfinding Dijkstra algorithm"""

import heapq
from models import Graph


class Router:
    """finds the shortest path across the map"""
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def find_shortest_path(self, start: str, end: str) -> list[str] | None:
        """returns a list of zone names to follow or None if no path"""
        # what zones to look at next
        # min heap array with tuples (accumulated_cost, node_name)
        queue: list[tuple[int, str]] = [(0, start)]
        # dict to trace back how we found each zone [zone, zone we came from]
        parent_tracker: dict[str, str | None] = {start: None}
        # tracking path weight (zonename: total_cost_to_get_there)
        weights: dict[str, int] = {start: 0}
        while queue:
            # extracting current cheapest node in 0(logN)
            current_weight, current = heapq.heappop(queue)
            if current == end:
                break
            # reconsider new faster path
            if current_weight > weights.get(current, 999999):
                continue
            for neighbour_name in self.graph.get_neighbours(current):
                neighbour_hub = self.graph.zones[neighbour_name]
                if neighbour_hub.zone_type == "blocked":
                    continue
                # if havent visisted this neighbour yet, save it
                hub_type = neighbour_hub.zone_type
                if hub_type == "restricted":
                    move_cost = 4
                elif hub_type == "priority":
                    move_cost = 1
                else:
                    move_cost = 2
                new_weight = current_weight + move_cost
                best_known = weights.get(neighbour_name, float("inf"))
                if new_weight < best_known:
                    weights[neighbour_name] = new_weight
                    parent_tracker[neighbour_name] = current
                    heapq.heappush(queue, (new_weight, neighbour_name))
        if end not in parent_tracker:
            return None
        # rebuild the path from end to start
        path: list[str] = []
        step: str | None = end
        while step is not None:
            path.append(step)
            step = parent_tracker[step]
        path.reverse()
        return path
