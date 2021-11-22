"""Harry Day (k14454hd) COMP16321 Coursework.

This coursework is an adaptation of the classic Tetris game written in Tkinter.
"""

# Imports
import tkinter as tk
from line_clear_engine import LineClearEngine


class LineClearApplication(tk.Frame):
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

    def __init__(self, engine, parent, *args, **kwargs):
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
        # Subframes
        self._next_queue_frame = NextQueue(self, *args, **kwargs)
        self._matrix_frame = Matrix(self, *args, **kwargs)
        self._hold_queue_frame = HoldQueue(self, *args, **kwargs)
        self._stats_frame = Stats(self, *args, **kwargs)

        # Place Subframes
        self._hold_queue_frame.grid(column=1, row=1)
        self._stats_frame.grid(column=1, row=2)
        self._matrix_frame.grid(column=2, row=1, rowspan=2)
        self._next_queue_frame.grid(column=3, row=1, rowspan=2)


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

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=800, width=200)

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
        # Create new PhotoImages
        self.queue_images = [
            tk.PhotoImage(file=self._piece_file_map[type]) for type in queue
        ]

        # Update Each Label
        for i in range(len(self.queue_images_lbls)):
            self.queue_images_lbls[i].configure(image=self.queue_images[i])
            self.queue_images_lbls[i].image = self.queue_images[i]


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
        canvas: The canvas widget that the matrix is drawn on
    """

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=800, width=400)

        self.current_grid = [[0 for i in range(10)] for r in range(22)]
        self.canvas = tk.Canvas(self, height=800, width=400)
        self.matrix = []
        self._create_empty_matrix()
        self.canvas.pack()

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

    def _update_matrix_cell(self, type, row, col):
        """Update the colour of a single cell in the Matrix.

        Args:
            type: The type of piece now in the cell
            row: The row number of the cell (tkinter origin)
            col: The column number of the cell (tkinter origin)
        """
        _grid_piece_colour_map = {
            "1": "yellow",
            "2": "#40bbe3",
            "3": "magenta",
            "4": "ff8000",
            "5": "blue",
            "6": "green",
            "7": "red"
        }
        self.canvas.itemconfig(
            self.matrix[row][col],
            fill=_grid_piece_colour_map[type]
        )

    def _update_matrix(self, changes):
        """Redraw the matrix with the current grid.

        Attributes:
            changes: A list of tuples containing the coords of changed cells
        """
        for (col, row) in changes:
            new_value = str(self.current_grid[row][col])
            self._update_matrix_cell(new_value, row, col)

    def update_grid(self, grid):
        """Update the grid.

        Args:
            grid: The updated grid
        """
        changes = []
        for row in range(20):
            i = 0
            for (n, m) in zip(self.current_grid[row], grid[row]):
                if n != m:
                    changes.append((i, row))
                i += 1

        self.current_grid = list(reversed(grid))
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

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=200, width=200)

        self.piece_image = None
        self.piece_lbl = tk.Label(self, image=self.piece_image, bg="#616161")
        self.piece_lbl.pack()

    def update_queue(self, queue):
        """Update the queue.

        Args:
            queue: A character representing the hold piece.
        """
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

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.score = tk.StringVar(self, value="0")
        self.lines = tk.StringVar(self, value="0")
        self.level = tk.StringVar(self, value="0")
        self.goal = tk.StringVar(self, value="0")

        self.configure(height=600, width=200)

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

    def update_stats(self, score, lines, level, goal):
        """Update the stats shown.

        Args:
            stats: A dictionary representing the new stats to update
        """
        self.score.set(str(score))
        self.lines.set(str(lines))
        self.level.set(str(level))
        self.goal.set(str(goal))


if __name__ == "__main__":
    # Initialise Window
    root = tk.Tk()
    root.geometry("1600x900")
    root.title("Line Clearing Game")
    root.configure(bg="#616161")

    # Create Canvas
    # canvas = tk.Canvas(root, bg="gray", width=1600, height=900)
    # canvas.pack()

    LineClearApplication(LineClearEngine(), root, bg="#616161").pack()
    root.mainloop()
