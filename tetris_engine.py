"""Tetris Game Engine for COMP16321 Coursework.

The module contains the Tetris Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""

# Imports
from csv import DictReader, DictWriter
from datetime import datetime
from ast import literal_eval
from random import randint


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
            A dictionary describing the piece controlled by the player.
            Tetrimino blocks are numbered top to bottom, left to right in the
            North facing orientation.
            type: The type of Tetrimino
            facing: Which direction the piece is facing. ('N', 'E', 'S' or 'W')
            block1: The coordinates for block 1
            block2: The coordinates for block 2
            block3: The coordinates for block 3
            block4: The coordinates for block 4

        stats:
            A dictionary of statistics for the game.
            score: The current score for the game
            lines: The number of lines the user has cleared so far
            level: The level the user is currently on
        game_running:
            Shows whether the game is currently in progress
        _bag:
            The bag to generate Tetriminos from
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
        self.current_piece = {
            "type": "",
            "facing": "",
            "block1": (0, 0),
            "block2": (0, 0),
            "block3": (0, 0),
            "block4": (0, 0)
        }
        self.stats = {
            "score": 0,
            "lines": 0,
            "level": 0
        }
        self.game_running = False
        self._bag = []

        # Set the game options to their default values
        self.set_game_options()

    def _create_grid(self):
        """Create the grid property containing information on the grid.

        Initialise a 20x10 2D array with the numbers representing the current
        state of the grid cell.

        0 means empty, the numbers 1-7 indicate what colour occupies the cell.
        The numbers 11-17 indicate that the cell has a ghost piece in it.

        Origin is bottom left corner. Y coordinate first then X.
        So Grid[4][7] is the 4th row high and 7th column from the left.
        """
        self.grid = [[0 for i in range(10)] for r in range(22)]
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
            str(self.current_piece),
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
            # print(*lines, sep='\n')

    def load_game(self, filename):
        """Load a saved game from the given file.

        Args:
            filename: The file to read the saved game from
        """
        with open(filename, mode='r') as f:
            lines = f.readlines()

        self.current_piece = literal_eval(lines[1].strip())
        self.hold_queue = lines[2].strip()
        self.next_queue = literal_eval(lines[3].strip())
        self.stats = literal_eval(lines[4].strip())
        self._game_options = literal_eval(lines[5].strip())
        self.grid = literal_eval(lines[6].strip())

        if self._debug:
            print("DEBUG: Opened save file and retrieved stored data")
            # print(*lines)

    def _update_grid_position(self, row, col, type, ghost=False):
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
                The Tetrimino type (a single character) or "E" for empty
            ghost:
                A boolean to determine if the grid contains a ghost piece
        """
        if type == "E":
            self.grid[row][col] = 0
        else:
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

    def _update_grid_with_current_piece(self, old_piece=None):
        """Update the grid with the new position of the current piece.

        Call this after the current piece has moved in order to update the grid

        Args:
            A copy of the old current_piece variable. Defaults to None.
            If None is given then do not remove the old piece, just add the
            new one
        """
        # Remove the old pieces
        if old_piece is not None:
            old_blocks = [old_piece["block" + str(i)] for i in range(1, 5)]
            for (col, row) in old_blocks:
                self._update_grid_position(row, col, "E")

        # Add the new pieces
        new_piece = [self.current_piece["block" + str(i)] for i in range(1, 5)]
        for (col, row) in new_piece:
            self._update_grid_position(row, col, self.current_piece["type"])

        if self._debug:
            print("DEBUG: Updated Grid with new position of current piece")

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

    def start_game(self):
        """Start the game engine to play a game."""
        self.game_running = True

        if self._debug:
            print("DEBUG: Game Started")

    def _generation_phase(self):
        """Generate a Tetrimino to add to the matrix."""
        # Get the new piece type
        new_type = self.next_queue.pop(0)

        # Add new Tetrimino to the next_queue
        if self._bag == []:
            self._bag = ["O", "I", "T", "L", "J", "S", "Z"]
        # Append to the queue a random Tetrimino in the bag
        self.next_queue.append(self._bag.pop(randint(len(self._bag) - 1)))

        # Create the new piece
        if new_type == "I":
            self.current_piece = {
                "type": "I",
                "facing": "N",
                "block1": (4, 20),
                "block2": (5, 20),
                "block3": (6, 20),
                "block4": (7, 20)
            }
        elif new_type == "O":
            self.current_piece = {
                "type": "O",
                "facing": "N",
                "block1": (5, 21),
                "block2": (6, 21),
                "block3": (5, 20),
                "block4": (6, 20)
            }
        elif new_type == "T":
            self.current_piece = {
                "type": "T",
                "facing": "N",
                "block1": (5, 21),
                "block2": (4, 20),
                "block3": (5, 20),
                "block4": (6, 20)
            }
        elif new_type == "L":
            self.current_piece = {
                "type": "L",
                "facing": "N",
                "block1": (6, 21),
                "block2": (4, 20),
                "block3": (5, 20),
                "block4": (6, 20)
            }
        elif new_type == "J":
            self.current_piece = {
                "type": "J",
                "facing": "N",
                "block1": (4, 21),
                "block2": (4, 20),
                "block3": (5, 20),
                "block4": (6, 20)
            }
        elif new_type == "S":
            self.current_piece = {
                "type": "S",
                "facing": "N",
                "block1": (5, 21),
                "block2": (6, 21),
                "block3": (4, 20),
                "block4": (5, 20)
            }
        elif new_type == "Z":
            self.current_piece = {
                "type": "Z",
                "facing": "N",
                "block1": (4, 21),
                "block2": (5, 21),
                "block3": (5, 20),
                "block4": (6, 20)
            }

        # Add the new piece to the grid
        self._update_grid_with_current_piece()

        # Check if the Tetrimino can drop any further
        if self._check_movement_possible():
            self._move_current_piece()

        if self._debug:
            print("DEBUG:", self.current_piece, "added to the grid")
            print("DEBUG:", self.next_queue[-1], "pulled from the bag")
            print("DEBUG: Current state of the bag is:", self._bag)

    def _falling_phase(self):
        pass

    def _move_current_piece(self, direction="D"):
        """Move the current piece based on the direction given.

        Given a direction, calculate if the input is possible and if it is then
        execute the movement/rotation.

        Args:
            direction:
                A single character representing the desired movement:
                    L: Move left
                    R: Move right
                    D: Move down
                    C: Rotation clockwise
                    A: Rotation anti-clockwise
        """
        # Preserve the last position for updating later
        old_piece = self.current_piece
        # If the direction is a move
        if direction in "LRD":
            # Check if the move is possible
            if self._check_movement_possible(direction=direction):
                # Set the row and column deltas depending on the direction
                row_delta = -1 if direction == "D" else 0
                col_delta = -1 if direction == "L" else (
                    1 if direction == "R" else 0
                )

                # Update each block with the new postion
                for i in range(1, 5):
                    (col, row) = self.current_piece["block" + str(i)]
                    self.current_piece["block" + str(i)] = (
                        col + col_delta,
                        row + row_delta
                    )
        elif direction == "C":
            self._super_rotation(True)
        elif direction == "A":
            self._super_rotation(False)

        # After any movement update the grid
        if old_piece != self.current_piece:
            self._update_grid_with_current_piece()

    def _check_movement_possible(self, direction="D"):
        """Check if the current piece is blocked from moving in a direction.

        If the piece has blocks directly next to the piece in the direction
        specified then a move in the given direction is not possible.

        Args:
            direction: A character representing the direction. (L, R or D)

        Returns:
            A boolean determining if a movement in the direction is possible.
        """
        if self._debug:
            print("DEBUG: Checking if piece movement is possible:", direction)

        # Get a list of the blocks
        blocks = [self.current_piece["block" + str(i)] for i in range(1, 5)]

        # Set the delta for row and column
        if direction == "D":
            row_delta = -1
            col_delta = 0
        elif direction == "L":
            row_delta = 0
            col_delta = -1
        elif direction == "R":
            row_delta = 0
            col_delta = 1

        for (col, row) in blocks:
            # Check if the blow directly below it is occupied
            target = self.grid[row + row_delta][col + col_delta]
            if target in range(1, 8):
                if self._debug:
                    print("DEBUG: Tetrimino is blocked")
                return False

    def _super_rotation(self, clockwise):
        """Perform a super rotation if possible on the current piece.

        Attempts to perform a super rotation on the current piece in the
        direction given.

        Args:
            clockwise: A boolean that determines if the rotation is clockwise.
        """
        # Cannot rotate the O Tetrimino
        if self.current_piece["type"] == "O":
            return
        # TODO: Add rotations as an option
        pass


if __name__ == "__main__":
    engine = TetrisEngine(debug=True)
    engine._create_grid()
    engine.current_piece = {
        "type": "T",
        "facing": "N",
        "block1": (5, 4),
        "block2": (6, 4),
        "block3": (7, 4),
        "block4": (6, 5)
    }
    engine._move_current_piece(direction="D")
    print(engine.current_piece)
