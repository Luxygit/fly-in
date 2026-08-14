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
        self.all_movement_logs: list[str] = []

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
        end_zone = self.graph.zones[self.end_hub_name]
        while (end_zone.current_drones < total_drones):
            self.current_turn += 1
            turn_log: list[str] = []
            just_arrived: list[int] = []
            # release drone space after landing
            for drone in self.drones:
                if drone.turns_in_transit > 0:
                    coming_from = drone.current_zone
                    going_to = drone.target_zone if drone.target_zone else ""
                    # update transit is true when a drone landed this turn
                    # conn is busy until countdown is 0
                    if drone.update_transit():
                        self.graph.zones[drone.current_zone].occupy()
                        just_arrived.append(drone.id)
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
                if drone.id in just_arrived:
                    continue
                path = self.router.find_shortest_path(drone.current_zone,
                                                      self.end_hub_name)
                if path is None or len(path) < 2:
                    continue
                # index0 is current spot, index1 is next step
                next_hub_name: str = path[1]
                next_hub = self.graph.zones[next_hub_name]
                connection = self.graph.get_connection(drone.current_zone,
                                                       next_hub_name)
                # track upcoming crowd limit
                claimed = reserved_spots.get(next_hub_name, 0)
                sim_occupancy = next_hub.current_drones + claimed
                is_full = (next_hub.zone_type != "end_hub"
                           and sim_occupancy >= next_hub.max_drones)
                if (connection is not None and not connection.is_full()
                   and not is_full):
                    self.graph.zones[drone.current_zone].release()
                    h_attrs = getattr(next_hub, "attributes", {})
                    h_type = h_attrs.get("zone", "normal")
                    travel_duration = (2 if h_type == "restricted"
                                       else 1)
                    drone.start_transit(destination=next_hub_name,
                                        duration=travel_duration)
                    connection.enter_path()
                    reserved_spots[next_hub_name] = claimed + 1
                    if h_type == "restricted":
                        p = (drone.current_zone, next_hub_name)
                        c_name = (f"{p}-{p}" if p < p else
                                  f"{p}-{p}")
                        turn_log.append(f"D{drone.id}-{c_name}")
                    else:
                        turn_log.append(f"D{drone.id}-{next_hub_name}")
            if turn_log:
                self.all_movement_logs.append(" ".join(turn_log))
        for log_line in self.all_movement_logs:
            print(log_line)
        self._print_visual_history()

    def _get_ansi_color(self, color_name: str) -> str:
        """matplot lib to parse color args"""
        import matplotlib.colors as mcolors
        name = color_name.lower().strip()
        if not name:
            return ""
        if name in mcolors.CSS4_COLORS:
            # getting the rrggbb hex string and convert to base10
            hex_code = str(mcolors.CSS4_COLORS[name])
            r = int(hex_code[1:3], 16)
            g = int(hex_code[3:5], 16)
            b = int(hex_code[5:7], 16)
            return f"\033[38;2;{r};{g};{b}m"
        return ""

    def _print_visual_history(self) -> None:
        """parses text logs chronologically to build accurate maps"""
        reset_code = "\033[0m"
        layout_path = self.router.find_shortest_path(self.start_hub_name,
                                                     self.end_hub_name)
        if not layout_path:
            return
        # 1. Track the active position of every drone name string
        drone_positions: dict[int, str] = {}
        for d in self.drones:
            drone_positions[d.id] = self.start_hub_name
        # PASS 1: TURN 0 - (All drones start at the start hub)
        print("\n=== TURN 0 ===")
        for index, hub_name in enumerate(layout_path):
            hub = self.graph.zones[hub_name]
            hub_attrs = getattr(hub, "attributes", {})
            h_type = hub_attrs.get("zone", "normal")
            z_color = (self._get_ansi_color(hub.color_name)
                       if hub.color_name else "")
            g_drones = [f"D{d_id}" for d_id, loc in drone_positions.items()
                        if loc == hub_name]
            z_cur = len(g_drones)
            if hub.zone_type in ("start_hub", "end_hub"):
                occupancy_str = f"[{z_cur}]"
            else:
                occupancy_str = f"[{z_cur}/{hub.max_drones}]"
            h_occupants = ", ".join(g_drones) if g_drones else "None"
            print(f" Hub: {z_color}{hub_name:<12}{reset_code}"
                  f"({h_type:<10}) -> "
                  f"Occupancy: {occupancy_str} ({h_occupants})")
            if index < len(layout_path) - 1:
                print("  │ Connection: [0/1] (None)\n  ▼")
        print("==============================")
        # PASS 2: SIMULATED TURNS (Drones occupy destinations at turn end)
        for turn_num, log_line in enumerate(self.all_movement_logs, 1):
            print(f"\n=== TURN {turn_num} ===")
            # Parse the commands. Drones spend the turn moving, then arrive!
            movements = log_line.split()
            for move in movements:
                if "-" in move:
                    d_part, dest_hub = move.split("-", 1)
                    d_id = int(d_part[1:])
                    # Update their positions immediately because the turn time
                    # has fully elapsed by the time we draw the frame
                    drone_positions[d_id] = dest_hub
            # Draw the integrated map layout pass
            for index, hub_name in enumerate(layout_path):
                hub = self.graph.zones[hub_name]
                hub_attrs = getattr(hub, "attributes", {})
                h_type = hub_attrs.get("zone", "normal")
                z_color = (self._get_ansi_color(hub.color_name)
                           if hub.color_name else "")
                # Find who is sitting or hovering at this hub right now
                g_drones = [f"D{d_id}" for d_id, loc in drone_positions.items()
                            if loc == hub_name]
                z_cur = len(g_drones)
                if hub.zone_type in ("start_hub", "end_hub"):
                    occupancy_str = f"[{z_cur}]"
                else:
                    occupancy_str = f"[{z_cur}/{hub.max_drones}]"
                h_occupants = ", ".join(g_drones) if g_drones else "None"
                print(f" Hub: {z_color}{hub_name:<12}{reset_code}"
                      f"({h_type:<10}) -> "
                      f"Occupancy: {occupancy_str} ({h_occupants})")
                # Connection link pass (Always 0/1 because normal flights land)
                if index < len(layout_path) - 1:
                    next_hub_name = layout_path[index + 1]
                    conn = self.graph.get_connection(hub_name, next_hub_name)
                    if conn is not None:
                        print(f"  │ Connection: [0/"
                              f"{conn.max_link_capacity}] (None)")
                        print("  ▼")
            print("==============================")
