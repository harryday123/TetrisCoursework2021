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
        self.hold_queue_frame.pack()
        self.stats_frame.pack()
        self.matrix_frame.pack()
        self.next_queue_frame.pack()


class NextQueue(tk.Frame):
    """The frame to show the next queue."""

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.queue = []

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

    def update_matrix(self, matrix):
        """Update the matrix.

        Args:
            matrix: The updated grid
        """
        self.matrix = matrix


class HoldQueue(tk.Frame):
    """The frame to show the hold queue."""

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.queue = ""

    def update_queue(self, queue):
        """Update the queue.

        Args:
            queue: A character representing the hold piece.
        """
        self.queue = queue


class Stats(tk.Frame):
    """The frame to show the stats section."""

    def __init__(self, parent, *args, **kwargs):
        """Initialise the Frame."""
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.stats = {
            "score": 0,
            "lines": 0,
            "level": 0,
            "goal": 0
        }

    def update_stats(self, stats):
        """Update the stats shown.

        Args:
            stats: A dictionary representing the new stats to update
        """
        for key in stats:
            self.stats[key] = stats[key]


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1600x900")
    root.title("Line Clearing Game")

    LineClearApplication(LineClearEngine(), root).pack()
    root.mainloop()
