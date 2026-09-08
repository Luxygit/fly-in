"""
engine that handles turns, moves drones along paths, checks zones and prints
- free up space after drones move
- plan and move drone and makes a drone mov string
- finish turn, prints all drone strings and then repeats
"""


from models import Graph
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
        initial_path = self.router.find_shortest_path(self.start_hub_name,
                                                      self.end_hub_name)
        if initial_path is None:
            from parser import MapParseError
            raise MapParseError("No valid path exists.")
        self.drones: list[Drone] = []
        # working drone objects starting at 1
        for i in range(1, config.nb_drones + 1):
            self.drones.append(Drone(drone_id=i,
                                     start_zone=self.start_hub_name))
        # all drones set at start
        self.graph.zones[self.start_hub_name].current_drones = config.nb_drones
        self.all_movement_logs: list[str] = []

    def _find_hubs(self) -> None:
        """scans graph zones and locates start and end hubs"""
        for zone_name, zone_obj in self.graph.zones.items():
            if zone_obj.identity_type == "start_hub":
                self.start_hub_name = zone_name
            elif zone_obj.identity_type == "end_hub":
                self.end_hub_name = zone_name

    def _process_arrivals(self) -> tuple[list[str], set[int]]:
        """updates flying drones and frees capacities when they land"""
        arrival_logs: list[str] = []
        just_landed: set[int] = set()
        for drone in self.drones:
            if drone.target_zone is not None:
                coming_from = drone.current_zone
                going_to = drone.target_zone
                # update_transit True if a drone lands this turn
                if drone.update_transit():
                    self.graph.zones[going_to].occupy()
                    old_conn = self.graph.get_connection(coming_from, going_to)
                    if old_conn is not None:
                        old_conn.leave_path()
                    arrival_logs.append(f"D{drone.id}-{going_to}")
                    just_landed.add(drone.id)
        return arrival_logs, just_landed

    def _route_resting_drones(self, moved_this_turn: set[int]) -> list[str]:
        """checks capacities and launches drones"""
        turn_log: list[str] = []
        reserved_spots: dict[str, int] = {}
        reserved_conn: dict[tuple[str, str], int] = {}
        current_zone_ct = {name: z.current_drones for name,
                           z in self.graph.zones.items()}
        current_conn_ct = {pair: conn.current_drones for pair, conn in
                           self.graph.connections.items()}
        for drone in self.drones:
            # skip flying drones or at the end or just landed in this turn
            if drone.turns_in_transit > 0 or drone.target_zone is not None:
                continue
            if drone.id in moved_this_turn:
                continue
            if drone.current_zone == self.end_hub_name:
                continue
            path = self.router.find_shortest_path(drone.current_zone,
                                                  self.end_hub_name)
            if path is None or len(path) < 2:
                continue
            next_hub_name: str = path[1]
            next_hub = self.graph.zones[next_hub_name]
            connection = self.graph.get_connection(drone.current_zone,
                                                   next_hub_name)
            if connection is None:
                continue
            conn_key = (connection.zone_a, connection.zone_b)
            claimed_zone = reserved_spots.get(next_hub_name, 0)
            claimed_conn = reserved_conn.get(conn_key, 0)
            is_conn_full = (current_conn_ct[conn_key] + claimed_conn
                            >= connection.max_link_capacity)
            if is_conn_full:
                continue
            h_type = next_hub.zone_type
            if h_type != "restricted":
                sim_occupancy = (current_zone_ct[next_hub_name]
                                 + claimed_zone)
                is_zone_full = (
                        next_hub.identity_type not in ("start_hub", "end_hub")
                        and sim_occupancy >= next_hub.max_drones)
                if is_zone_full:
                    continue
            # drone takes off
            og_zone = drone.current_zone
            self.graph.zones[og_zone].release()
            current_zone_ct[og_zone] = max(0, current_zone_ct[og_zone] - 1)
            reserved_conn[conn_key] = claimed_conn + 1
            reserved_spots[next_hub_name] = claimed_zone + 1
            if h_type == "restricted":
                drone.start_transit(destination=next_hub_name,
                                    duration=1)
                connection.enter_path()
                # logs connection movement
                turn_log.append(f"D{drone.id}-{og_zone}-{next_hub_name}")
            else:
                drone.current_zone = next_hub_name
                next_hub.occupy()
                # logs reached zone
                turn_log.append(f"D{drone.id}-{next_hub_name}")
        return turn_log

    def step_turn(self) -> list[str]:
        """sim takes 1 turn"""
        total_drones: int = len(self.drones)
        end_zone = self.graph.zones[self.end_hub_name]
        if end_zone.current_drones >= total_drones:
            return []
        self.current_turn += 1
        arrival_logs, moved_this_turn = self._process_arrivals()
        launch_logs = self._route_resting_drones(moved_this_turn)
        turn_log: list[str] = arrival_logs + launch_logs
        log_line = " ".join(turn_log)
        self.all_movement_logs.append(log_line)
        print(f"{log_line}")
        return turn_log

    def run_sim(self) -> None:
        """running the main turn loop"""
        total_drones: int = len(self.drones)
        end_zone = self.graph.zones[self.end_hub_name]
        while (end_zone.current_drones < total_drones
               and self.current_turn < 999):
            self.step_turn()
        if end_zone.current_drones < total_drones:
            print("Sim aborted after max turns allowed")
