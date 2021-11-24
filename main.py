"""Harry Day (k14454hd) COMP16321 Coursework.

This coursework is an adaptation of the classic Tetris game written in Tkinter.
"""

# Imports
import tkinter as tk
from line_clear_engine import LineClearEngine


class LineClearApp(tk.Frame):
    """The main frame for the Tetris game.

    Contains all the relevant GUI for the tetris game.

    Attributes:
        parent: The parent of the frame (normally the root)
        engine: The TetrisEngine object to use to run the game
        _next_queue_frame: The Next Queue Frame
        _matrix_frame: The Matrix Frame
        _hold_queue_frame: The Hold Queue Frame
        _stats_frame: The Stats Frame
    """

    def __init__(self, engine, parent, debug=False, *args, **kwargs):
        """Initialise the LineClearApplication object.

        Initialises the class with a parent and any arguments
        that have been provided

        Args:
            parent: The parent to this frame (normally the root)
            *args: A variable length list of arguments
            **kwargs: A variable length dictionary of keyword arguments
        """
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.engine = engine

        self._debug = debug

        if self._debug:
            print("DEBUG - LineClearApp: Running __init__")

        # Subframes
        self._next_queue_frame = NextQueue(self, debug=debug, *args, **kwargs)
        self._matrix_frame = Matrix(self, debug=debug, *args, **kwargs)
        self._hold_queue_frame = HoldQueue(self, debug=debug, *args, **kwargs)
        self._stats_frame = Stats(self, debug=debug, *args, **kwargs)
        self._menu_frame = Menu(self, debug=debug, *args, **kwargs)

        # Place Subframes
        self._hold_queue_frame.grid(column=1, row=1)
        self._stats_frame.grid(column=1, row=2)
        self._matrix_frame.grid(column=2, row=1, rowspan=2)
        self._menu_frame.grid(column=2, row=1, rowspan=2)
        self._next_queue_frame.grid(column=3, row=1, rowspan=2)

    def update_ui_panels(self):
        """Mass update all UI panels with one function."""
        if self._debug:
            print("DEBUG - LineClearApp: Update All UI Panels")
        self._matrix_frame.update_grid(self.engine.grid)
        self._hold_queue_frame.update_queue(self.engine.hold_queue)
        self._next_queue_frame.update_queue(self.engine.next_queue)
        self._stats_frame.update_stats(self.engine.stats)

    def _main_run_loop(self):
        # If the game is over
        if not self.engine.game_running and not self.engine.game_paused:
            self._game_over()
            return

        if self._debug:
            print("DEBUG - LineClearApp: Main Loop Ran")
        if self.engine.game_running and not self.engine.game_paused:
            # Running and not paused
            self.engine.falling_phase()
            self.update_ui_panels()

        self.parent.after(self.engine.fallspeed, self._main_run_loop)

    def start_game(self):
        """Begin the game."""
        if self._debug:
            print("DEBUG - LineClearApp: Start the game")

        self._menu_frame.grid_remove()
        self.engine.start_game(from_save=True)
        self._main_run_loop()

    def load_game(self):
        """Load a game from a save."""
        if self._debug:
            print("DEBUG - LineClearApp: Load a game from save")
        self.engine.load_game("./saves/2021-11-24 17:19.txt")
        self.start_game()

    def _game_over(self):
        """Show the game over screen."""
        self._menu_frame.grid(column=2, row=1, rowspan=2)
        self._menu_frame.game_over_buttons()

    def play_again(self):
        """Reset the game to play again."""
        self.engine.reset_state()
        self.update_ui_panels()

    def toggle_pause_game(self):
        """Pause the game."""
        if self._debug:
            print("DEBUG - LineClearApp: Toggle Pause Game")

        self.engine.toggle_pause_game()
        if self.engine.game_paused:
            self._menu_frame.pause_buttons()
            self._menu_frame.grid(column=2, row=1, rowspan=2)
        else:
            self._matrix_frame.canvas.focus_set()
            self._menu_frame.grid_remove()
            self._matrix_frame._update_matrix(None)

    def save_game(self):
        """Save the current game state and exit."""
        self.engine.save_game()
        self.play_again()


class NextQueue(tk.Frame):
    """The frame to show the next queue.

    Attributes:
        _piece_file_map: A dictionary to map a piece to its image file
        parent: The parent of the Frame
        queue_images: A list of PhotoImages in the queue
        queue_images_lbls: A list containing the labels displaying the queue
    """

    _piece_file_map = {
        "O": "./assets/images/skinny/O-Piece.png",
        "I": "./assets/images/skinny/I-Piece.png",
        "T": "./assets/images/skinny/T-Piece.png",
        "L": "./assets/images/skinny/L-Piece.png",
        "J": "./assets/images/skinny/J-Piece.png",
        "S": "./assets/images/skinny/S-Piece.png",
        "Z": "./assets/images/skinny/Z-Piece.png"
    }

    def __init__(self, parent, debug=False, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=800, width=200)

        self._debug = debug

        if self._debug:
            print("DEBUG - NextQueue: Running __init__")

        # Set up the queue images initially
        self.queue_images = [None] * 6
        self.queue_images_lbls = [
            tk.Label(
                self,
                image=image,
                bg="#616161"
            ) for image in self.queue_images
        ]

        for image in self.queue_images_lbls:
            image.pack(pady=27)

    def update_queue(self, queue):
        """Update the queue.

        Args:
            queue: A list of characters representing the next pieces.
        """
        if queue is None:
            return

        if self._debug:
            print("DEBUG - NextQueue: Updating Queue")

        # Create new PhotoImages
        self.queue_images = [
            tk.PhotoImage(file=self._piece_file_map[type]) for type in queue
        ]

        # Update Each Label
        for i in range(len(self.queue_images_lbls)):
            self.queue_images_lbls[i].configure(image=self.queue_images[i])
            self.queue_images_lbls[i].image = self.queue_images[i]

        if self._debug:
            print("DEBUG - NextQueue: Queue Updated")


class Matrix(tk.Frame):
    """The frame to show the matrix.

    Attributes:
        parent: The parent of the Frame
        current_grid: The current state of the grid
        matrix:
            Holds the shapes in the grid.
            Canvas origin is top left, therefore the matrix's first list is
            actually the last list in the engine. The first list draws the top
            row.
        key_history: Holds the currently pressed keys
        canvas: The canvas widget that the matrix is drawn on
    """

    _keybind_map = {
        "Left": "mv_left",
        "Right": "mv_right",
        "x": "rt_clock",
        "z": "rt_anti",
        "Down": "softdrop",
        "space": "harddrop",
        "c": "hold",
        "Escape": "pause"
    }

    def __init__(self, parent, debug=False, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=800, width=400)

        self._debug = debug

        if self._debug:
            print("DEBUG - Matrix: Running __init__")

        self.current_grid = [[0 for i in range(10)] for r in range(22)]
        self.canvas = tk.Canvas(self, height=800, width=400)
        self.matrix = []
        self.key_history = []
        self._create_empty_matrix()
        self._init_keybinds()

        self.canvas.pack()

    def _init_keybinds(self):
        self.canvas.bind("<Escape>", self._toggle_pause)
        self.canvas.bind("<KeyPress>", self._key_press)
        self.canvas.bind("<KeyRelease>", self._key_release)
        self.canvas.focus_set()

    def _key_press(self, event):
        """Handle a key press from the user.

        Args:
            event: The KeyPress event from the canvas
        """
        if event.keysym not in self.key_history:
            self.key_history.append(event.keysym)

            self._perform_actions_pressed()

    def _key_release(self, event):
        """Handle a key release from the user.

        Args:
            event: The KeyPress event from the canvas
        """
        if event.keysym in self.key_history:
            self.key_history.pop(self.key_history.index(event.keysym))

            self._perform_actions_pressed()

    def _perform_actions_pressed(self):
        """Perform the actions represented by the keys in key_history."""
        for key in self.key_history:
            if key in list(self._keybind_map.keys()):
                action = self._keybind_map[key]
                if self._debug:
                    print("DEBUG - Matrix: Action Performed:", action)
                if action == "mv_left":
                    self.parent.engine.move_current_piece(direction="L")
                elif action == "mv_right":
                    self.parent.engine.move_current_piece(direction="R")
                elif action == "rt_clock":
                    self.parent.engine.move_current_piece(direction="C")
                elif action == "rt_anti":
                    self.parent.engine.move_current_piece(direction="A")
                elif action == "softdrop":
                    self.parent.engine.move_current_piece(direction="D")
                elif action == "harddrop":
                    self.parent.engine.hard_drop()
                elif action == "hold":
                    self.parent.engine.hold_swap()

                self.parent.update_ui_panels()

            else:
                return

    def _toggle_pause(self, event):
        """Toggle the pause of the game."""
        if self._debug:
            print("DEBUG - Matrix: Action Performed: pause")
        self.parent.toggle_pause_game()

    def _create_empty_matrix(self):
        """Create a matrix filled with black squares."""
        self.matrix = []
        for row_num in range(20):
            row = []
            for col_num in range(10):
                row.append(
                    self.canvas.create_rectangle(
                        # First row is the top left of the square
                        col_num * 40, row_num * 40,
                        # Second row is just outside the bottom left of the
                        # square hence the +1 after the multiplication
                        ((col_num + 1) * 40) + 1, ((row_num + 1) * 40) + 1,
                        fill="black"
                    )
                )
            self.matrix.append(row)

        if self._debug:
            print("DEBUG - Matrix: Empty Matrix Created")

    def _update_matrix_cell(self, type, row, col):
        """Update the colour of a single cell in the Matrix.

        Args:
            type: The type of piece now in the cell
            row: The row number of the cell (tkinter origin)
            col: The column number of the cell (tkinter origin)
        """
        _grid_piece_colour_map = {
            0: "black",
            1: "yellow",
            2: "#40bbe3",
            3: "magenta",
            4: "#ff8000",
            5: "blue",
            6: "green",
            7: "red"
        }
        self.canvas.itemconfig(
            self.matrix[row][col],
            fill=_grid_piece_colour_map[type]
        )

        if self._debug:
            print(
                "DEBUG - Matrix: Matrix Cell at row", row,
                "and col", col,
                "updated to colour", _grid_piece_colour_map[type]
            )

    def _update_matrix(self, changes):
        """Redraw the matrix with the current grid.

        Attributes:
            changes: A list of tuples containing the coords of changed cells

        Important:
            The coordinates for the input should be relative to the grid.
            So the origin for those coordinates should be 2 rows higher than
            the origin of the matrix (2 rows above the matrix are for
            generation)
        """
        if self._debug:
            print("DEBUG - Matrix: Updating Matrix")

        if changes is not None:
            for (col, row) in changes:
                new_value = self.current_grid[row][col]
                self._update_matrix_cell(new_value, row - 2, col)
        else:
            for row in range(2, 22):
                for col in range(10):
                    new_value = self.current_grid[row][col]
                    self._update_matrix_cell(new_value, row - 2, col)

    def update_grid(self, grid):
        """Update the grid.

        Args:
            grid: The updated grid
        """
        if self._debug:
            print("DEBUG - Matrix: Updating Grid")

        grid = list(reversed([row[:] for row in grid]))

        changes = []
        # Searching in rows 2-21 as first two rows are off the top of the grid
        for row in range(2, 22):
            i = 0
            for (n, m) in zip(self.current_grid[row], grid[row]):
                if n != m:
                    changes.append((i, row))
                i += 1

        if self._debug:
            print("DEBUG - Matrix: Grid found", len(changes), "changes")

        self.current_grid = grid
        self._update_matrix(changes)


class HoldQueue(tk.Frame):
    """The frame to show the hold queue.

    Attributs:
        _piece_file_map: A dictionary to map a piece to its image file
        parent: The parent of this Frame
        piece_image = The PhotoImage for the hold queue label
        piece_lbl: The Label displaying the image
    """

    _piece_file_map = {
        "O": "./assets/images/O-Piece.png",
        "I": "./assets/images/I-Piece.png",
        "T": "./assets/images/T-Piece.png",
        "L": "./assets/images/L-Piece.png",
        "J": "./assets/images/J-Piece.png",
        "S": "./assets/images/S-Piece.png",
        "Z": "./assets/images/Z-Piece.png"
    }

    def __init__(self, parent, debug=False, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=200, width=200)

        self._debug = debug

        if self._debug:
            print("DEBUG - HoldQueue: Running __init__")

        self.piece_image = None
        self.piece_lbl = tk.Label(self, image=self.piece_image, bg="#616161")
        self.piece_lbl.pack()

    def update_queue(self, queue):
        """Update the queue.

        Args:
            queue: A character representing the hold piece.
        """
        if queue is None:
            return

        if self._debug:
            print("DEBUG - HoldQueue: Updating Hold Queue")

        newimg = tk.PhotoImage(file=self._piece_file_map[queue])
        self.piece_lbl.configure(image=newimg)
        self.piece_lbl.image = newimg


class Stats(tk.Frame):
    """The frame to show the stats section.

    Attributes:
        parent: The parent of the Frame
        score: The current score
        lines: The number of lines the player has cleared
        level: The current level
        goal: The number of lines needed to clear to level up
        score_lbl: The Label containing the score
        lines_lbl: The Label containing the lines
        level_lbl: The Label containing the level
        goal_lbl: The Label containing the goal
    """

    def __init__(self, parent, debug=False, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self._debug = debug

        if self._debug:
            print("DEBUG - Stats: Running __init__")

        self.score = tk.StringVar(self, value="0")
        self.lines = tk.StringVar(self, value="0")
        self.level = tk.StringVar(self, value="0")
        self.goal = tk.StringVar(self, value="0")

        self.configure(height=600, width=200)
        self._init_labels()

    def _init_labels(self):
        """Initialise the stats labels."""
        tk.Label(self, text="Score:", bg="#616161").pack()
        self.score_lbl = tk.Label(self, textvariable=self.score, bg="#616161")
        self.score_lbl.pack()

        tk.Label(self, text="Lines Cleared:", bg="#616161").pack()
        self.lines_lbl = tk.Label(self, textvariable=self.lines, bg="#616161")
        self.lines_lbl.pack()

        tk.Label(self, text="Level:", bg="#616161").pack()
        self.level_lbl = tk.Label(self, textvariable=self.level, bg="#616161")
        self.level_lbl.pack()

        tk.Label(self, text="Goal:", bg="#616161").pack()
        self.goal_lbl = tk.Label(self, textvariable=self.goal, bg="#616161")
        self.goal_lbl.pack()

    def update_stats(self, stats):
        """Update the stats shown.

        Args:
            stats: A dictionary representing the new stats to update
        """
        if self._debug:
            print("DEBUG - Stats: Updating Stats")

        self.score.set(str(stats["score"]))
        self.lines.set(str(stats["lines"]))
        self.level.set(str(stats["level"]))
        self.goal.set(str(stats["goal"]))


class Menu(tk.Frame):
    """The frame to show the menu above the canvas.

    Attributes:
        parent: The parent of the frame
        _debug: Determines whether to show the debug output
        _start_button: The start game button
        _load_game_button: The load game button
        _game_over_lbl:
        _play_again_btn:
        _pause_lbl:
        _continue_btn:
    """

    def __init__(self, parent, debug=False, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=800, width=400)

        self._init_buttons_()

        self._debug = debug

        if self._debug:
            print("DEBUG - Menu: Running __init__")

        self.start_screen_buttons()

    def _init_buttons_(self):
        """Initialise the buttons on the menu."""
        self._start_btn = tk.Button(
            self,
            text="Start Game",
            command=self._start_game
        )
        self._load_game_btn = tk.Button(
            self,
            text="Load Game",
            command=self._load_game
        )
        self._game_over_lbl = tk.Label(self, text="Game Over")
        self._play_again_btn = tk.Button(
            self,
            text="Play Again",
            command=self._play_again
        )
        self._pause_lbl = tk.Label(self, text="Game Paused")
        self._save_and_exit_btn = tk.Button(
            self,
            text="Save and Exit",
            command=self._save_and_exit
        )
        self._continue_btn = tk.Button(
            self,
            text="Continue",
            command=self._continue_game
        )

    def start_screen_buttons(self):
        """Show the start screen buttons."""
        self.unpack_all()
        self._start_btn.pack()
        self._load_game_btn.pack()
        self.focus_set()

    def game_over_buttons(self):
        """Configure the menu for a game over screen."""
        # Unload the start game buttons
        self.unpack_all()

        # TODO: Add scoreboard options here

        self._game_over_lbl.pack()
        self._play_again_btn.pack()
        self.focus_set()

    def pause_buttons(self):
        """Configure the menu for a pause screen."""
        # Unload the buttons
        self.unpack_all()

        self._pause_lbl.pack()
        self._save_and_exit_btn.pack()
        self._continue_btn.pack()
        self.focus_set()

    def _start_game(self):
        """Run the command to start the game."""
        self.parent.start_game()

    def _load_game(self):
        """Run the command to load a game from a save."""
        self.parent.load_game()

    def _save_and_exit(self):
        """Save and Exit the Game."""
        if self._debug:
            print("DEBUG - Menu: Save and Exit Button Pressed")
        self.parent.save_game()

    def _play_again(self):
        """Run the command to start the game."""
        self.parent.play_again()

        self._game_over_lbl.pack_forget()
        self._play_again_btn.pack_forget()

        self._init_buttons_()

    def _continue_game(self):
        """Continue Playing the game."""
        self.parent.toggle_pause_game()

    def unpack_all(self):
        """Unpack all the currently showing buttons."""
        self._start_btn.pack_forget()
        self._load_game_btn.pack_forget()
        self._game_over_lbl.pack_forget()
        self._play_again_btn.pack_forget()
        self._pause_lbl.pack_forget()
        self._continue_btn.pack_forget()
        self._save_and_exit_btn.pack_forget()


if __name__ == "__main__":
    # Initialise Window
    root = tk.Tk()
    root.geometry("1600x900")
    root.title("Line Clearing Game")
    root.configure(bg="#616161")

    LineClearApp(
        LineClearEngine(debug=True),
        root,
        bg="#616161",
        debug=True
    ).pack()
    root.mainloop()
