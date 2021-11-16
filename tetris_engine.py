"""Tetris Game Engine for COMP16321 Coursework.

The module contains the Tetris Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""

# Imports
from csv import DictReader, DictWriter


class TetrisEngine:
    """An engine to run the classic Tetris Game.

    This class contains all the relevant code in order to have a functioning
    version of the tetris game. It provides an API to connect this engine to
    a GUI.

    Attributes:
        _debug:
            Debug mode shows output messages and logs to aid with debugging
        _game_options:
            A dictionary of game options.
            Current keys are next_queue, hold_queue and ghost_piece
        _leaderboard:
            The relative file path to the leaderboard file.
        _grid_tetrimino_map:
            A dictionary in order to map a Tetrimino to its relevant number
    """
    _grid_tetrimino_map = {
        "O": "1",
        "I": "2",
        "T": "3",
        "L": "4",
        "J": "5",
        "S": "6",
        "Z": "7"
    }

    def __init__(self, debug=False, scoreboard="leaderboard.csv"):
        """Initialise the Game Engine with the given options.

        Args:
            debug: Determines whether to run the engine in debug mode
        """
        if debug:
            print("DEBUG: Running TetrisEngine.__init__()")

        self._debug = debug
        self._leaderboard = scoreboard
        self.set_game_options()

    def create_grid(self):
        """Create the grid property containing information on the grid.

        Initialise a 20x10 2D array with the numbers representing the current
        state of the grid cell.

        0 means empty, the numbers 1-7 indicate what colour occupies the cell.
        The numbers 11-17 indicate that the cell has a ghost piece in it.

        Grid is referenced from the top left corner, y first then x.
        So grid position (9, 3) would indicate the 9th row from the top,
        3rd column from the left.
        """
        self.grid = [[0 for i in range(10)] for r in range(20)]
        if self._debug:
            print("DEBUG: Generated empty grid array")

    def update_grid_position(self, row, col, type, ghost=False):
        """Update a grid cell with a new Tetrimino or ghost piece.

        0 means empty, the numbers 1-7 indicate what colour occupies the cell.
        The numbers 11-17 indicate that the cell has a ghost piece in it.

        Grid is referenced from the top left corner, y first then x.
        So grid position (9, 3) would indicate the 9th row from the top,
        3rd column from the left.

        Args:
            row:
                The row number from the top of the grid
            col:
                The column number from the left of the grid
            type:
                The Tetrimino type (a single character)
            ghost:
                A boolean to determine if the grid contains a ghost piece
        """
        if ghost:
            self.grid[row][col] = self._grid_tetrimino_map[type] + 10
        else:
            self.grid[row][col] = self._grid_tetrimino_map[type]

        if self._debug:
            print(
                "DEBUG: Updated Grid Cell at row: ", row,
                ", col: ", col, " with value", self.grid[row][col],
                sep=" "
            )

    def set_game_options(self, next_queue=6, hold_on=True, ghost_piece=True):
        """Set the options for the game engine.

        Args:
            next_queue:
                How many Tetriminos to display in the next queue.
                Int 1-6
            hold_on:
                Sets whether the user is able to hold a Tetrimino or not
                Defaults to True
            ghost_piece:
                Whether to show the ghost piece
                Defaults to True
        """
        self._game_options = {
            "next_queue": next_queue,
            "hold_queue": hold_on,
            "ghost_piece": ghost_piece
        }
        if self._debug:
            print("DEBUG: Set Game Options to", self._game_options)

    def read_leaderboard(self):
        """Return the saved leaderboard.

        Read the leaderboard from the engine's leaderboard file and return it.

        Returns:
            A list of tuples. The first item being the player's initials,
            the second their score.
        """
        output_list = []
        with open(self._leaderboard, mode='r') as f:
            reader = DictReader(f)
            for row in reader:
                output_list.append((row["Initials"], int(row["Score"])))

        output_list.sort(key=lambda x: x[1])
        if self._debug:
            print("DEBUG: Leaderboard Generated: ", output_list)

        return output_list

    def add_to_leaderboard(self, initials, score):
        """Add an entry to the leaderboard.

        Writes a new row in the engine's leaderboard file with the given
        initials and score.

        Args:
            initials:
                A string containing the initials of the player
            score:
                An integer representing the player's score
        """
        with open(self._leaderboard, mode='a') as f:
            fieldnames = ["Initials", "Score"]
            writer = DictWriter(f, fieldnames=fieldnames)

            writer.writerow({"Initials": initials, "Score": score})

        if self._debug:
            print(
                "DEBUG:", initials, "with score", score,
                "added to leaderboard file", self._leaderboard
            )


if __name__ == "__main__":
    engine = TetrisEngine(debug=True)
    engine.create_grid()
