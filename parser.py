"""parsing and validating the zone settings"""


class MapParseError(Exception):
    """base execp for all map parsing issues"""
    def __init__(self, message: str, line_num: int | None = None) -> None:
        if line_num is not None:
            super().__init__(f"Error line {line_num}: {message}")
        else:
            super().__init__(f"Error: {message}")


class ZoneData:
    """structure data for each map zone, attr may be [color=green]"""
    def __init__(self, name: str, zone_type: str, x: float, y: float) -> None:
        self.name: str = name
        self.zone_type: str = zone_type
        self.x: float = x
        self.y: float = y
        self.max_drones: int = 1
        self.attributes: dict[str, str] = {}


class MapConfig:
    """
    main container for the full map config, including zone name, zone cfg and
    a list of connections [("start", "way1")] and their capacities in a dict
    """
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.zones: dict[str, ZoneData] = {}
        self.connections: dict[tuple[str, str], int] = {}


class MapParser:
    """main parser"""
    def __init__(self) -> None:
        self._config: MapConfig = MapConfig()
        self._current_line_num: int = 0

    def parse_file(self, file_path: str) -> MapConfig:
        """reads file and validates the lines"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    self._current_line_num += 1
                    cleaned_line = line.strip()
                    if not cleaned_line or cleaned_line.startswith("#"):
                        continue
                    self._parse_line(cleaned_line)
        except FileNotFoundError:
            raise MapParseError(f"File not found: '{file_path}'")
        # run global rules after file input
        self._validate_global()
        return self._config

    def _parse_line(self, line: str, ) -> None:
        """split lines into a keyword and args"""
        if ":" not in line:
            raise MapParseError("Missing colon ':' separator",
                                self._current_line_num)
        keyword, raw_args = line.split(":", 1)
        keyword = keyword.strip()
        args = raw_args.strip()
        # passing args to their each validating method
        if keyword == "nb_drones":
            self._process_drone_count(args)
        elif keyword == "connection":
            self._process_connection(args)
        else:
            self._process_zone(keyword, args)

    def _process_drone_count(self, args: str) -> None:
        """parsing validating the total drone count cfg line"""
        if self._config.nb_drones > 0:
            raise MapParseError("Duplicate 'nb_drones'")
        try:
            count = int(args)
        except ValueError:
            raise MapParseError(f"Invalid int value for drone count: {args}",
                                self._current_line_num)
        if count <= 0:
            raise MapParseError("Drone count should be positive int",
                                self._current_line_num)
        self._config.nb_drones = count

    def _process_zone(self, zone_type: str, args: str) -> None:
        """parsing validation zone layout lines into ZoneData"""
        tokens = args.split()
        if len(tokens) < 3:
            raise MapParseError(
                    "Zone requires at least a name, X and Y",
                    self._current_line_num)
        zone_name = tokens[0]
        raw_x = tokens[1]
        raw_y = tokens[2]
        if "-" in zone_name:
            raise MapParseError(
                    "Zone names cannot contain dashes", self._current_line_num)
        if zone_name in self._config.zones:
            raise MapParseError("Duplicate zone name", self._current_line_num)
        try:
            x_coord = float(raw_x)
            y_coord = float(raw_y)
        except ValueError:
            raise MapParseError("Coords must be valid numbers",
                                self._current_line_num)
        # instantiate the container class
        new_zone = ZoneData(name=zone_name,
                            zone_type=zone_type,
                            x=x_coord, y=y_coord)
        """optional bracket parameters"""
        if len(tokens) > 3:
            remaining_str = " ".join(tokens[3:])
            self._parse_optional_attributes(new_zone, remaining_str)
        self._config.zones[zone_name] = new_zone

    def _parse_optional_attributes(self, zone: ZoneData, raw_attrs: str
                                   ) -> None:
        """extracting key value config"""
        if not (raw_attrs.startswith("[") and raw_attrs.endswith("]")):
            raise MapParseError("Invalid attribute in brackets",
                                self._current_line_num)
        content = raw_attrs[1:-1].strip()
        pairs = content.split()
        for pair in pairs:
            if "=" not in pair:
                raise MapParseError("Invalid attribute in brackets",
                                    self._current_line_num)
            key, val = pair.split("=", 1)
            key = key.strip()
            val = val.strip()
            # storing in dic
            zone.attributes[key] = val
            if key == "max_drones":
                try:
                    zone.max_drones = int(val)
                except ValueError:
                    raise MapParseError("Max drones should be an int",
                                        self._current_line_num)

    def _process_connection(self, args: str) -> None:
        """parsing direction paths linking zones"""
        tokens = args.split()
        if not tokens:
            raise MapParseError("Empty connection line",
                                self._current_line_num)
        link_str = tokens[0]
        if "-" not in link_str:
            raise MapParseError("Connections must use a dash",
                                self._current_line_num)
        # splitting left and right nodes
        nodes = link_str.split("-", 1)
        zone_a = nodes[0].strip()
        zone_b = nodes[1].strip()
        if not zone_a or not zone_b:
            raise MapParseError("Invalid connection format",
                                self._current_line_num)
        if zone_a == zone_b:
            raise MapParseError("Zone cannot establish connection to itself",
                                self._current_line_num)
        # standardising pair orientation
        ordered_pair = (zone_a, zone_b) if zone_a < zone_b else (zone_b,
                                                                 zone_a)
        if ordered_pair in self._config.connections:
            raise MapParseError("Duplicate connection", self._current_line_num)
        link_capacity = 1
        # if there are brackets, look for custom capacity
        if len(tokens) > 1:
            remaining_str = "".join(tokens[1:])
            if not (remaining_str.startswith("[")
                    and remaining_str.endswith("]")):
                raise MapParseError("Invalid connection attribute",
                                    self._current_line_num)
            content = remaining_str[1:-1].strip()
            pairs = content.split()
            for pair in pairs:
                if "=" not in pair:
                    raise MapParseError("Invalid connection attribute",
                                        self._current_line_num)
                key, val = pair.split("=", 1)
                key = key.strip()
                val = val.strip()
                if key == "max_link_capacity":
                    try:
                        link_capacity = int(val)
                    except ValueError:
                        raise MapParseError("Max link capacity should be int",
                                            self._current_line_num)
        self._config.connections[ordered_pair] = link_capacity

    def _validate_global(self) -> None:
        """second layer validation"""
        has_start = False
        has_end = False
        for zone in self._config.zones.values():
            if zone.zone_type == "start_hub":
                if has_start:
                    raise MapParseError("Invalid map config with duplicates")
                has_start = True
            if zone.zone_type == "end_hub":
                if has_end:
                    raise MapParseError("Invalid map config with duplicates")
                has_end = True
        if not has_start:
            raise MapParseError("Invalid map structure missing start")
        if not has_end:
            raise MapParseError("Invalid map structure missing end")
        if self._config.nb_drones == 0:
            raise MapParseError("Invalid drone number")
        for zone_a, zone_b in self._config.connections.keys():
            if zone_a not in self._config.zones:
                raise MapParseError("Connection is not a valid zone name")
            if zone_b not in self._config.zones:
                raise MapParseError("Connection is not a valid zone name")
