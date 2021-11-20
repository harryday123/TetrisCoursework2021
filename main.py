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
        self.next_queue_frame = NextQueue(self, *args, **kwargs)
        self.matrix_frame = Matrix(self, *args, **kwargs)
        self.hold_queue_frame = HoldQueue(self, *args, **kwargs)
        self.stats_frame = Stats(self, *args, **kwargs)

        # Place Subframes
        self.hold_queue_frame.grid(column=1, row=1)
        self.stats_frame.grid(column=1, row=2)
        self.matrix_frame.grid(column=2, row=1, rowspan=2)
        self.next_queue_frame.grid(column=3, row=1, rowspan=2)


class NextQueue(tk.Frame):
    """The frame to show the next queue."""

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.queue = []
        self.configure(height=800, width=200, bg="red")

    def update_queue(self, queue):
        """Update the queue.

        Args:
            queue: A list of characters representing the next pieces.
        """
        self.queue = queue


class Matrix(tk.Frame):
    """The frame to show the matrix."""

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.matrix = [[0 for i in range(10)] for r in range(22)]
        self.configure(height=800, width=400, bg="blue")

    def update_matrix(self, matrix):
        """Update the matrix.

        Args:
            matrix: The updated grid
        """
        self.matrix = matrix


class HoldQueue(tk.Frame):
    """The frame to show the hold queue.

    Attributs:
        parent: The parent of this Frame
        piece_image = The PhotoImage for the hold queue label
        piece_Lbl: The Label displaying the image
    """

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        self.parent = parent
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.configure(height=200, width=200)

        self.piece_image = tk.PhotoImage(file="./assets/images/O-Piece.png")
        self.piece_Lbl = tk.Label(self, image=self.piece_image, bg="#616161")
        self.piece_Lbl.pack()

    def update_queue(self, queue):
        """Update the queue.

        Args:
            queue: A character representing the hold piece.
        """
        file_name = "./assets/images/" + queue + "-Piece.png"
        newimg = tk.PhotoImage(file=file_name)
        self.piece_Lbl.configure(image=newimg)
        self.piece_Lbl.image = newimg


class Stats(tk.Frame):
    """The frame to show the stats section."""

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
