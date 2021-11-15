"""Tetris Game Engine for COMP16321 Coursework.

The module contains the Tetris Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""


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
    """

    def __init__(self, debug=False):
        """Initialise the Game Engine with the given options.

        Args:
            debug: Determines whether to run the engine in debug mode
        """
        if debug:
            print("DEBUG: Running TetrisEngine.__init__()")

        self._debug = debug
        self.set_game_options()

    def set_game_options(
        self,
        next_queue=6,
        hold_queue=True,
        ghost_piece=True
    ):
        """Set the options for the game engine.

        Args:
            next_queue:
                How many Tetriminos to display in the next queue.
                Int 1-6
            hold_queue:
                Sets whether the user is able to hold a Tetrimino or not
                Defaults to True
            ghost_piece:
                Whether to show the ghost piece
                Defaults to True
        """
        self._game_options = {
            "next_queue": next_queue,
            "hold_queue": hold_queue,
            "ghost_piece": ghost_piece
        }
        if self._debug:
            print("DEBUG: Set Game Options to", self._game_options)


if __name__ == "__main__":
    engine = TetrisEngine(debug=True)
