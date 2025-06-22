import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu ,QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import QPointF

from ui.image_view import ImageView
from ui.button_row import ButtonRow, ButtonRowMode

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initializes the main window for the PyQt6 Image Annotator application.
        Sets up the window title and size, creates the button row for image controls,
        initializes coordinate and zoom labels, and sets up the image view area.
        Finally, calls the method to initialize the rest of the UI components.
        """
        super().__init__()

        # Window initialization
        self.setWindowTitle("PyQt6 Image Annotator")
        self.resize(1200, 800)

        # Buttons for Image view
        self.button_row: ButtonRow = ButtonRow(main_window=self)

        # Labels
        self.coord_label: QLabel = QLabel("")
        self.zoom_label: QLabel = QLabel("")

        # Image view
        self.image_view: ImageView = ImageView(main_window=self)

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
        main_layout.addLayout(self.button_row)
        main_layout.addWidget(self.image_view)
        main_layout.addWidget(self.coord_label)
        main_layout.addWidget(self.zoom_label)
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
        self.image_view.set_mode(target_mode)

    def open_image(self) -> None:
        """
        Opens a file dialog for the user to select an image file, loads the selected image into a QPixmap,
        and displays it in the image view. If no file is selected or the image fails to load, the method returns early.
        Also sets the UI mode to navigation after loading the image.
        """
        # Ask user for an image file
        file_path: str
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.bmp)")
        if file_path is None:
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
