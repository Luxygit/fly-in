"""
engine that handles turns, moves drones along paths, checks zones and prints
- free up space after drones move
- plan and move drone and print
- finish turn and repeat
"""


from graph import Graph
from drone import Drone
from router import Router
from parser import MapConfig


class Simulation:
    """managing turn loop and drone movement state"""
    def __init__(self, config: MapConfig, graph: Graph) -> None:
        self.graph: Graph = graph
        self.router: Router = Router(graph)
        self.current_turn: int = 0
        self.start_hub_name: str = ""
        self.end_hub_name: str = ""
        self._find_hubs()
        self.drones: list[Drone] = []
        # working drone objects starting at 1
        for i in range(1, config.nb_drones + 1):
            self.drones.append(Drone(drone_id=i,
                                     start_zone=self.start_hub_name))
        # all drones set at start
        self.graph.zones[self.start_hub_name].current_drones = config.nb_drones

    def _find_hubs(self) -> None:
        """scans graph zones and locates start and end hubs"""
        for zone_name, zone_obj in self.graph.zones.items():
            if zone_obj.zone_type == "start_hub":
                self.start_hub_name = zone_name
            elif zone_obj.zone_type == "end_hub":
                self.end_hub_name = zone_name

    def run_sim(self) -> None:
        """running the main turn loop"""
        total_drones: int = len(self.drones)
        while (self.graph.zones[self.end_hub_name].current_drones
               < total_drones):
            self.current_turn += 1
        turn_log: list[str] = []
        # release drone space after landing
        for drone in self.drones:
            if drone.turns_in_transit > 0:
                # update transit is true when a drone landed this turn
                if drone.update_transit():
                    self.graph.zones[drone.current_zone].occupy()
        # plan and launching drone paths
        for drone in self.drones:
            # if drone in flight it cannot move again
            if drone.turns_in_transit > 0:
                continue
            if drone.current_zone == self.end_hub_name:
                continue
            path = self.router.find_shortest_path(drone.current_zone,
                                                  self.end_hub_name)
            if path is not None and len(path) > 1:
                # index0 is current spot, index1 is next step
                next_zone_name = path[1]
                next_zone = self.graph.zone[next_zone_name]
            connection = self.graph.get_connection(drone.current_zone,
                                                   next_zone_name)
            if (connection is not None and not connection.is_full()
               and not next_zone.is_full()):
                self.graph.zones[drone.current_zone].release()
                travel_duration = (2 if next_zone.zone_type == "restricted"
                                   else 1)
                drone.start_transit(destination=next_zone_name,
                                    duration=travel_duration)
                connection.enter_path()
                turn_log.append(f"D{drone.id}-{next_zone_name}")
        if turn_log:
            print(" ".join(turn_log))
