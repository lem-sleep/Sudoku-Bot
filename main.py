# Install Requirements
# pip install -r requirements.txt

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


class SudokuBotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sudoku Bot")
        self.root.geometry("320x240")
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

        self.info_label = tk.Label(
            self.root, text="Press S to solve  |  Press Q to quit",
            font=("Consolas", 10), fg="#888888", bg="#1e1e1e"
        )
        self.info_label.pack(side=tk.BOTTOM, pady=8)

        self.root.configure(bg="#1e1e1e")

        self.solving = False

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

    def set_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.update_idletasks()

    def on_s_pressed(self, event=None):
        if self.solving:
            return
        self.solving = True
        thread = threading.Thread(target=self.run_solver, daemon=True)
        thread.start()

    def on_q_pressed(self, event=None):
        self.on_close()

    def on_close(self):
        keyboard.unhook_all()
        self.root.destroy()

    def run_solver(self):
        try:
            self.root.after(0, lambda: self.set_status("Solving...", "#f59e0b"))

            start_time = time.time()

            img = pyautogui.screenshot()
            imgNA, thresh = readBoard.loadImage(img)
            boardContour = readBoard.findBoard(thresh)

            if boardContour is None:
                self.root.after(0, lambda: self.set_status("No board found!", "#ef4444"))
                self.solving = False
                return

            pts = boardContour.reshape(4, 2)
            boardCorner = (int(pts[0, 0]), int(pts[0, 1]))

            width = int(np.linalg.norm(pts[3, 0] - pts[0, 0]))
            height = int(np.linalg.norm(pts[2, 1] - pts[0, 1]))
            cellSize = int(((width / 9) + (height / 9)) / 2)

            boardImg = readBoard.warpBoard(imgNA, boardContour)
            cells = readBoard.splitCells(boardImg)
            processedCells = readBoard.preprocessCells(cells)

            # Reuse pre-loaded model
            board = readBoard.readBoard(self.model, processedCells)

            read_time = time.time()

            board = sudoku.refactorBoard(board)
            print(f"\nBoard: {board}")

            # Use the fast solver
            solvedBoard, solvedEmpties = solver_fast.solve(board)

            solve_time = time.time()
            print(f"\nSolved Board: {solvedBoard}")

            isSolved = all(all(cell != 0 for cell in row) for row in solvedBoard)
            if isSolved:
                self.root.after(0, lambda: self.set_status("Filling board...", "#3b82f6"))
                # Map slider (1-100) to pause: 1%=0.15s (slow), 100%=0.005s (instant)
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
            else:
                self.root.after(0, lambda: self.set_status("Could not solve!", "#ef4444"))

        except Exception as e:
            print(f"Error: {e}")
            self.root.after(0, lambda: self.set_status("Error!", "#ef4444"))
        finally:
            self.solving = False


if __name__ == "__main__":
    SudokuBotGUI()
