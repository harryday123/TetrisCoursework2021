"""Tetris Game Engine for COMP16321 Coursework.

The module contains the Tetris Game Engine adapted from the official Tetris
guidelines. More info at: https://tetris.fandom.com/wiki/Tetris_Guideline
"""


class TetrisEngine():
    """An engine to run the classic Tetris Game.

    This class contains all the relevant code in order to have a functioning
    version of the tetris game. It provides an API to connect this engine to
    a GUI.

    Attributes:
        debug: Debug mode shows output messages and logs to aid with debugging
    """

    def __init__(self, debug=False):
        """Initialise the Game Engine with the given options.

        Args:
            debug: Determines whether to run the engine in debug mode
        """
        self.debug = debug


if __name__ == "__main__":
    TetrisEngine(debug=True)
