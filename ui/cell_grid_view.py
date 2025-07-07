from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QFrame, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class CellGridView(QWidget):
    def __init__(self, main_window: QMainWindow, parent: QWidget = None):
        super().__init__(parent)

        # Main window
        self.main_window = main_window

        # Main layout for this widget
        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)

        # Scroll area setup
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scroll_area)

        # Container for cell images
        self.container = QFrame()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setSpacing(8)
        self.container_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_area.setWidget(self.container)

    def display_cells(self, cell_pixmap_list: list[QPixmap]) -> None:
        # Clear precedent cell display
        self.clear()

        # Display cell displays
        for cell_idx, cell_pixmap in enumerate(cell_pixmap_list):
            cell_widget = QWidget()
            cell_layout = QVBoxLayout(cell_widget)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(2)

            image_label = QLabel()
            image_label.setPixmap(cell_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            text_label = QLabel(f"Cell {cell_idx + 1}")
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            cell_layout.addWidget(image_label)
            cell_layout.addWidget(text_label)

            self.container_layout.addWidget(cell_widget)

    def clear(self) -> None:
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()