"""

"""

import sys


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
    a list of connections [("start", "way1")]
    """
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.zones: dict[str, ZoneData] = {}
        self.connections: list[tuple[str, str]] = []


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
        self._validate_global_rules()
        return self._config

    def _parse_line(self, line: str, ) -> None:
        """split lines into a keyword and args"""
        if ":" not in line:
            raise MapParseError("Missing colon ':' separator",
                                self._current_line_num)
        keyword, raw_args = line.split(":", 1)
        keyword = keyword.strip()
        args = raw_args.strip()
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
        new_zone = ZoneData(name=zone_name,
                            zone_type=zone_type,
                            x=x_coord, y=y_coord)
        """optional bracket parameters"""
        if len(tokens) > 3:
            remaining_str = " ".join(tokens[3:])
            self._parse_optional_attributes(new_zone, remaining_str)
            self._config.zones[zone_name] = new_zone

    def _parse_optional_attributes(self, zone: ZoneData, raw_attrs:str) -> None:
        """extracting key value config"""
