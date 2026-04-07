# Install Requirements
# pip install -r requirements.txt

import os
import numpy as np
from PIL import Image
import pyautogui
import keyboard
import time
import threading
import tkinter as tk

import readBoard
import sudoku
import solver_fast

# Directory where reference images live
REF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "references")

# Reference images for button detection (multiple variants for reliability)
NEW_GAME_REFS = [
    os.path.join(REF_DIR, f) for f in [
        "new_game_btn.png", "new_game_btn_1.png",
        "new_game_btn_2.png", "new_game_btn_3.png"
    ]
]
EXTREME_REFS = [
    os.path.join(REF_DIR, f) for f in [
        "extreme_btn.png", "extreme_btn_1.png", "extreme_btn_2.png"
    ]
]


def locate_and_click(ref_paths, confidence=0.9, retries=10, delay=0.5, pick_lowest=False):
    """Try to find and click a button using multiple reference images.
    If pick_lowest=True, find ALL matches and click the one lowest on screen.
    """
    for attempt in range(retries):
        best = None  # (x, y) with highest y value
        for ref in ref_paths:
            if not os.path.exists(ref):
                continue
            try:
                if pick_lowest:
                    matches = list(pyautogui.locateAllOnScreen(ref, confidence=confidence))
                    for match in matches:
                        center = pyautogui.center(match)
                        if best is None or center.y > best.y:
                            best = center
                else:
                    loc = pyautogui.locateCenterOnScreen(ref, confidence=confidence)
                    if loc:
                        pyautogui.click(loc)
                        return True
            except pyautogui.ImageNotFoundException:
                continue
        if best:
            pyautogui.click(best)
            return True
        time.sleep(delay)
    return False


class SudokuBotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sudoku Bot")
        self.root.geometry("320x270")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.status_label = tk.Label(
            self.root, text="Ready", font=("Consolas", 14, "bold"),
            fg="#22c55e", bg="#1e1e1e"
        )
        self.status_label.pack(fill=tk.BOTH, expand=True)

        # Speed slider frame
        slider_frame = tk.Frame(self.root, bg="#1e1e1e")
        slider_frame.pack(fill=tk.X, padx=16, pady=(0, 4))

        tk.Label(
            slider_frame, text="Speed", font=("Consolas", 9),
            fg="#888888", bg="#1e1e1e"
        ).pack(side=tk.LEFT)

        self.speed_var = tk.IntVar(value=90)
        self.speed_slider = tk.Scale(
            slider_frame, from_=1, to=100, orient=tk.HORIZONTAL,
            variable=self.speed_var, showvalue=False,
            bg="#1e1e1e", fg="#888888", troughcolor="#333333",
            highlightthickness=0, sliderrelief=tk.FLAT,
            activebackground="#3b82f6"
        )
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))

        self.speed_label = tk.Label(
            slider_frame, text="90%", font=("Consolas", 9),
            fg="#888888", bg="#1e1e1e", width=4
        )
        self.speed_label.pack(side=tk.RIGHT)
        self.speed_var.trace_add("write", self._update_speed_label)

        # Auto Replay toggle
        toggle_frame = tk.Frame(self.root, bg="#1e1e1e")
        toggle_frame.pack(fill=tk.X, padx=16, pady=(0, 4))

        tk.Label(
            toggle_frame, text="Auto Replay", font=("Consolas", 9),
            fg="#888888", bg="#1e1e1e"
        ).pack(side=tk.LEFT)

        self.auto_replay_var = tk.BooleanVar(value=False)
        self.auto_replay_cb = tk.Checkbutton(
            toggle_frame, variable=self.auto_replay_var,
            bg="#1e1e1e", activebackground="#1e1e1e",
            selectcolor="#333333", relief=tk.FLAT,
            command=self._on_toggle_auto_replay
        )
        self.auto_replay_cb.pack(side=tk.LEFT, padx=(8, 0))

        self.auto_replay_label = tk.Label(
            toggle_frame, text="OFF", font=("Consolas", 9, "bold"),
            fg="#ef4444", bg="#1e1e1e"
        )
        self.auto_replay_label.pack(side=tk.LEFT, padx=(4, 0))

        self.info_label = tk.Label(
            self.root, text="Press S to solve  |  Press Q to quit",
            font=("Consolas", 10), fg="#888888", bg="#1e1e1e"
        )
        self.info_label.pack(side=tk.BOTTOM, pady=8)

        self.root.configure(bg="#1e1e1e")

        self.solving = False
        self.running = False  # True while auto-loop is active

        # Load CNN model once at startup
        self.set_status("Loading model...", "#f59e0b")
        self.root.update()
        self.model = readBoard.loadModel()
        self.set_status("Ready  -  Press S", "#22c55e")

        # Register global hotkeys
        keyboard.on_press_key("s", self.on_s_pressed)
        keyboard.on_press_key("q", self.on_q_pressed)

        # Default pyautogui speed (overridden per-solve by slider)
        pyautogui.PAUSE = 0.01

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def _update_speed_label(self, *args):
        self.speed_label.config(text=f"{self.speed_var.get()}%")

    def _on_toggle_auto_replay(self):
        if self.auto_replay_var.get():
            self.auto_replay_label.config(text="ON", fg="#22c55e")
        else:
            self.auto_replay_label.config(text="OFF", fg="#ef4444")
            # If currently looping, signal stop
            if self.running:
                self.running = False

    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.update_idletasks()

    def on_s_pressed(self, event=None):
        if self.running:
            # Stop the auto-loop
            self.running = False
            self.root.after(0, lambda: self.set_status("Stopping...", "#f59e0b"))
            return
        if self.solving:
            return
        self.solving = True

        if self.auto_replay_var.get():
            self.running = True
            thread = threading.Thread(target=self.run_loop, daemon=True)
        else:
            thread = threading.Thread(target=self.run_single, daemon=True)
        thread.start()

    def on_q_pressed(self, event=None):
        self.running = False
        self.on_close()

    def on_close(self):
        self.running = False
        keyboard.unhook_all()
        self.root.destroy()

    def run_single(self):
        """Solve once then stop."""
        try:
            success = self.run_solver()
            if not success:
                self.root.after(0, lambda: self.set_status("Ready  -  Press S", "#22c55e"))
        finally:
            self.solving = False

    def run_loop(self):
        """Auto-loop: solve -> New Game -> Extreme -> wait -> repeat."""
        solve_count = 0
        try:
            while self.running:
                success = self.run_solver()

                if not success or not self.running:
                    break

                solve_count += 1

                # Click "New Game"
                self.root.after(0, lambda: self.set_status("Clicking New Game...", "#a855f7"))
                pyautogui.PAUSE = 0.01
                time.sleep(1)

                if not locate_and_click(NEW_GAME_REFS, confidence=0.9):
                    self.root.after(0, lambda: self.set_status("Can't find New Game!", "#ef4444"))
                    break

                if not self.running:
                    break

                # Click "Extreme"
                self.root.after(0, lambda: self.set_status("Clicking Extreme...", "#a855f7"))
                time.sleep(0.5)

                if not locate_and_click(EXTREME_REFS, confidence=0.9, pick_lowest=True):
                    self.root.after(0, lambda: self.set_status("Can't find Extreme!", "#ef4444"))
                    break

                if not self.running:
                    break

                # Wait for the new puzzle to load
                self.root.after(0, lambda: self.set_status("Waiting for puzzle...", "#f59e0b"))
                time.sleep(4)

        except Exception as e:
            print(f"Loop error: {e}")
            self.root.after(0, lambda: self.set_status("Error!", "#ef4444"))
        finally:
            self.running = False
            self.solving = False
            n = solve_count
            self.root.after(0, lambda: self.set_status(
                f"Stopped ({n} solved)  -  Press S", "#22c55e"
            ))

    def run_solver(self):
        """Run a single solve. Returns True if solved successfully."""
        try:
            self.root.after(0, lambda: self.set_status("Solving...", "#f59e0b"))

            start_time = time.time()

            img = pyautogui.screenshot()
            imgNA, thresh = readBoard.loadImage(img)
            boardContour = readBoard.findBoard(thresh)

            if boardContour is None:
                self.root.after(0, lambda: self.set_status("No board found!", "#ef4444"))
                return False

            pts = boardContour.reshape(4, 2)
            boardCorner = (int(pts[0, 0]), int(pts[0, 1]))

            width = int(np.linalg.norm(pts[3, 0] - pts[0, 0]))
            height = int(np.linalg.norm(pts[2, 1] - pts[0, 1]))
            cellSize = int(((width / 9) + (height / 9)) / 2)

            boardImg = readBoard.warpBoard(imgNA, boardContour)
            cells = readBoard.splitCells(boardImg)
            processedCells = readBoard.preprocessCells(cells)

            board = readBoard.readBoard(self.model, processedCells)

            read_time = time.time()

            board = sudoku.refactorBoard(board)
            print(f"\nBoard: {board}")

            solvedBoard, solvedEmpties = solver_fast.solve(board)

            solve_time = time.time()
            print(f"\nSolved Board: {solvedBoard}")

            isSolved = all(all(cell != 0 for cell in row) for row in solvedBoard)
            if isSolved:
                self.root.after(0, lambda: self.set_status("Filling board...", "#3b82f6"))
                speed = self.speed_var.get()
                pyautogui.PAUSE = 0.15 - (speed - 1) * (0.145 / 99)
                sudoku.FillBoard(solvedEmpties, boardCorner, cellSize)

            end_time = time.time()

            print(f"\nRead Board: {read_time - start_time:.3f}s")
            print(f"Solve:      {solve_time - read_time:.3f}s")
            print(f"Total:      {end_time - start_time:.3f}s")

            if isSolved:
                msg = f"Solved in {end_time - start_time:.2f}s"
                self.root.after(0, lambda: self.set_status(msg, "#22c55e"))
                return True
            else:
                self.root.after(0, lambda: self.set_status("Could not solve!", "#ef4444"))
                return False

        except Exception as e:
            print(f"Error: {e}")
            self.root.after(0, lambda: self.set_status("Error!", "#ef4444"))
            return False


if __name__ == "__main__":
    SudokuBotGUI()
