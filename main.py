import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QStatusBar, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QAction

from ui.image_view import ImageView, ImageViewMode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Image Annotator")
        self.resize(1200, 800)
        self.image_view = ImageView()
        self.coord_label = QLabel("")
        self.zoom_label = QLabel("")
        self.image_view.set_coord_label(self.coord_label)
        self.image_view.set_zoom_label(self.zoom_label)
        self.init_ui()

    def init_ui(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_image)
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close_image)
        file_menu.addAction(open_action)
        file_menu.addAction(close_action)

        view_menu = menubar.addMenu("View")
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(lambda: self.image_view.zoom_in_out(incremental_factor=self.image_view.ZOOM_IN_FACTOR))
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(lambda: self.image_view.zoom_in_out(incremental_factor=self.image_view.ZOOM_OUT_FACTOR))
        view_menu.addAction(zoom_in_action)
        view_menu.addAction(zoom_out_action)

        # --- Mode selection buttons (mutually exclusive) ---
        mode_row = QHBoxLayout()
        self.draw_btn = QPushButton("Draw")
        self.modify_btn = QPushButton("Modify")
        self.navigate_btn = QPushButton("Navigate")

        for btn in (self.draw_btn, self.modify_btn, self.navigate_btn):
            btn.setCheckable(True)
            mode_row.addWidget(btn)

        self.draw_btn.setChecked(True)  # Default mode

        self.navigate_btn.clicked.connect(lambda: self.set_mode(ImageViewMode.NAVIGATE))
        self.draw_btn.clicked.connect(lambda: self.set_mode(ImageViewMode.DRAW))
        self.modify_btn.clicked.connect(lambda: self.set_mode(ImageViewMode.MODIFY))

        # Layout without rulers, just the image view and coordinate label
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addLayout(mode_row)
        main_layout.addWidget(self.image_view)
        main_layout.addWidget(self.coord_label)
        main_layout.addWidget(self.zoom_label)
        self.setCentralWidget(central_widget)
        self.setStatusBar(QStatusBar())

        # Set initial mode
        self.set_mode(ImageViewMode.NAVIGATE)

    def set_mode(self, mode: ImageViewMode):
        # Ensure only one button is checked
        self.draw_btn.setChecked(False)
        self.modify_btn.setChecked(False)
        self.navigate_btn.setChecked(False)

        match mode:
            case ImageViewMode.NAVIGATE:
                self.navigate_btn.setChecked(True)
            case ImageViewMode.DRAW:
                self.draw_btn.setChecked(True)
            case ImageViewMode.MODIFY:
                self.modify_btn.setChecked(True)

        # Pass mode to image_view
        self.image_view.set_mode(mode)

    def open_image(self) -> None:
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

    def close_image(self):
        self.image_view.close_image()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
