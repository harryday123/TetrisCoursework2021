"""Tetris Game Engine for COMP16321 Coursework.

The module contains the Tetris Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""

# Imports
from csv import DictReader, DictWriter, reader


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
    """

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


if __name__ == "__main__":
    engine = TetrisEngine(debug=True)
    engine._prepare_leaderboard_file()
