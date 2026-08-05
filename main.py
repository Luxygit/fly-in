""""""

import sys
from parser import MapParser, MapParseError


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path_to_map>", file=sys.stderr)
        sys.exit(1)
    map_path: str = sys.argv[1]
    parser = MapParser()
    try:
        # load cfg, tokenise and validate it
        config = parser.parse_file(map_path)
        print(f"Parsed {len(config.zones)} zones and "
              f"{len(config.connections)} paths.")
        print(f"Simulating flight for {config.nb_drones} drones.")
    except MapParseError as e:
        print(f"Configuration rejected: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
