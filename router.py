"""pathfinding algorithm BFS breadth first search"""

from models import Graph


class Router:
    """finds the shortest path across the map"""
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def find_shortest_path(self, start: str, end: str) -> list[str] | None:
        """returns a list of zone names to follow or None if no path"""
        # what zones to look at next
        queue: list[tuple[float, str]] = [(0.0, start)]
        # dict to trace back how we found each zone [zone, zone it came from]
        parent_tracker: dict[str, str | None] = {start: None}
        # tracking path weight
        weights: dict[str, float] = {start: 0.0}
        while queue:
            queue.sort(key=lambda x: x[0])
            current_weight, current = queue.pop(0)
            if current == end:
                break
            # reconsider new faster path
            if current_weight > weights.get(current, float('inf')):
                continue
            for neighbour_name in self.graph.get_neighbours(current):
                # if havent visisted this neighbour yet, save it
                neighbour_hub = self.graph.zones[neighbour_name]
                hub_attrs = getattr(neighbour_hub, "attributes", {})
                hub_type = hub_attrs.get("zone", "normal")
                if hub_type == "blocked":
                    continue
                if hub_type == "priority":
                    move_cost = 0.1
                else:
                    move_cost = 1.0
                new_weight = current_weight + move_cost
                is_cheaper = new_weight < weights.get(neighbour_name,
                                                      float('inf'))
                if neighbour_name not in weights or is_cheaper:
                    weights[neighbour_name] = new_weight
                    parent_tracker[neighbour_name] = current
                    queue.append((new_weight, neighbour_name))
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
