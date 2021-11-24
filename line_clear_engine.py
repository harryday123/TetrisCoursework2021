"""Line Clear Game Engine for COMP16321 Coursework.

The module contains the Line Clear Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""

# Imports
from csv import DictReader, DictWriter
from datetime import datetime
from ast import literal_eval
from random import randint, shuffle


class LineClearEngine:
    """An engine to run the classic line clearing game.

    This class contains all the relevant code in order to have a functioning
    version of the line clearing game. It provides an API to connect this
    engine to a GUI.

    Attributes:
        _debug:
            Debug mode shows output messages and logs to aid with debugging
        _game_options:
            A dictionary of game options.
             - hold_queue: Sets if the hold queue is turned on
             - ghost_piece: Determines if the ghost piece is shown
             - lock_down:
                The type of lock down setting to use.
                Values are "Extended", "Infinite" or "Classic"
                Refer to section 2.5.4 in the Tetris Guidlines for more info.
        _leaderboard:
            The relative file path to the leaderboard file.
        _grid_piece_map:
            A dictionary in order to map a piece to its relevant number
        grid:
            The array containing the matrix of cells on the board
        next_queue:
            The next 6 pieces to be added to the board
        hold_queue:
            The piece currently in the hold queue
        current_piece:
            A dictionary describing the piece controlled by the player.
            piece blocks are numbered top to bottom, left to right in the
            North facing orientation.
             - type: The type of piece
             - facing: Which direction the piece is facing. (N, E, S or W)
             - block1: The coordinates for block 1
             - block2: The coordinates for block 2
             - block3: The coordinates for block 3
             - block4: The coordinates for block 4

        stats:
            A dictionary of statistics for the game.
             - score: The current score for the game
             - lines: The number of lines the user has cleared so far
             - level: The level the user is currently on
             - goal: The next goal for line clears
        game_running:
            Shows whether the game is currently in progress
        game_paused:
            Shows whether the game is currently paused
        _hold_available:
            Determines if the current piece can swap into the hold queue
        _bag:
            The bag to generate pieces from
         fallspeed:
            The normal fall speed for the level. Defined in seconds per line.
    """

    _grid_piece_map = {
        "O": 1,
        "I": 2,
        "T": 3,
        "L": 4,
        "J": 5,
        "S": 6,
        "Z": 7
    }

    def __init__(self, debug=False, scoreboard="leaderboard.csv"):
        """Initialise the Game Engine with the given options.

        Args:
            debug: Determines whether to run the engine in debug mode
        """
        if debug:
            print("DEBUG - LineClearEngine: Running LineClearEngine.__init__")

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
            "level": 1,
            "goal": 0
        }
        self.game_running = False
        self.game_paused = False
        self._hold_available = True
        self._bag = []
        self.fallspeed = 0

        # Set the game options to their default values
        self._init_next_queue()
        self.set_game_options()
        self._create_grid()
        self._set_fall_speed()

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
            print("DEBUG - LineClearEngine: Generated empty grid array")

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
            print(
                "DEBUG - LineClearEngine: Output made for save. Output to:",
                file_name
            )
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
            print(
                "DEBUG - LineClearEngine: Opened save file and",
                "retrieved stored data"
            )
            # print(*lines)

    def _update_grid_position(self, row, col, type, ghost=False):
        """Update a grid cell with a new piece or ghost piece.

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
                The piece type (a single character) or "E" for empty
            ghost:
                A boolean to determine if the grid contains a ghost piece
        """
        if type == "E":
            self.grid[row][col] = 0
        else:
            if ghost:
                self.grid[row][col] = self._grid_piece_map[type] + 10
            else:
                self.grid[row][col] = self._grid_piece_map[type]

        if self._debug:
            print(
                "DEBUG - LineClearEngine: Updated Grid Cell at row: ", row,
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
            print("DEBUG - LineClearEngine: Updated Grid with new position",
                  "of current piece")

    def set_game_options(self, hold_on=True, ghost_piece=True):
        """Set the options for the game engine.

        Args:
            hold_on:
                Sets whether the user is able to hold a piece or not
                Defaults to True
            ghost_piece:
                Whether to show the ghost piece
                Defaults to True
        """
        self._game_options = {
            "hold_queue": hold_on,
            "ghost_piece": ghost_piece,
            "lock_down": "Extended"
        }
        if self._debug:
            print(
                "DEBUG - LineClearEngine: Set Game Options to",
                self._game_options
            )

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
            print(
                "DEBUG - LineClearEngine: Leaderboard Generated: ",
                output_list
            )

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
                "DEBUG - LineClearEngine:", initials, "with score", score,
                "added to leaderboard file", self._leaderboard
            )

    def start_game(self):
        """Start the game engine to play a game."""
        self.game_running = True
        self.game_paused = False

        self._set_fall_speed()
        self._generation_phase()

        if self._debug:
            print("DEBUG - LineClearEngine: Game Started")

    def _init_next_queue(self):
        self.next_queue = ["O", "I", "T", "L", "J", "S", "Z"]
        shuffle(self.next_queue)

    def _generation_phase(self, type=None, old_piece=None):
        """Generate a piece to add to the matrix.

        Args:
            type:
                The type of the piece to generate.
                Defaults to None. If None, the piece will be drawn from the bag
            old_piece:
                The old piece if one needs to be removed. Used when generating
                a piece from the Hold Queue
        """
        # If the type has not been given then generate a piece from the bag
        if type is None:
            # Add new piece to the next_queue
            if self._bag == []:
                self._bag = ["O", "I", "T", "L", "J", "S", "Z"]

            # Get the new piece type
            new_type = self.next_queue.pop(0)

            # Append to the queue a random piece in the bag
            self.next_queue.append(
                self._bag.pop(randint(0, len(self._bag) - 1))
            )
        else:
            # If the type has been given this is normally for a hold queue swap
            # The bag is not affected
            new_type = type

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
        self._update_grid_with_current_piece(old_piece=old_piece)

        if self._debug:
            print("DEBUG - LineClearEngine: Generation Phase Summary")
            print("DEBUG - LineClearEngine:",
                  self.current_piece, "added to the grid")
            if type is not None:
                print("DEBUG - LineClearEngine:",
                      self.next_queue[-1], "pulled from the bag")
                print(
                    "DEBUG - LineClearEngine: Current state of the bag is:",
                    self._bag
                )

        # Check if the piece can drop any further
        if self._check_movement_possible():
            self.move_current_piece()

    def falling_phase(self):
        """Run the Falling Phase of the engine.

        This is the phase where the piece is constantly falling.
        """
        if self._debug:
            print("DEBUG - LineClearEngine: Entering Falling Phase")

        if self._check_movement_possible():
            if self._debug:
                print("DEBUG - LineClearEngine: Fall Possible")

            self.move_current_piece()
        else:
            if self._debug:
                print("DEBUG - LineClearEngine: Fall Not Possible")

            self._lock_phase()

    def _lock_phase(self):
        """Run the Lock Phase of the engine.

        This is the phase where the current piece has touched down onto a
        surface.
        """
        if self._debug:
            print("DEBUG - LineClearEngine: Entering Lock Phase")
        # if self._game_options["lock_down"] == "Extended":
        #     pass
        # elif self._game_options["lock_down"] == "Classic":
        #     pass
        # else:
        # TODO: Look into if the above is possible

        # Locked down here
        self._hold_available = True
        self._pattern_match()
        self._completion_phase()
        if self.game_running:
            self._generation_phase()

    def _set_fall_speed(self):
        """Set the fall speed based on the level and soft drop setting.

        Args:
            soft: A boolean defaults to False. If True, the speed is 20x faster
        """
        # Update the fall speed
        self.fallspeed = round(((
            0.8 - ((self.stats["level"] - 1) * 0.007)
        ) ** (self.stats["level"] - 1)) * 1000)

        if self._debug:
            print("DEBUG - LineClearEngine: Fall Speed set to", self.fallspeed)

    def hard_drop(self):
        """Hard Drop the current piece."""
        if self._debug:
            print("DEBUG - LineClearEngine: Hard Dropping")

        while self._check_movement_possible():
            self.move_current_piece()

    def toggle_pause_game(self):
        """Pause the game running."""
        if self._debug:
            print(
                "DEBUG - LineClearEngine: Game Pause Toggled from:",
                self.game_paused
            )

        self.game_paused = not self.game_paused

    def hold_swap(self):
        """Swap the current piece into the hold queue if available."""
        if self._hold_available:
            # If the hold queue has a value to swap out
            if self.hold_queue is not None:
                current_type = self.current_piece["type"]
                self._generation_phase(
                    type=self.hold_queue,
                    old_piece=self.current_piece
                )
                self.hold_queue = current_type
            else:
                # If the hold queue is empty
                self.hold_queue = self.current_piece["type"]
                self._generation_phase(
                    old_piece=self.current_piece
                )

            # After swapping
            self._hold_available = False

    def move_current_piece(self, direction="D"):
        """Move the current piece based on the direction given.

        Given a direction, calculate if the input is possible and if it is then
        execute the movement / rotation.

        Args:
            direction:
                A single character representing the desired movement:
                    L: Move left
                    R: Move right
                    D: Move down
                    C: Rotation clockwise
                    A: Rotation anti - clockwise
        """
        if self._debug:
            print(
                "DEBUG - LineClearEngine: Moving current piece in direction:",
                direction
            )

        # Preserve the last position for updating later
        old_piece = self.current_piece.copy()
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
            self._update_grid_with_current_piece(old_piece=old_piece)
            if self._debug:
                print("DEBUG - LineClearEngine: Piece moved")

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
            print(
                "DEBUG - LineClearEngine: Checking if movement is possible:",
                direction
            )

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
            (new_col, new_row) = (col + col_delta, row + row_delta)

            # Check the new coords are in the Grid
            if new_col not in range(10) or new_row not in range(22):
                return False

            target = self.grid[new_row][new_col]

            if target in range(1, 8) and (new_col, new_row) not in blocks:
                if self._debug:
                    print("DEBUG - LineClearEngine: Piece is blocked")
                return False
        return True

    def _super_rotation(self, clockwise):
        """Perform a super rotation if possible on the current piece.

        Attempts to perform a super rotation on the current piece in the
        direction given.

        Args:
            clockwise: A boolean that determines if the rotation is clockwise.
        """
        type = self.current_piece["type"]
        # Cannot rotate the O piece
        if type == "O":
            return
        # A dictionary showing which block is the centre of each piece
        centre_point_map = {
            "O": "block3",
            "I": "block2",
            "T": "block3",
            "L": "block3",
            "J": "block3",
            "S": "block4",
            "Z": "block3"
        }

        # Maps a direction to a tuple containing the adjacent directions
        rotation_map = {
            "N": ("W", "E"),
            "E": ("N", "S"),
            "S": ("E", "W"),
            "W": ("S", "N")
        }

        # Get the coordinates of the centre block
        centre_coords = self.current_piece[
            centre_point_map[type]
        ]

        # Save the new locations for each block
        new_block_coords = []
        for i in range(1, 5):
            # For each block in the piece
            # Get the block's new coords after it has been rotated.
            new_block_coords.append(self._calculate_block_rotation(
                self.current_piece["block" + str(i)],
                centre_coords,
                clockwise
            ))

        if self._debug:
            print("DEBUG - LineClearEngine: Coordinates generated after block",
                  "rotation")

        # Check that the rotation is possible with the offsets
        self._check_offsets(
            type,
            new_block_coords,
            self.current_piece["facing"],
            rotation_map[self.current_piece["facing"]][clockwise]
        )

    def _check_offsets(self, type, block_coords, old_facing, new_facing):
        """Check if a rotation is possible via the offsets.

        Args:
            type: The type of piece
            block_coords: The coordinates for the rotated blocks
            old_facing: The direction the piece was originally facing
            new_facing: The direction the piece is now facing

        Returns:
            bool: Shows if the rotation is possible
        """
        if self._debug:
            print("DEBUG - LineClearEngine: Checking offsets for possible",
                  "rotation")

        offsets = {
            "I": {
                1: {"N": (0, 0), "E": (-1, 0), "S": (-1, 1), "W": (0, 1)},
                2: {"N": (-1, 0), "E": (0, 0), "S": (1, 1), "W": (0, 1)},
                3: {"N": (2, 0), "E": (0, 0), "S": (-2, 1), "W": (0, 1)},
                4: {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)},
                5: {"N": (2, 0), "E": (0, -2), "S": (-2, 0), "W": (0, 1)}
            },
            "L": {
                1: {"N": (0, 0), "E": (0, 0), "S": (0, 0), "W": (0, 0)},
                2: {"N": (0, 0), "E": (1, 0), "S": (0, 0), "W": (-1, 0)},
                3: {"N": (0, 0), "E": (1, -1), "S": (0, 0), "W": (-1, -1)},
                4: {"N": (0, 0), "E": (0, 2), "S": (0, 0), "W": (0, 2)},
                5: {"N": (0, 0), "E": (1, 2), "S": (0, 0), "W": (-1, 2)}
            },
            "S": {
                1: {"N": (0, 0), "E": (0, 0), "S": (0, 0), "W": (0, 0)},
                2: {"N": (0, 0), "E": (1, 0), "S": (0, 0), "W": (-1, 0)},
                3: {"N": (0, 0), "E": (1, -1), "S": (0, 0), "W": (-1, -1)},
                4: {"N": (0, 0), "E": (0, 2), "S": (0, 0), "W": (0, 2)},
                5: {"N": (0, 0), "E": (1, 2), "S": (0, 0), "W": (-1, 2)}
            },
            "T": {
                1: {"N": (0, 0), "E": (0, 0), "S": (0, 0), "W": (0, 0)},
                2: {"N": (0, 0), "E": (1, 0), "S": (0, 0), "W": (-1, 0)},
                3: {"N": (0, 0), "E": (1, -1), "S": (0, 0), "W": (-1, -1)},
                4: {"N": (0, 0), "E": (0, 2), "S": (0, 0), "W": (0, 2)},
                5: {"N": (0, 0), "E": (1, 2), "S": (0, 0), "W": (-1, 2)}
            },
            "Z": {
                1: {"N": (0, 0), "E": (0, 0), "S": (0, 0), "W": (0, 0)},
                2: {"N": (0, 0), "E": (1, 0), "S": (0, 0), "W": (-1, 0)},
                3: {"N": (0, 0), "E": (1, -1), "S": (0, 0), "W": (-1, -1)},
                4: {"N": (0, 0), "E": (0, 2), "S": (0, 0), "W": (0, 2)},
                5: {"N": (0, 0), "E": (1, 2), "S": (0, 0), "W": (-1, 2)}
            },
            "J": {
                1: {"N": (0, 0), "E": (0, 0), "S": (0, 0), "W": (0, 0)},
                2: {"N": (0, 0), "E": (1, 0), "S": (0, 0), "W": (-1, 0)},
                3: {"N": (0, 0), "E": (1, -1), "S": (0, 0), "W": (-1, -1)},
                4: {"N": (0, 0), "E": (0, 2), "S": (0, 0), "W": (0, 2)},
                5: {"N": (0, 0), "E": (1, 2), "S": (0, 0), "W": (-1, 2)}
            }
        }

        possible = False
        offset = None

        for i in range(1, 6):
            offset_1 = offsets[type][i][old_facing]
            offset_2 = offsets[type][i][new_facing]
            offset = (offset_1[0] - offset_2[0], offset_1[1] - offset_2[1])
            if self._check_piece_can_move_by_offset(block_coords, offset):
                possible = True
                if self._debug:
                    print("DEBUG - LineClearEngine: Possible offset found:", i)
                break

        if possible:
            if self._debug:
                print("DEBUG - LineClearEngine: Possible rotation found.")
            self._rotate_current_piece(block_coords, offset)
        else:
            if self._debug:
                print("DEBUG - LineClearEngine: Rotation not possible.")

    def _rotate_current_piece(self, block_coords, offset):
        """Rotate the current piece to the new coordinates.

        Args:
            block_coords: The new coordinates of the blocks after rotation
            offset: The offset to apply to the coordinates
        """
        for i in range(1, 5):
            self.current_piece["block" + str(i)] = (
                block_coords[i - 1][0] + offset[0],
                block_coords[i - 1][1] + offset[1]
            )

        if self._debug:
            print("DEBUG - LineClearEngine: Current Piece Rotated")

    def _check_piece_can_move_by_offset(self, block_coords, offset):
        """Check if the can move by a given offset.

        Args:
            block_coords: The new block cordinates
            offset: The offset to shift the piece by

        Returns:
            bool: True if the offset is possible or not
        """
        if self._debug:
            print("DEBUG - LineClearEngine: Checking offset is legal")
        # For each block in the piece
        for (col, row) in block_coords:
            # Calculate the new coords with the offset
            (new_col, new_row) = (col + offset[0], row + offset[1])

            if new_col not in range(10) or new_row not in range(22):
                if self._debug:
                    print("DEBUG - LineClearEngine: Offset not in grid")
                return False

            # Check if the block is currently filled with a block
            if self.grid[new_row][new_col] in range(1, 8):
                held_by_current = False
                # Aim of this for loop is to check if the block is trying to
                # move into a block occupied by the current piece
                # For each block in the current piece
                for i in range(1, 5):
                    # Check that the current piece is not the block in the way
                    if (new_col,
                            new_row) == self.current_piece["block" + str(i)]:
                        # If the piece is moving to a block currently held by
                        # the current piece then exit the loop
                        held_by_current = True
                        break
                if not held_by_current:
                    if self._debug:
                        print("DEBUG - LineClearEngine: Offset blocked")
                    return False

        return True

    def _calculate_block_rotation(self, coords, center, clockwise):
        """Rotate a block 90 degrees about a center of rotation.

        Args:
            coords: The coordinates for the block
            center: Coordinates for the center of rotation
            clockwise: True for clockwise, false for anti - clockwise
        """
        rel_pos_to_center = (coords[0] - center[0], coords[1] - center[1])
        rot_mat = [[0, 1], [-1, 0]] if clockwise else [[0, -1], [1, 0]]

        new_rel_coords = (
            (rot_mat[0][0] * rel_pos_to_center[0]) +
            (rot_mat[0][1] * rel_pos_to_center[1]),
            (rot_mat[1][0] * rel_pos_to_center[0]) +
            (rot_mat[1][1] * rel_pos_to_center[1])
        )
        if self._debug:
            print("DEBUG - LineClearEngine: New coordinates after rotation",
                  "calculated")
        return (center[0] + new_rel_coords[0], center[1] + new_rel_coords[1])

    def _check_game_overs(self):
        """Check if a Game Over event has occured."""
        if self._debug:
            print("DEBUG - LineClearEngine: Checking for Game Over conditions")

        game_over = False
        below_sky = False
        above_sky = False

        blocks = [self.current_piece["block" + str(i)] for i in range(1, 5)]

        for (col, row) in blocks:
            # Check if the current piece is in the spawn area
            if row == 20 and col in range(4, 8):
                game_over = True
            elif row == 21 and col in range(4, 7):
                game_over = True
            # Else check if there are any other blocks above tha
            elif row < 20:
                below_sky = True
            else:
                above_sky = True

        # Check that there at least one piece is below the skyline
        if above_sky and not below_sky:
            game_over = True

        if game_over:
            # Game Over Logic
            self.game_running = False
            if self._debug:
                print("DEBUG - LineClearEngine: Game Over Condition Found")

    def _pattern_match(self):
        """Check the grid for lines to be cleared.

        Check each row in turn and if it is full then mark it to be deleted.
        """
        if self._debug:
            print("DEBUG - LineClearEngine: Checking for line clears")
        # TODO: Check this
        rows_to_clear = []
        # Loop through each row
        for i in range(len(self.grid)):
            row_clear = True
            # Check each cell in the row
            for cell in self.grid[i]:
                # If the cell does not contain a Mino
                if cell not in range(1, 8):
                    # Do not clear the row
                    row_clear = False
                    break
            # If the row can be cleared
            if row_clear:
                # Add the row to the list
                rows_to_clear.append(i)

        # After all rows are checked update the grid
        self._clear_rows(rows_to_clear)

        # Update the lines cleared stat
        self.stats["lines"] += len(rows_to_clear)
        if self._debug:
            print("DEBUG - LineClearEngine: Lines cleared updated to:",
                  self.stats["lines"])

    def _clear_rows(self, rows):
        """Clear the given rows from the grid.

        Args:
            rows: The list of rows to remove
        """
        for row in rows:
            self.grid.pop(row)
            self.grid.append([0 for i in range(10)])

        if self._debug:
            print("DEBUG - LineClearEngine: Rows:",
                  rows, "cleared from the grid")

    def _completion_phase(self):
        """Finalise the round and prepare for the next generation."""
        # TODO: Update Score
        # Check if level up has occured
        if self.stats["goal"] <= self.stats["lines"]:
            if self._debug:
                print("DEBUG - LineClearEngine: Level Up Occured")

            self.stats["level"] += 1
            self.stats["goal"] += self.stats["level"] * 5
            self._set_fall_speed()

        self._check_game_overs()

    def reset_state(self):
        """Reset the engine to run the game again."""
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
            "level": 1,
            "goal": 0
        }
        self.game_running = False
        self.game_paused = False
        self._hold_available = True
        self.hold_queue = None
        self._bag = []
        self._init_next_queue()
        self._create_grid()
        self._set_fall_speed()


if __name__ == "__main__":
    engine = LineClearEngine(debug=True)
    engine._create_grid()
    engine.current_piece = {
        "type": "T",
        "facing": "N",
        "block1": (5, 4),
        "block2": (6, 4),
        "block3": (7, 4),
        "block4": (6, 5)
    }
    engine.move_current_piece(direction="D")
    print(engine.current_piece)
