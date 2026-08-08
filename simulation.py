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
                    coming_from = drone.current_zone
                    going_to = drone.target_zone if drone.target_zone else ""
                    # update transit is true when a drone landed this turn
                    # conn is busy until countdown is 0
                    if drone.update_transit():
                        self.graph.zones[drone.current_zone].occupy()
                        # clean conn link counter on arrival
                        old_conn = self.graph.get_connection(
                                coming_from,
                                going_to
                                )
                        if old_conn is not None:
                            old_conn.leave_path()
            # plan and launching drone paths
            # reserved spots promised to drones this turn
            reserved_spots: dict[str, int] = {}
            for drone in self.drones:
                # if drone in flight it cannot move again
                if drone.turns_in_transit > 0:
                    continue
                if drone.current_zone == self.end_hub_name:
                    continue
                path = self.router.find_shortest_path(drone.current_zone,
                                                      self.end_hub_name)
                if path is None or len(path) < 2:
                    continue
                # index0 is current spot, index1 is next step
                next_zone_name = path[1]
                next_zone = self.graph.zones[next_zone_name]
                connection = self.graph.get_connection(drone.current_zone,
                                                       next_zone_name)
                # track upcoming crowd limit
                claimed = reserved_spots.get(next_zone_name, 0)
                sim_occupancy = next_zone.current_drones + claimed
                is_full = (next_zone.zone_type != "end_hub"
                           and sim_occupancy >= next_zone.max_drones)
                if (connection is not None and not connection.is_full()
                   and not is_full):
                    self.graph.zones[drone.current_zone].release()
                    travel_duration = (2 if next_zone.zone_type == "restricted"
                                       else 1)
                    drone.start_transit(destination=next_zone_name,
                                        duration=travel_duration)
                    connection.enter_path()
                    reserved_spots[next_zone_name] = claimed + 1
                    if next_zone.zone_type == "restricted":
                        p = (drone.current_zone, next_zone_name)
                        c_name = (f"{p[0]}-{p[1]}" if p[0] < p[1] else
                                  f"{p[1]}-{p[0]}")
                        turn_log.append(f"D{drone.id}-{c_name}")
                    else:
                        turn_log.append(f"D{drone.id}-{next_zone_name}")
            if turn_log:
                print(" ".join(turn_log))
                self._print_visual_state()

    def _get_ansi_color(self, color_name: str) -> str:
        """generates the terminal color from any color word in the config"""
        name = color_name.lower().strip()
        if not name:
            return ""
        r, g, b = 0, 0, 0
        # add up char byte values across the 3 channels
        # this spreads letters evenly out of the word
        for index, char in enumerate(name):
            # reading the ASCII byte of each letter with ord
            char_value = ord(char)
            if index % 3 == 0:
                r += char_value
            elif index % 3 == 1:
                g += char_value
            else:
                b += char_value
        # modulo limits values to 255 rgb limits, adding 50 to get it bright
        final_r = (r % 205) + 50
        final_g = (g % 205) + 50
        final_b = (b % 205) + 50
        return f"\033[38;2;{final_r};{final_g};{final_b}m"

    def _print_visual_state(self) -> None:
        """prints coloured terminal output"""
        reset_code = "\033[0m"
        print(f"\n=== TURN {self.current_turn} ===")
        for name, zone in self.graph.zones.items():
            # look up any upcoming flights
            air_drones = 0
            air_drone_ids = []
            for drone in self.drones:
                if drone.turns_in_transit > 0 and drone.target_zone == name:
                    air_drones += 1
                    air_drone_ids.append(f"D{drone.id}")
            z_color = ""
            if zone.color_name:
                z_color = self._get_ansi_color(zone.color_name)
            total_here = zone.current_drones + air_drones
            if zone.zone_type in ("start_hub", "end_hub"):
                occupancy_str = (f"[ Count: {zone.current_drones} ]")
            elif total_here >= zone.max_drones:
                occupancy_str = (f"[ Full: {total_here}/{zone.max_drones}]")
            else:
                occupancy_str = (f"[ Drones: {total_here}"
                                 f"/{zone.max_drones} ]")
            air_status = ""
            if air_drone_ids:
                air_status = (f"<- In Flight: {', '.join(air_drone_ids)}")
            print(f" Zone: {z_color}{name:<12}{reset_code} "
                  f"({zone.zone_type:<10}) -> {occupancy_str}{air_status}")
        print("==============================\n")
