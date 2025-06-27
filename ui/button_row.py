from enum import Enum

from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QMainWindow

class ButtonRowMode(Enum):
    """
    An enumeration representing the different modes available for a button row in the UI.

    Attributes:
        DRAW (ButtonRowMode): Mode for drawing or creating new elements.
        EDIT (ButtonRowMode): Mode for navigating, modifying or editing existing elements.
    """
    DRAW = "Draw"
    EDIT = "Edit"

class ButtonRow(QHBoxLayout):
    def __init__(self, main_window, parent=None):
        """
        Initializes the ButtonRow widget.
        Args:
            main_window (QMainWindow): The main application window to interact with.
            parent (QWidget, optional): The parent widget. Defaults to None.
        Attributes:
            button_dict (dict[ButtonRowMode, QPushButton]): 
                Dictionary mapping each ButtonRowMode to its corresponding QPushButton.
            main_window (QMainWindow): 
                Reference to the main application window.
        The constructor creates a checkable QPushButton for each mode in ButtonRowMode,
        connects each button's clicked signal to set the mode in the main window,
        adds the button to the layout, and stores it in button_dict.
        """
        super().__init__(parent)

        # Button Dictionnary
        self.button_dict: dict[ButtonRowMode, QPushButton] = {}
        for mode in ButtonRowMode:
            # Create button
            button: QPushButton = QPushButton(mode.value)
            button.setCheckable(True)
            button.clicked.connect(lambda _, m=mode: self.main_window.set_mode(m))

            # Add button
            self.addWidget(button)
            self.button_dict[mode] = button
        
        # Main window
        self.main_window: QMainWindow = main_window

    def check_button(self, target_mode: ButtonRowMode) -> None:
        """
        Sets the checked state of buttons in the button row.

        Iterates through all buttons in the button_dict and sets the checked state to True
        for the button corresponding to the given target_mode, and False for all others.

        Args:
            target_mode (ButtonRowMode): The mode whose button should be checked.
        """
        for mode, btn in self.button_dict.items():
            btn.setChecked(mode == target_mode)
