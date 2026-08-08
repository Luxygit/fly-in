""""""

import sys
from parser import MapParser, MapParseError
from models import Graph
from simulation import Simulation


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path_to_map>", file=sys.stderr)
        sys.exit(1)
    map_path: str = sys.argv[1]
    parser = MapParser()
    try:
        # load cfg, tokenise and validate it
        config = parser.parse_file(map_path)
        graph = Graph(config)
        sim = Simulation(config, graph)
        sim.run_sim()
    except MapParseError as e:
        print(f"Map error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
