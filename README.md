<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h2 align="center">Sudoku Bot</h2>

  <p align="center">
    A fast Sudoku bot with a GUI, CNN digit recognition, and an optimized bitmask solver.
    <br />
    Reads puzzles from your screen and fills them in automatically.
  </p>

  ## [![Sudoku Solver Preview][product-preview]](https://github.com/lem-sleep/Sudoku-Bot/blob/main/preview.gif)
</div>

<!-- Index -->
<details>
  <summary>Index</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#requirements">Requirements</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#how-it-works">How It Works</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- GETTING STARTED -->
## Getting Started

### Requirements
- Python 3.8+
- Windows, macOS, or Linux
- A visible Sudoku board on screen (supports sudoku.com, websudoku, etc.)

### Installation

1. Install requirements:
  ```sh
  pip install -r requirements.txt
  ```

2. Run the bot:
  ```sh
  python main.py
  ```

3. A small GUI window will appear. Switch to your Sudoku tab and press **S** to solve. Press **S** again for the next puzzle — no need to restart.

4. Press **Q** to quit.

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- ABOUT THE PROJECT -->
## About The Project

I built this as a remake of [dig0w's Sudoku-Bot](https://github.com/dig0w/Sudoku-Bot), rewriting the entry point and solver from scratch while keeping the CNN and board reader intact.

The original bot solved puzzles in ~13 seconds using rule-based constraint propagation with a recursive brute-force fallback, and exited after each solve. I replaced the solver with a bitmask backtracking algorithm with MRV heuristic that solves any 9x9 puzzle in milliseconds, added a persistent GUI so you can solve back-to-back without restarting, and added a speed slider to control how fast it fills in the answers.

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- FEATURES -->
## Features

- **Persistent GUI** — small always-on-top window showing status (Ready / Solving / Filling / Error / Solved). No more restarting between puzzles.
- **Speed slider** — drag to control how fast the bot fills in cells, from slow and visible to near-instant.
- **Fast solver** — bitmask constraint tracking + backtracking with MRV heuristic. Solves puzzles in under a millisecond.
- **CNN digit recognition** — custom-trained CNN recognizes digits across different fonts and Sudoku sites. Model loads once at startup for faster repeated solves.
- **Hotkey controls** — press S to solve, Q to quit. Works globally so you can stay on your Sudoku tab.

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- HOW IT WORKS -->
## How It Works

1. Takes a screenshot and detects the largest quadrilateral (the Sudoku board)
2. Warps the board into a clean 450x450 image and splits it into 81 cells
3. Runs each cell through a CNN to recognize the digit (or 0 for empty)
4. Solves the puzzle using bitmask backtracking with MRV heuristic
5. Fills in the answers by simulating mouse clicks and key presses at the detected board position

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

**Project Link:** [github.com/lem-sleep/Sudoku-Bot](https://github.com/lem-sleep/Sudoku-Bot)

**Original Project:** [github.com/dig0w/Sudoku-Bot](https://github.com/dig0w/Sudoku-Bot)

[product-preview]: ./preview.gif
