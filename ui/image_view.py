from enum import Enum

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMainWindow
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent, QCursor
from PyQt6.QtCore import Qt, QPointF, QRectF

from ui.utils.Quadrilateral import Quadrilateral
from ui.button_row import ButtonRowMode

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

    def __init__(self, main_window, parent=None):
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
        self.main_window: QMainWindow = main_window

        # Scene parameters
        self.mode: ButtonRowMode = ButtonRowMode.EDIT
        self.scale_factor: float = 1.0
        self.quadrilaterals: list[Quadrilateral] = []
        self.drawing_quadrilateral: Quadrilateral | None = None
        self.selected_quadrilateral_id: int | None = None
        self.dragging_quadrilateral: bool = False
        self.dragging_point_id: int | None = None
        self.last_mouse_pos: QPointF | None = None

    def reset_drawing(self) -> None:
        """
        Resets the current drawing quadrilateral to None.

        This method clears any existing quadrilateral selection or drawing state,
        effectively resetting the drawing overlay in the image view.
        """
        self.drawing_quadrilateral = None

    def reset_modification(self) -> None:
        """
        Resets the modification state of the image view.

        This method clears any ongoing dragging operations, including point dragging,
        quadrilateral dragging, and the last recorded mouse position.
        """
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.unsetCursor()
        self.dragging_point_id = None
        self.dragging_quadrilateral = False
        self.last_mouse_pos = None
 
    def reset_all(self) -> None:
        """
        Resets the image view to its initial state.

        This method performs the following actions:
            - Resets the view transformation to default.
            - Sets the interaction mode to navigation.
            - Resets the scale factor to 1.0.
            - Clears all drawn quadrilaterals.
            - Resets any ongoing drawing or modification actions.
            - Deselects any selected quadrilateral.
            - Updates the viewport and main window labels to reflect the reset state.
        """
        self.resetTransform()
        self.mode = ButtonRowMode.EDIT
        self.scale_factor = 1.0
        self.quadrilaterals = []
        self.reset_drawing()
        self.reset_modification()
        self.set_selected_quadrilateral(quadrilateral_id=None)
        self.viewport().update()
        self.main_window.update_labels(mouse_position = None, scale_factor = 1.0)

    def get_nb_quadrilateral(self) -> int:
        """
        Returns the number of quadrilaterals currently stored.

        Returns:
            int: The count of quadrilaterals in the collection.
        """
        return len(self.quadrilaterals)

    def delete_selected_quadrilateral(self) -> int:
        """
        Deletes the currently selected quadrilateral from the view.
        Returns:
            int: The result of the deletion operation. Returns -1 if no quadrilateral is selected,
            otherwise returns the result of `delete_quadrilateral` with the selected quadrilateral's ID.
        """
        # check quadrilateral id value
        if self.selected_quadrilateral_id is None:
            return -1

        return self.delete_quadrilateral(self.selected_quadrilateral_id)
    
    def delete_quadrilateral(self, quadrilateral_id: int) -> int:
        """
        Deletes a quadrilateral from the list by its ID.
        Args:
            quadrilateral_id (int): The index of the quadrilateral to delete.
        Returns:
            int: 0 if the deletion was successful, -1 if the ID is invalid.
        Side Effects:
            Removes the specified quadrilateral from self.quadrilaterals.
            Clears the current selection by setting self.selected_quadrilateral_id to None.
        """
        # check quadrilateral id value
        if not 0 <= quadrilateral_id < self.get_nb_quadrilateral():
            return -1
        
        # Deletion
        del self.quadrilaterals[quadrilateral_id]
        # Clear selection
        self.selected_quadrilateral_id = None

        return 0
    
    def add_drawing_quadrilateral(self) -> int:
        """
        Adds the currently drawn quadrilateral to the list of quadrilaterals.

        Returns:
            int: 0 if the quadrilateral was successfully added, -1 if there was no quadrilateral to add.
        """
        if self.drawing_quadrilateral is not None:
            self.quadrilaterals.append(self.drawing_quadrilateral)
        else:
            return -1
        self.drawing_quadrilateral = None
        return 0

    def set_selected_quadrilateral(self, quadrilateral_id: int | None) -> None:
        """
        Sets the currently selected quadrilateral by its ID.

        Resets any ongoing modifications before updating the selected quadrilateral.
        If `quadrilateral_id` is None, deselects any currently selected quadrilateral.

        Args:
            quadrilateral_id (int | None): The ID of the quadrilateral to select, or None to deselect.
        """
        self.reset_modification()
        self.selected_quadrilateral_id = quadrilateral_id
      
    def get_selected_quadrilateral(self) -> Quadrilateral | None:
        """
        Returns the currently selected quadrilateral if a valid selection exists.
        Returns:
            Quadrilateral | None: The selected Quadrilateral object if the selection is valid,
            otherwise None.
        """
        if self.selected_quadrilateral_id is None:
            return None
        
        if not 0 <= self.selected_quadrilateral_id < self.get_nb_quadrilateral():
            return None
        
        return self.quadrilaterals[self.selected_quadrilateral_id]
     
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
        self.reset_all()

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
        new_scale_factor: float = self.scale_factor * incremental_factor
        # Update scale factor and label
        if not self.ZOOM_LOWER_LIMIT <= new_scale_factor <= self.ZOOM_UPPER_LIMIT:
            return
        
        self.scale_factor = new_scale_factor
        self.main_window.update_labels(scale_factor=new_scale_factor)
        self.scale(incremental_factor, incremental_factor)

    def is_point_in_quadrilateral(self, point: QPointF) -> int | None:
        """
        Determines if a given point lies within any of the quadrilaterals.
        Checks first if the point is inside the currently selected quadrilateral.
        If not, iterates through all other quadrilaterals to check if the point is inside any of them.
        Args:
            point (QPointF): The point to check.
        Returns:
            int | None: The index of the quadrilateral containing the point, or None if the point is not inside any quadrilateral.
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
    
    def get_selected_quadrilateral_close_corner(self, point: QPointF) -> None:
        """
        Returns the index of the corner of the currently selected quadrilateral that is closest to the given point.
        Args:
            point (QPointF): The point to compare against the corners of the selected quadrilateral.
        Returns:
            int | None: The index of the closest corner if a quadrilateral is selected and a close corner is found, otherwise None.
        """
        close_corner: int | None = None
        selected_quadrilateral: Quadrilateral =  self.get_selected_quadrilateral()
        if selected_quadrilateral is not None:
            close_corner = selected_quadrilateral.find_close_corner(point=point)
        
        return close_corner


    def set_mode(self, mode: ButtonRowMode) -> None:
        """
        Sets the current mode of the image view and resets relevant state.
        Args:
            mode (ButtonRowMode): The mode to set for the image view.
        Side Effects:
            - Updates the internal mode state.
            - Resets any ongoing drawing actions.
            - Clears the currently selected quadrilateral.
            - Triggers a viewport update to reflect changes.
        """
        # Set mode
        self.mode = mode
        
        # Reset drawing and modification
        self.reset_drawing()
        self.set_selected_quadrilateral(quadrilateral_id=None)

        # Update view
        self.viewport().update()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Handles mouse wheel events to zoom in or out of the image view.

        When the user scrolls the mouse wheel, this method determines the direction of the scroll.
        If the wheel is scrolled upwards (strictly positive angle delta), the view is zoomed in using the predefined ZOOM_IN_FACTOR.
        If the wheel is scrolled downwards (strictly negative angle delta), the view is zoomed out using the predefined ZOOM_OUT_FACTOR.

        Args:
            event (QWheelEvent): The wheel event containing information about the scroll action.
        """
        if event.angleDelta().y() > 0:
            self.zoom_in_out(incremental_factor = self.ZOOM_IN_FACTOR)
        elif event.angleDelta().y() < 0:
            self.zoom_in_out(incremental_factor = self.ZOOM_OUT_FACTOR)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse movement events within the image view.
        Updates the mouse position labels in the main window and manages interactive behaviors
        depending on the current mode (DRAW or EDIT). In EDIT mode, allows for dragging and editing
        of quadrilaterals, including moving points or the entire shape, and updates the cursor
        appearance based on proximity to corners or hovered quadrilaterals.
        Args:
            event (QMouseEvent): The mouse move event containing the current mouse position and state.
        Side Effects:
            - Updates labels in the main window with the current mouse position.
            - Modifies quadrilateral geometry if dragging is in progress.
            - Changes the cursor shape when hovering over interactive elements.
            - Triggers a viewport update to reflect any changes.
            - Calls the parent class's mouseMoveEvent for default handling.
        """
        # Get mouse positions and update labels
        mouse_position: QPointF = self.mapToScene(event.position().toPoint())
        self.main_window.update_labels(mouse_position=mouse_position)

        match(self.mode):
            case ButtonRowMode.DRAW:
                # Do noting
                # TODO : quadrilateral previsualisations
                pass
            case ButtonRowMode.EDIT:
                # Get selected quadrilateral
                selected_quadrilateral: Quadrilateral | None = self.get_selected_quadrilateral()

                if selected_quadrilateral is not None:
                    # Dragging point defined -> Update point
                    if self.dragging_point_id is not None:
                        selected_quadrilateral.update_point(
                            point_id=self.dragging_point_id,
                            new_point_value=mouse_position
                        )
                    # Drag quadrilateral if flag is raised
                    elif self.dragging_quadrilateral and self.last_mouse_pos is not None:
                        delta: QPointF = mouse_position - self.last_mouse_pos
                        selected_quadrilateral.move_delta(delta)
                        self.last_mouse_pos = mouse_position
                    # Change cursor if corner is near or selected quadrilateral is hover
                    else:
                        hovered_selected_quadrilateral: bool = self.is_point_in_quadrilateral(point=mouse_position) == self.selected_quadrilateral_id
                        is_corner_close: bool = self.get_selected_quadrilateral_close_corner(point=mouse_position) != None

                        # Change cursor
                        if hovered_selected_quadrilateral or is_corner_close:
                            self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
                        else:
                            self.unsetCursor()
        
        # Update view
        self.viewport().update()

        # Call the parent class
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        # Get mouse positions and update labels
        mouse_position: QPointF = self.mapToScene(event.position().toPoint())
        self.main_window.update_labels(mouse_position=mouse_position)

        match(self.mode):
            case ButtonRowMode.DRAW:
                if event.button() == Qt.MouseButton.LeftButton:
                    # Create new quadrilateral if not existing
                    if self.drawing_quadrilateral is None:
                        self.drawing_quadrilateral = Quadrilateral()
                    # Add point to quadrilateral
                    self.drawing_quadrilateral.append_point_to_quadrilateral(new_point=mouse_position)
                    # Add quadrilateral to the list of quadrilateral
                    if self.drawing_quadrilateral.drawing_complete:
                        self.add_drawing_quadrilateral()
                elif event.button() == Qt.MouseButton.RightButton:
                    # Clear drawing quadrilateral is right button is clicked
                    self.reset_drawing()
                else:
                    pass
                    
            case ButtonRowMode.EDIT:
                if event.button() == Qt.MouseButton.LeftButton:
                    clicked_quadrilateral_id: int | None = self.is_point_in_quadrilateral(point=mouse_position)
                    clicked_corner_id: int | None = self.get_selected_quadrilateral_close_corner(point=mouse_position)

                    # No quadrilateral and corner clicked -> Set drag mode
                    if clicked_corner_id is None and clicked_quadrilateral_id is None:
                        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                    # Click corner -> drag corner
                    elif clicked_corner_id is not None:
                        self.dragging_point_id = clicked_corner_id
                        self.dragging_quadrilateral = False
                        self.last_mouse_pos = None
                        self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    # Click selected quadrilateral -> move quadrilateral
                    elif clicked_quadrilateral_id == self.selected_quadrilateral_id:
                        # Start dragging the whole quadrilateral if selected quadrilateral is once again clicked
                        self.dragging_point_id = None
                        self.dragging_quadrilateral = True
                        self.last_mouse_pos = mouse_position
                        self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                    # Change selection
                    else:
                        self.set_selected_quadrilateral(quadrilateral_id=clicked_quadrilateral_id)

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
        self.reset_modification()
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