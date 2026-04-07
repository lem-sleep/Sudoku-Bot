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
    <li><a href="#download">Download</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#option-1-download-the-exe">Option 1: Download the .exe</a></li>
        <li><a href="#option-2-run-from-source">Option 2: Run from source</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#how-it-works">How It Works</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- DOWNLOAD -->
## Download

**[Download SudokuBot.exe from the latest release](https://github.com/lem-sleep/Sudoku-Bot/releases/latest)**

No Python or dependencies required. Just download and run.

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

### Option 1: Download the .exe

1. Go to [Releases](https://github.com/lem-sleep/Sudoku-Bot/releases/latest) and download `SudokuBot.exe`
2. Run `SudokuBot.exe`

### Option 2: Run from source

**Requirements:** Python 3.8+, Windows

1. Clone the repo:
   ```sh
   git clone https://github.com/lem-sleep/Sudoku-Bot.git
   cd Sudoku-Bot
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```sh
   python main.py
   ```

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- USAGE -->
## Usage

1. Launch the bot. A small always-on-top GUI window appears.
2. Open a Sudoku puzzle in your browser (supports sudoku.com, websudoku, etc.).
3. Press **S** to solve the current puzzle.

### Controls

| Key | Action |
|-----|--------|
| **S** | Solve the puzzle on screen (or stop auto-replay) |
| **Q** | Quit the bot |

### GUI Options

- **Speed slider** — controls how fast the bot fills in cells. Drag left for slow (visible cell-by-cell), drag right for near-instant.
- **Auto Replay** — toggle this ON to farm puzzles automatically. When enabled, pressing S will solve the current puzzle, click "New Game", select "Extreme" difficulty, and repeat until you press S again to stop.

<p align="right">(<a href="#Sudoku-Bot">back to top</a>)</p>

<!-- FEATURES -->
## Features

- **Persistent GUI** — small always-on-top window showing status. No more restarting between puzzles.
- **Speed slider** — drag to control how fast the bot fills in cells, from slow and visible to near-instant.
- **Auto Replay** — toggle on to farm puzzles back-to-back automatically. Solves, clicks New Game, selects Extreme, and repeats.
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
