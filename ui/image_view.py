from enum import Enum

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent
from PyQt6.QtCore import Qt, QPointF, QRectF

from ui.utils.Quadrilateral import Quadrilateral

class ImageViewMode(Enum):
    NAVIGATE = 0
    DRAW = 1
    MODIFY = 2


class ImageView(QGraphicsView):

    ZOOM_LOWER_LIMIT: float = 0.2
    ZOOM_UPPER_LIMIT: float = 5.0

    ZOOM_IN_FACTOR: float = 1.05
    ZOOM_OUT_FACTOR: float = 1.0 / ZOOM_IN_FACTOR

    COLOR_UNSELECTED_QUADRILATERAL_POINTS: QColor = QColor(255, 255, 255)
    PEN_UNSELECTED_QUADRILATERAL: QPen = QPen(QColor(255, 0, 0), 2)
    UNSELECTED_POINT_SIZE: int = 5

    COLOR_DRAWING_QUADRILATERAL_POINTS: QColor = QColor(0, 0, 255)
    PEN_DRAWING_QUADRILATERAL: QPen = QPen(QColor(0, 0, 255), 2, Qt.PenStyle.DashLine)
    DRAWING_POINT_SIZE: int = 7

    COLOR_SELECTED_QUADRILATERAL_POINTS: QColor = QColor(0, 255, 0)
    PEN_SELECTED_QUADRILATERAL: QPen = QPen(QColor(0, 255, 0), 2)
    SELECTED_POINT_SIZE: int = 7

    def __init__(self, parent=None):
        """
        Initializes the image annotator view.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.

        Attributes:
            scene (QGraphicsScene): The graphics scene for displaying items.
            pixmap_item (QGraphicsPixmapItem | None): The current pixmap item displayed in the scene.
            scale_factor (float): The current scale factor for zooming.
            coord_label (QLabel | None): Label for displaying coordinates under the mouse cursor.
            quadrilateral_points (list[QPointF]): Points of the quadrilateral currently being drawn.
            quadrilaterals (list[list[QPointF]]): List of completed quadrilaterals, each as a list of points.
            selected_quadrilateral (list[QPointF] | None): The currently selected quadrilateral, if any.
            dragging_point (int | None): Index of the point being dragged, if any.

        Sets up rendering hints, drag mode, mouse tracking, and initializes all relevant attributes for image annotation.
        """
        super().__init__(parent)
        # Initialize scene
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene: QGraphicsScene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item: QGraphicsPixmapItem |  None = None
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setMouseTracking(True)
        self.coord_label: QLabel | None = None
        self.zoom_label: QLabel | None = None

        # Scene parameters
        self.mode: ImageViewMode = ImageViewMode.NAVIGATE
        self.scale_factor: float = 1.0
        self.quadrilaterals: list[Quadrilateral] = []
        self.drawing_quadrilateral: Quadrilateral | None = None
        self.selected_quadrilateral_id: int | None = None
        self.dragging_point_id: int | None = None
    
    def reset_scene_parameters(self) -> None:
        """
        Resets the scene parameters to their default values.

        This method restores the scale factor to 1.0, clears all quadrilateral points and quadrilaterals,
        and resets any selected quadrilateral or dragging point. It is typically used to reinitialize
        the scene state, for example, when loading a new image or clearing the current selection.
        """
        self.resetTransform()
        self.mode = ImageViewMode.NAVIGATE
        self.scale_factor = 1.0
        self.quadrilaterals = []
        self.drawing_quadrilateral = None
        self.selected_quadrilateral_id = None
        self.dragging_point_id = None
        self.viewport().update()
        
        self.coord_label.setText("")
        self.zoom_label.setText("100 %")

    def get_nb_quadrilateral(self) -> int:
        return len(self.quadrilaterals)
    
    def get_selected_quadrilateral(self) -> Quadrilateral | None:
        if self.selected_quadrilateral_id is None:
            return None
        
        if not 0 <= self.selected_quadrilateral_id < self.get_nb_quadrilateral():
            return None
        
        return self.quadrilaterals[self.selected_quadrilateral_id]
    
    def delete_selected_quadrilateral(self) -> int:
        # check quadrilateral id value
        if self.selected_quadrilateral_id is None:
            return -1

        return self.delete_quadrilateral(self.selected_quadrilateral_id)
    
    def delete_quadrilateral(self, quadrilateral_id: int) -> int:
        # check quadrilateral id value
        if not 0 <= quadrilateral_id < self.get_nb_quadrilateral():
            return -1
        
        # Deletion
        del self.quadrilaterals[quadrilateral_id]
        # Clear selection
        self.selected_quadrilateral_id = None

        return 0

    def set_coord_label(self, label) -> None:
        """
        Sets the coordinate label for the annotator.

        Parameters:
            label: The label widget or object to be used for displaying coordinates.
        """
        self.coord_label = label

    def set_zoom_label(self, label) -> None:
        """
        Sets the zoom label for the annotator.

        Parameters:
            label: The label widget or object to be used for displaying zoom percentage.
        """
        self.zoom_label = label

    def load_image(self, pixmap: QPixmap) -> None:
        """
        Loads a new image into the view by adding the provided QPixmap to the scene.
        This method first closes any previously loaded image, then creates a new QGraphicsPixmapItem
        from the given pixmap and adds it to the scene. It also updates the scene rectangle to match
        the dimensions of the new image.
        Args:
            pixmap (QPixmap): The image to be displayed in the view.
        """
        # Close previous image 
        self.close_image()

        # Add new image
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(pixmap.rect()))

    def close_image(self) -> None:
        """
        Closes the currently displayed image by clearing the scene and resetting scene parameters.

        This method removes all items from the scene and restores any scene-related settings to their default state.
        """
        self.scene.clear()
        self.reset_scene_parameters()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Handles mouse wheel events to zoom in or out of the image view.

        When the user scrolls the mouse wheel, this method determines the direction of the scroll.
        If the wheel is scrolled upwards (positive angle delta), the view is zoomed in using the predefined ZOOM_IN_FACTOR.
        If the wheel is scrolled downwards (negative angle delta), the view is zoomed out using the predefined ZOOM_OUT_FACTOR.

        Args:
            event (QWheelEvent): The wheel event containing information about the scroll action.
        """
        if event.angleDelta().y() > 0:
            self.zoom_in_out(incremental_factor = self.ZOOM_IN_FACTOR)
        else:
            self.zoom_in_out(incremental_factor = self.ZOOM_OUT_FACTOR)

    def zoom_in_out(self, incremental_factor: float = 1.0) -> None:
        """
        Zooms the view in or out by a specified incremental factor.
        This method adjusts the current scale factor by multiplying it with the given
        incremental_factor. The new scale factor is constrained within the defined
        ZOOM_LOWER_LIMIT and ZOOM_UPPER_LIMIT. If the resulting scale factor is out of bounds,
        the method returns without making any changes. Otherwise, it updates the scale factor,
        refreshes any relevant labels, and applies the scaling transformation.

        Args:
            incremental_factor (float, optional): The factor by which to zoom in or out.
                Values greater than 1.0 zoom in, values less than 1.0 zoom out.
                Defaults to 1.0.
        """
        new_factor_scale: float = self.scale_factor * incremental_factor
        # Update scale factor and label
        if not self.ZOOM_LOWER_LIMIT <= new_factor_scale <= self.ZOOM_UPPER_LIMIT:
            return
        
        self.scale_factor = new_factor_scale
        self.update_labels()
        self.scale(incremental_factor, incremental_factor)

    def update_labels(self, mouse_position: QPointF | None = None) -> None:
        """
        Updates the coordinate and zoom labels in the UI.

        If a mouse position is provided and the coordinate label exists, updates the coordinate label
        to display the current mouse position in pixels. Always updates the zoom label to display the
        current zoom level as a percentage.

        Args:
            mouse_position (QPointF | None, optional): The current mouse position in scene coordinates.
                If None, the coordinate label is not updated.
        """
        if (self.coord_label is not None) and (mouse_position is not None):
            self.coord_label.setText(f"{int(mouse_position.x())}, {int(mouse_position.y())} px")
        if self.zoom_label is not None:
            self.zoom_label.setText(f"{int(self.scale_factor * 100)} %")

    def set_mode(self, mode: ImageViewMode) -> None:
        """
        Sets the current interaction mode for the image view.

        Args:
            mode (ImageViewMode): The mode to set for the image view. If set to
                ImageViewMode.NAVIGATE, enables scroll hand drag mode for navigation.
                Otherwise, disables drag mode.

        """
        self.mode = mode
        if mode == ImageViewMode.NAVIGATE:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        # Reset drawing and modification
        self.drawing_quadrilateral = None
        self.selected_quadrilateral_id = None
        self.dragging_point_id = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse move events within the image view.
        Updates the mouse position labels and, if in MODIFY_quadrilateral mode, allows dragging and modifying
        points of a selected quadrilateral. The method also ensures the viewport is updated to reflect changes
        and calls the parent class's mouseMoveEvent for default behavior.
        Args:
            event (QMouseEvent): The mouse move event containing position and state information.
        """
        # Get mouse positions and update labels
        mouse_position: QPointF = self.mapToScene(event.position().toPoint())
        self.update_labels(mouse_position=mouse_position)

        match(self.mode):
            case ImageViewMode.NAVIGATE:
                # Do nothing
                pass
            case ImageViewMode.DRAW:
                # Do noting
                # TODO : quadrilateral previsualisations
                pass
            case ImageViewMode.MODIFY:
                selected_quadrilateral: Quadrilateral | None = self.get_selected_quadrilateral()
                if selected_quadrilateral is not None and self.dragging_point_id is not None:
                    ret = selected_quadrilateral.update_point(
                        point_id=self.dragging_point_id,
                        new_point_value=mouse_position
                    )
                self.viewport().update()

        # Call the parent class
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """
        Handles mouse press events for the image view, enabling navigation, drawing, and modification of quadrilaterals.
        Depending on the current mode (`self.mode`), this method performs the following actions:
            - NAVIGATE: No action is taken.
            - DRAW: 
                - On left mouse button press, starts or continues drawing a quadrilateral by adding points.
                - Completes and stores the quadrilateral when all points are added.
                - On right mouse button press, cancels the current quadrilateral drawing.
            - MODIFY:
                - On left mouse button press, selects a quadrilateral or initiates dragging of a corner point if clicked near one.
        Updates the mouse position labels, refreshes the viewport, and calls the parent class implementation.
        Args:
            event (QMouseEvent): The mouse event containing information about the button pressed and cursor position.
        """
        # Get mouse positions and update labels
        mouse_position: QPointF = self.mapToScene(event.position().toPoint())
        self.update_labels(mouse_position=mouse_position)

        match(self.mode):
            case ImageViewMode.NAVIGATE:
                # Do nothing
                pass
            case ImageViewMode.DRAW:
                if event.button() == Qt.MouseButton.LeftButton:
                    # Create new quadrilateral if not existing
                    if self.drawing_quadrilateral is None:
                        self.drawing_quadrilateral = Quadrilateral()
                    # Add point to quadrilateral
                    self.drawing_quadrilateral.append_point_to_quadrilateral(new_point=mouse_position)
                    # Add quadrilateral to the list of quadrilateral
                    if self.drawing_quadrilateral.drawing_complete:
                        self.quadrilaterals.append(self.drawing_quadrilateral)
                        self.drawing_quadrilateral = None
                elif event.button() == Qt.MouseButton.RightButton:
                    # Clear drawing quadrilateral is right button is clicked
                    self.drawing_quadrilateral = None
                else:
                    pass
                    
            case ImageViewMode.MODIFY:
                if event.button() == Qt.MouseButton.LeftButton:
                    clicked_quadrilateral_id: int | None = self.get_clicked_quadrilateral(point=mouse_position)
                    selected_quadrilateral: Quadrilateral | None = self.get_selected_quadrilateral()

                    # Select quadrilateral if no quadrilateral is selected
                    if selected_quadrilateral is None:
                        self.selected_quadrilateral_id = clicked_quadrilateral_id
                    else:
                        # Check if a corner of the currently selected quadrilateral is clicked
                        corner_id: int | None = selected_quadrilateral.find_close_corner(point=mouse_position)
                        if corner_id is not None:
                            self.dragging_point_id = corner_id
                        else:
                            # Select quadrilateral if no corner is near
                            self.selected_quadrilateral_id = clicked_quadrilateral_id

        # Update view
        self.viewport().update()

        # Call the parent class
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Handles the mouse release event.

        Resets the dragging point state by setting `dragging_point_id` to None,
        and then calls the base class implementation to ensure default behavior.

        Args:
            event (QMouseEvent): The mouse release event object.
        """
        self.dragging_point_id = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """
        Handles key press events in the image view.
        If the 'Delete' or 'Backspace' key is pressed and a quadrilateral is selected,
        deletes the selected quadrilateral from the list and updates the view.
        """
        match event.key():
            case Qt.Key.Key_Delete | Qt.Key.Key_Backspace:
                    self.delete_selected_quadrilateral()
                    self.viewport().update()
            case _:
                super().keyPressEvent(event)

    def get_clicked_quadrilateral(self, point: QPointF) -> int | None:
        """
        Returns the index of the quadrilateral that contains the given point.
        First, checks if the point is inside the currently selected quadrilateral.
        If so, returns its index. Otherwise, iterates through all other quadrilaterals
        and returns the index of the first one that contains the point.
        Args:
            point (QPointF): The point to check.
        Returns:
            int | None: The index of the quadrilateral containing the point, or None if none are found.
        """
        # Check if point is in currently selected quadrilateral
        selected_quadrilateral: Quadrilateral =  self.get_selected_quadrilateral()
        if selected_quadrilateral is not None:
            if selected_quadrilateral.is_point_in_quadrilateral(point):
                return self.selected_quadrilateral_id
            
        for i, quadrilateral in enumerate(self.quadrilaterals):
            # Avoid repeating this check 
            if i == self.selected_quadrilateral_id:
                continue

            if quadrilateral.is_point_in_quadrilateral(point):
                return i
            
        return None


    def drawForeground(self, painter, rect):
        """
        Draws the foreground elements on the scene, including finished and unfinished quadrilaterals.
        This method visualizes all quadrilaterals stored in `self.quadrilaterals`, highlighting the selected one,
        and draws their corner points with different styles depending on their selection state. It also draws the
        currently drawn (unfinished) quadrilateral, if any, with a distinct style.
        Args:
            painter (QPainter): The painter object used for drawing.
            rect (QRectF): The rectangle area to be painted (not directly used in this method).
        Visual Elements:
            - Finished quadrilaterals: Drawn as closed polylines with corner points.
            - Selected quadrilateral: Uses special pen and brush for highlighting.
            - Unfinished quadrilateral: Drawn as an open polyline with distinct points.
        """
        # Draw finished quadrilaterals
        for quadrilateral_id, quadrilateral in enumerate(self.quadrilaterals):
            quadrilateral_points: list[QPointF] = quadrilateral.quadrilateral_points

            # Set pen and brush
            if quadrilateral_id == self.selected_quadrilateral_id:
                ellipse_size: int = self.SELECTED_POINT_SIZE
                painter.setBrush(self.COLOR_SELECTED_QUADRILATERAL_POINTS)
                painter.setPen(self.PEN_SELECTED_QUADRILATERAL)
            else:
                ellipse_size: int = self.UNSELECTED_POINT_SIZE
                painter.setBrush(self.COLOR_UNSELECTED_QUADRILATERAL_POINTS)
                painter.setPen(self.PEN_UNSELECTED_QUADRILATERAL)

            # Draw quadrilateral and points
            painter.drawPolyline(quadrilateral_points + [quadrilateral_points[0]])
            for point in quadrilateral_points:
                painter.drawEllipse(point, ellipse_size, ellipse_size)
        
        
        # Draw unfinished quadrilateral
        if self.drawing_quadrilateral is not None:
            quadrilateral_points = self.drawing_quadrilateral.quadrilateral_points

            painter.setPen(self.PEN_DRAWING_QUADRILATERAL)
            painter.setBrush(self.COLOR_DRAWING_QUADRILATERAL_POINTS)

            painter.drawPolyline(quadrilateral_points)
            for pt in quadrilateral_points:
                painter.drawEllipse(pt, self.DRAWING_POINT_SIZE, self.DRAWING_POINT_SIZE)