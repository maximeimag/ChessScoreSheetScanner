import os
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu ,QFileDialog, QVBoxLayout, QWidget, QStatusBar, QLabel
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import QPointF

from ui.image_view import ImageView
from ui.button_row import ButtonRow, ButtonRowMode
from ui.settings_row import SettingsRow
from ui.cell_grid_view import CellGridView

class MainWindow(QMainWindow):
    """
    MainWindow is the primary window class for the Chess Score Sheet Scanner application.
    This class manages the main user interface, including the menu bar, image view, 
    settings and button rows, coordinate and zoom labels, and status bar. It provides 
    methods for initializing and updating the UI, handling image loading and closing, 
    switching interaction modes, and responding to user actions such as zooming and 
    settings changes.
    Attributes:
        settings_row (SettingsRow): The row containing settings controls for the application.
        button_row (ButtonRow): The row containing image control buttons.
        coord_label (QLabel): Label displaying the current mouse coordinates over the image.
        zoom_label (QLabel): Label displaying the current zoom level.
        image_view (ImageView): The widget responsible for displaying and interacting with the image.
        cell_grid_view (CellGridView): The widget responsible for displaying internal cells
    Methods:
        __init__(): Initializes the main window and its components.
        init_ui(): Sets up the layout, menu bar, and main UI elements.
        init_menubar(): Configures the menu bar with File and View menus and their actions.
        set_mode(target_mode): Sets the current interaction mode and updates UI accordingly.
        open_image(): Opens a file dialog to load and display an image.
        close_image(): Closes the currently displayed image and resets labels.
        reset_labels(): Clears the coordinate and zoom labels.
        update_labels(mouse_position, scale_factor): Updates the coordinate and zoom labels.
        update_cell_grid_view() : Get internal cells and display in cell_grid_view widget
        on_settings_changed(): Handles updates when application settings are changed.
    """
    def __init__(self):
        """
        Initializes the main window for the Chess Score Sheet Scanner application.
        Sets up the window title and size, initializes the settings and button rows,
        creates labels for coordinates and zoom level, and sets up the image view.
        Finally, calls the method to initialize the user interface.
        """
        super().__init__()

        # Window initialization
        self.setWindowTitle("Chess Score Sheet Scanner")
        self.resize(1200, 800)

        # Quadrilateral settings
        self.settings_row: SettingsRow = SettingsRow(main_window=self)

        # Buttons for Image view
        self.button_row: ButtonRow = ButtonRow(main_window=self)

        # Labels
        self.coord_label: QLabel = QLabel("")
        self.zoom_label: QLabel = QLabel("")

        # Image view
        self.image_view: ImageView = ImageView(main_window=self)

        # Cells display
        self.cell_grid_view: CellGridView = CellGridView(main_window=self)

        # Init UI
        self.init_ui()

    def init_ui(self) -> None:
        """
        Initializes the main window's user interface components.
        This method sets up the menu bar, central widget, and main layout, 
        including the button row, image view, coordinate label, and zoom label. 
        It also configures the status bar and sets the initial interaction mode 
        for the application.
        """
        # Init Menu Bar
        self.init_menubar()

        # Layout without rulers, just the image view and coordinate label
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addLayout(self.settings_row)
        main_layout.addLayout(self.button_row)
        main_layout.addWidget(self.image_view)
        main_layout.addWidget(self.coord_label)
        main_layout.addWidget(self.zoom_label)
        main_layout.addWidget(self.cell_grid_view)
        self.setCentralWidget(central_widget)
        self.setStatusBar(QStatusBar())

        # Set initial mode
        self.set_mode(target_mode=ButtonRowMode.EDIT)

    def init_menubar(self) -> None:
        """
        Initializes the application's menu bar with 'File' and 'View' menus.
        The 'File' menu provides actions to open and close images.
        The 'View' menu provides actions to zoom in and zoom out on the image view.
        Connects menu actions to their respective handler methods.
        """
        # Menu bar initialization
        menubar: QMenuBar = self.menuBar()

        # File Menu
        file_menu: QMenu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_image)
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_image)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        # View Menu
        view_menu = menubar.addMenu("View")
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(lambda: self.image_view.zoom_in_out(incremental_factor=self.image_view.ZOOM_IN_FACTOR))
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(lambda: self.image_view.zoom_in_out(incremental_factor=self.image_view.ZOOM_OUT_FACTOR))
        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)

    def set_mode(self, target_mode: ButtonRowMode):
        """
        Sets the current mode for the application.
        This method ensures that only the button corresponding to the specified mode is checked,
        and updates the image view to reflect the selected mode.
        Args:
            target_mode (ButtonRowMode): The mode to set, which determines the active button and image view state.
        """
        # Ensure only one button is checked
        self.button_row.check_button(target_mode=target_mode)

        # Pass mode to image_view
        self.image_view.set_mode(target_mode=target_mode)

    def open_image(self) -> None:
        """
        Opens a file dialog for the user to select an image file, loads the selected image into a QPixmap,
        and displays it in the image view. If no file is selected or the image fails to load, the method returns early.
        Also sets the UI mode to navigation after loading the image.
        """
        # Ask user for an image file
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")

        # Check file_path
        if file_path is None:
            return
        if not os.path.exists(file_path):
            return
        
        # Load image to a pixmap
        pixmap: QPixmap = QPixmap(file_path)
        if pixmap is None:
            return

        self.image_view.load_image(pixmap=pixmap)
        self.set_mode(ButtonRowMode.EDIT)

    def close_image(self):
        """
        Closes the currently displayed image in the image view component.
        """
        self.reset_labels()
        self.image_view.close_image()
        self.cell_grid_view.clear()

    def reset_labels(self) -> None:
        """
        Clears the text of the coordinate and zoom labels by setting them to empty strings.
        """
        self.coord_label.setText("")
        self.zoom_label.setText("")

    def update_labels(self, mouse_position: QPointF | None = None, scale_factor: float | None = None) -> None:
        """
        Updates the coordinate and zoom labels based on the provided mouse position and scale factor.

        Args:
            mouse_position (QPointF | None, optional): The current mouse position to display in the coordinate label.
                If None, the coordinate label is not updated.
            scale_factor (float | None, optional): The current zoom scale factor to display in the zoom label.
                If None, the zoom label is not updated.

        Returns:
            None
        """
        if mouse_position is not None:
            self.coord_label.setText(f"{int(mouse_position.x())}, {int(mouse_position.y())} px")
        if scale_factor is not None:
            self.zoom_label.setText(f"{int(scale_factor * 100)} %")

    def update_cell_grid_view(self) -> None:
        """
        Updates the cell grid view with the latest extracted and resized cell images.
        This method retrieves a list of QPixmap objects representing individual cells
        from the image view. If the extraction fails (returns None), it clears the cell grid view.
        Otherwise, it displays the extracted cell images in the cell grid view.
        Returns:
            None
        """
        # Get cells list
        cell_pixmaps_list: list[QPixmap] | None = self.image_view.extract_and_resize_cells()

        # Clear if list is None
        if cell_pixmaps_list is None:
            self.cell_grid_view.clear()
            return
        
        # Display cells
        self.cell_grid_view.display_cells(cell_pixmap_list=cell_pixmaps_list)
    
    def on_settings_changed(self):
        """
        Handles updates when settings are changed by delegating the update to the image view component.
        """
        self.image_view.on_settings_changed()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
