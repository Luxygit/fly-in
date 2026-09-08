"""main execution function"""

import sys
from parser import MapParser, MapParseError
from models import Graph
from simulation import Simulation
from visualizer import Visualizer


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
        print(f"{config.nb_drones} drones at start zone.")
        has_color = any(zone.color_name != "" for zone in graph.zones.values())
        if has_color:
            vis = Visualizer(simulation=sim, graph=graph)
            vis.run()
            print(f"Sim finished in {sim.current_turn} turns!")
            sys.exit(0)
        sim.run_sim()
        print(f"Sim finished in {sim.current_turn} turns!")
    except MapParseError as e:
        print(f"Map error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSimulation aborted", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
