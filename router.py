"""pathfinding algorithm BFS breadth first search"""

from collections import deque
from models import Graph


class Router:
    """finds the shortest path across the map"""
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def find_shortest_path(self, start: str, end: str) -> list[str] | None:
        """returns a list of zone names to follow or None if no path"""
        # what zones to look at next
        queue: deque[str] = deque([start])
        # dict to trace back how we found each zone [zone, zone it came from]
        parent_tracker: dict[str, str | None] = {start: None}
        while queue:
            current: str = queue.popleft()
            if current == end:
                break
            for neighbour in self.graph.get_neighbours(current):
                # if havent visisted this neighbour yet, save it
                if self.graph.zones[neighbour].zone_type == "blocked":
                    continue
                if neighbour not in parent_tracker:
                    parent_tracker[neighbour] = current
                    queue.append(neighbour)
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
