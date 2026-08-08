*This project has been created as part of the 42 curriculum by dievarga*

# Fly-in

## Description

A-Maze-ing is a Python project that generates a seed-based maze on a
rectangular grid, draws a "42" pattern of permanently closed cells 
somewhere in the middle of it, and find the shortest valid path from
an entry cell to an exit cell. The maze can be generated in two modes:

- PERFECT=True: a perfect maze, with exactly one path between entry and exit.
- PERFECT=False (default): a Pac-Man style playable board, fully connected,
  so a chased Pac-Man player always has an alternative route, and dead ends
  are rare.

The generated maze is written to a text file (hexadecimal) and
displayed in a graphical window using the MiniLibX (MLX) library.

## Instructions

### Installation

python3 -m venv .venv
pip install mlx-2_2-py3-none-any.whl

make (or make install) does this automatically.

### Debugging
Using make pdb we got access to pythons debugger to examine the program:
- n (Next): Executes the current line and moves to the next line
- s (Step): Steps inside a function call
- c (Continue): Lets the program run normally until it hits a crash or finishes
- p <variable> (Print): Displays the live contents of any variable
- l (List): Prints the surrounding lines of code
- q (Quit): Instantly terminates the debugger

### Execution

python3 a_maze_ing.py config.txt

or

make run

config.txt is the only argument, and can be replaced by any other config file
path. Errors (missing file, bad syntax, invalid dimensions, entry/exit outside
the grid or on the same cell, etc.) are reported with a clear message and the
program exits without crashing.

Once the window is open:

1         | Re-generate a new maze        
2         | Show / hide the shortest path 
3         | Change the wall colours         
4/ESC     | Quit                       

### Makefile targets

- make install      : create the virtual environment and install dependencies
- make run          : run the project with a default config file
- make debug        : run the project under pdb pythons debugger
- make clean        : remove caches and stop any hanging window process
- make lint         : run flake8 and mypy
- make lint-strict  : execute the commands flake8 . and mypy . --strict

## Config File Format

One KEY=VALUE pair per line. Lines starting with # are ignored.

 Key         | Description                         | Example            
 WIDTH       | Maze width in cells                 | WIDTH=20            
 HEIGHT      | Maze height in cells                | HEIGHT=15           
 ENTRY       | Entry coordinates (x,y)             | ENTRY=0,0           
 EXIT        | Exit coordinates (x,y)              | EXIT=19,14          
 OUTPUT_FILE | Output filename                     | OUTPUT_FILE=maze.txt
 PERFECT     | Perfect maze or Pac-Man board       | PERFECT=True        
 SEED        | Optional, integer, reproducibility  | SEED=42             

Minimum size for the patter to appear is WIDTH >= 13 and HEIGHT >= 9.

## Maze Generation Algorithm

Depth-First Search (recursive backtracker): starting from the entry cell,
the algorithm marks the current cell as visited, picks a random unvisited
neighbour, knocks down the wall between them, and moves into it, pushing every
step onto a history stack. When a cell has no unvisited neighbour left, the
algorithm backtracks by popping the stack until it finds a cell with an
unexplored side. The search ends once the stack is empty, which produces a
spanning tree that touches every reachable cell exactly once: a perfect maze.

For PERFECT=False, extra walls are then knocked down between remaining
dead-end cells and one of their neighbours, which loops while checking that 
no 3x3 block of cells ends up fully open, to respect the maximum corridor 
width rule.

### Why DFS?

DFS with a stack is simple to implement and to understand, it naturally
guarantees every cell is reachable, it produces long corridors well 
suited to a maze, and it is easy to seed for reproducibility since 
the only randomness is random.choice() picking the next neighbour.

### BFS Algorithm
To solve the maze with the shortest path, DFS would have to analyze too many
possible different paths and give out the shortest, possibly crashing the 
system.
Because of this using BFS breadth first search gives us a faster more
efficient way of finding the shortest path, by advancing horizontally 
through the possible solutions and stopping right when any of them gets
to the exit.

## Code Reusability

The maze generation and solving logic lives in a single standalone module,
mazegen.py, with no dependency on MLX or on any other project file. It
exposes one class, MazeGenerator.

This module is packaged as mazegen-.whl at the root of the
repository, built from gen_maze.py and pyproject.toml via python3 -m build
To rebuild it:

python3 -m venv build_env
pip install mazegen-.whl
```
import example:

from gen_maze import MazeGenerator
maze = MazeGenerator(
    width=15,
    height=15,
    entry_coord=(1, 1),
    exit_coord=(13, 13),
    seed=12345,
    perfect=False
)
print(f"Cell (1,1) wall integer: {maze.grid[1][1].walls}")'
```
The main project (a_maze_ing.py, gen_maze.py, solve_maze.py, write_maze.py
mlx_view.py) is a separate layer on top of it: config parsing, output
file writing, and the MLX display.

## Resources

- MLX documentation (man pages inside the provided wheel)
- Wikipedia: [Maze generation algorithm]
    (https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- Python ctypes documentation, used by the MLX Python wrapper
- Python packaging user guide, for building the mazegen wheel

### AI usage

AI (Claude & Gemini) were used to:
- Debug the code
- Understand DFS algorithm logic and implementation
- Understand Mlx graphic library documentation

## Team and Project Management

- Roles: Both members of the team worked on their or own versions
    of the entire project, so in the end, the final version implemented
    the best approach for every part from each member.
- Planning: First we had to do some research about way of implementing
    any sort of maze generating algorithm, then once that was covered and
    the scope of the project seemd relatively small, we decided to make
    it more interesting by using the Mlx lib as an output.
    Once we had our own versions on how to do this and discussed
    and merged them into one, we polished the bugs and edge cases which in 
    the end were not many and were quite easy to debug.
- What worked well / what could be improved: The algorithm implementation
    was the easiest to get along with how to create and solve the maze.
    But the Mlx documentation provided seemed to obscure and hard to 
    analyze and comprehend, it is something that almost made us drop that
    part of the project.
- Tools used: Python3, MiniLibX (MLX), flake8, mypy, git

## Licensing

This project is distributed under the MIT license, see LICENSE.md.
