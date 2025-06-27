from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSpinBox, QCheckBox, QWidget, QMainWindow

class SettingsRow(QHBoxLayout):
    """
    A custom QHBoxLayout subclass that provides a row of settings controls for configuring quadrilateral detection parameters.
    Args:
        main_window (QMainWindow): The main application window, used to notify when settings change.
        parent (QWidget, optional): The parent widget for this layout. Defaults to None.
    Attributes:
        main_window (QMainWindow): Reference to the main application window.
        rows_label (QLabel): Label for the number of rows setting.
        rows_spin (QSpinBox): Spin box to select the number of rows.
        cols_label (QLabel): Label for the number of columns setting.
        cols_spin (QSpinBox): Spin box to select the number of columns.
        check_box (QCheckBox): Checkbox to toggle display of cells.
    Methods:
        on_settings_changed():
            Notifies the main window that a setting has changed.
        get_nb_quadrilateral_rows() -> int:
            Returns the current value for the number of quadrilateral rows.
        get_nb_quadrilateral_cols() -> int:
            Returns the current value for the number of quadrilateral columns.
        is_display_on() -> bool:
            Returns True if the "Display Cells" checkbox is checked, False otherwise.
    """
    def __init__(self, main_window: QMainWindow, parent: QWidget = None):
        """
        Initializes the settings row UI components for the Chess Score Sheet Scanner application.
        Args:
            main_window (QMainWindow): The main application window to which this settings row belongs.
            parent (QWidget, optional): The parent widget of this settings row. Defaults to None.
        Attributes:
            main_window (QMainWindow): Reference to the main application window.
            rows_label (QLabel): Label for the number of rows setting.
            rows_spin (QSpinBox): Spin box to select the number of rows (1-100, default 40).
            cols_label (QLabel): Label for the number of columns setting.
            cols_spin (QSpinBox): Spin box to select the number of columns (1-100, default 2).
            check_box (QCheckBox): Checkbox to toggle the display of cells.
        Connects:
            - Value changes in spin boxes and state changes in the checkbox to the `on_settings_changed` handler.
        """
        super().__init__(parent)

        # Main window
        self.main_window = main_window

        # Rows
        self.rows_label = QLabel("Rows:")
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setMaximum(100)
        self.rows_spin.setValue(40)

        # Columns
        self.cols_label = QLabel("Columns:")
        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setMaximum(100)
        self.cols_spin.setValue(2)

        # Checkable button
        self.check_box = QCheckBox("Display Cells")

        # Add widgets to layout
        self.addWidget(self.rows_label)
        self.addWidget(self.rows_spin)
        self.addWidget(self.cols_label)
        self.addWidget(self.cols_spin)
        self.addWidget(self.check_box)

        # Connect signals to update handler
        self.rows_spin.valueChanged.connect(self.on_settings_changed)
        self.cols_spin.valueChanged.connect(self.on_settings_changed)
        self.check_box.stateChanged.connect(self.on_settings_changed)

    def on_settings_changed(self) -> None:
        """
        Handles the event when settings are changed by invoking the corresponding method
        on the main window to update the application state accordingly.
        """
        self.main_window.on_settings_changed()

    def get_nb_quadrilateral_rows(self) -> int:
        """
        Returns the current value of the rows spin box, representing the number of quadrilateral rows.

        Returns:
            int: The number of quadrilateral rows as specified by the user input.
        """
        return self.rows_spin.value() 

    def get_nb_quadrilateral_cols(self) -> int:
        """
        Returns the current value of the cols spin box, representing the number of quadrilateral cols.

        Returns:
            int: The number of quadrilateral cols as specified by the user input.
        """
        return self.cols_spin.value() 

    def is_display_on(self) -> bool:
        """
        Check if the display option is enabled.

        Returns:
            bool: True if the checkbox is checked (display is on), False otherwise.
        """
        return self.check_box.isChecked() 