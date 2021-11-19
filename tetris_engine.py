"""Tetris Game Engine for COMP16321 Coursework.

The module contains the Tetris Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""

# Imports
from csv import DictReader, DictWriter
from datetime import datetime
from ast import literal_eval


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
            next_queue: How many of the next pieces to show. Integer 1-6
            hold_queue: Sets if the hold queue is turned on
            ghost_piece: Determines if the ghost piece is shown
            lock_down:
                The type of lock down setting to use.
                Values are "Extended", "Infinite" or "Classic"
                Refer to section 2.5.4 in the Tetris Guidlines for more info.
        _leaderboard:
            The relative file path to the leaderboard file.
        _grid_tetrimino_map:
            A dictionary in order to map a Tetrimino to its relevant number
        grid:
            The array containing the matrix of cells on the board
        next_queue:
            The next 6 pieces to be added to the board
        hold_queue:
            The piece currently in the hold queue
        current_piece:
            The piece currently controlled by the player
        stats:
            A dictionary of statistics for the game.
            score: The current score for the game
            lines: The number of lines the user has cleared so far
            level: The level the user is currently on
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
        self._game_options = None
        self._leaderboard = scoreboard
        self.grid = None
        self.next_queue = None
        self.hold_queue = None
        self.current_piece = None
        self.stats = {
            "score": 0,
            "lines": 0,
            "level": 0
        }

        # Set the game options to their default values
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

    def save_game(self):
        """Save the current game state to a file.

        This saves all the state variables to a file.
        """
        today = datetime.now()
        formatted_time = today.strftime("%Y-%m-%d %H:%M")
        file_name = formatted_time + ".txt"

        lines = [
            formatted_time,
            self.current_piece,
            self.hold_queue,
            str(self.next_queue),
            str(self.stats),
            str(self._game_options),
            str(self.grid)
        ]
        with open(file_name, mode='w') as f:
            f.write("\n".join(lines))

        if self._debug:
            print("DEBUG: Generated output for save. Written to", file_name)
            print(*lines, sep='\n')

    def load_game(self, filename):
        """Load a saved game from the given file.

        Args:
            filename: The file to read the saved game from
        """
        with open(filename, mode='r') as f:
            lines = f.readlines()

        self.current_piece = lines[1].strip()
        self.hold_queue = lines[2].strip()
        self.next_queue = literal_eval(lines[3].strip())
        self.stats = literal_eval(lines[4].strip())
        self._game_options = literal_eval(lines[5].strip())
        self.grid = literal_eval(lines[6].strip())

        if self._debug:
            print("DEBUG: Opened save file and retrieved stored data:")
            print(*lines)

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
            "ghost_piece": ghost_piece,
            "lock_down": "Extended"
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
