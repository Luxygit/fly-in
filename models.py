"""classes where the raw data will be stored and updated live"""

from parser import MapConfig


class Zone:
    """a zone in the map with its current drone count"""
    def __init__(self, name: str,
                 zone_type: str, x: float, y: float, max_drones: int) -> None:
        self.name: str = name
        self.zone_type: str = zone_type
        self.x: float = x
        self.y: float = y
        self.max_drones: int = max_drones
        self.current_drones: int = 0
        self.color_name: str = ""

    def is_full(self) -> bool:
        """occupancy tracker"""
        if self.zone_type in ("start_hub", "end_hub"):
            return False
        return self.current_drones >= self.max_drones

    def occupy(self) -> None:
        """adds drone here"""
        self.current_drones += 1

    def release(self) -> None:
        """removes drone from here"""
        if self.current_drones > 0:
            self.current_drones -= 1


class Connection:
    """path between zones for drones to fly through"""
    def __init__(self, zone_a: str, zone_b: str, max_link_capacity: int
                 ) -> None:
        self.zone_a: str = zone_a
        self.zone_b: str = zone_b
        self.max_link_capacity: int = max_link_capacity
        self.current_drones: int = 0

    def is_full(self) -> bool:
        """check if full for next drone"""
        return self.current_drones >= self.max_link_capacity

    def enter_path(self) -> None:
        """drone enters this path"""
        self.current_drones += 1

    def leave_path(self) -> None:
        """drone leaves this path"""
        if self.current_drones > 0:
            self.current_drones -= 1


class Graph:
    """holds all zone and pathways together"""
    def __init__(self, config: MapConfig) -> None:
        # {"zone_name": Zone}
        self.zones: dict[str, Zone] = {}
        # {("zone_a", "zone_b"): Connection}
        self.connections: dict[tuple[str, str], Connection] = {}
        # a zone list with its neighbours {"start": ["path_a", "junction"]}
        self.adj_list: dict[str, list[str]] = {}
        # loading data from parser
        self._build_graph(config)

    def _build_graph(self, config: MapConfig) -> None:
        """setting up the graph maps"""
        for name, data in config.zones.items():
            new_zone = Zone(
                    name=data.name,
                    zone_type=data.zone_type,
                    x=data.x,
                    y=data.y,
                    max_drones=data.max_drones
                    )
            new_zone.color_name = data.attributes.get("color", "")
            self.zones[name] = new_zone
            # create list for this zone's neighbours
            self.adj_list[name] = []
        for pair, capacity in config.connections.items():
            zone_a, zone_b = pair
            self.connections[pair] = Connection(zone_a, zone_b, capacity)
            # saving paths bidirectionally so drones go both ways
            self.adj_list[zone_a].append(zone_b)
            self.adj_list[zone_b].append(zone_a)

    def get_neighbours(self, zone_name: str) -> list[str]:
        """returns a list of all zones connected to this zone"""
        return self.adj_list.get(zone_name, [])

    def get_connection(self, zone_1: str, zone_2: str) -> Connection | None:
        """finds the path linking two zones"""
        ordered_pair = (zone_1, zone_2) if zone_1 < zone_2 else (zone_2,
                                                                 zone_1)
        return self.connections.get(ordered_pair)
