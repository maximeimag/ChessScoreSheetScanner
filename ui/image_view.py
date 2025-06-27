from enum import Enum

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMainWindow
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent, QCursor
from PyQt6.QtCore import Qt, QPointF, QRectF

from ui.utils.Quadrilateral import Quadrilateral
from ui.button_row import ButtonRowMode

class ImageView(QGraphicsView):
    """
    ImageView is a custom QGraphicsView subclass for displaying and interacting with images and annotated quadrilaterals.
    This class provides a graphical interface for loading images, drawing and editing quadrilaterals, and handling user interactions such as mouse and keyboard events. It supports two primary modes: DRAW (for creating new quadrilaterals) and EDIT (for selecting and modifying existing quadrilaterals). The view supports zooming, panning, and visual feedback for selection and editing actions.
    Attributes:
        ZOOM_LOWER_LIMIT (float): Minimum allowed zoom scale.
        ZOOM_UPPER_LIMIT (float): Maximum allowed zoom scale.
        ZOOM_IN_FACTOR (float): Factor by which to zoom in.
        ZOOM_OUT_FACTOR (float): Factor by which to zoom out.
        main_window (QMainWindow): Reference to the main application window.
        scene (QGraphicsScene): The graphics scene for displaying items.
        pixmap_item (QGraphicsPixmapItem | None): The currently loaded image item.
        image_loaded (bool): Flag indicating if an image is loaded.
        mode (ButtonRowMode): Current interaction mode (DRAW or EDIT).
        scale_factor (float): Current zoom scale factor.
        quadrilaterals (list[Quadrilateral]): List of annotated quadrilaterals.
        drawing_quadrilateral (Quadrilateral | None): The quadrilateral currently being drawn.
        selected_quadrilateral_id (int | None): Index of the currently selected quadrilateral.
        dragging_quadrilateral (bool): Flag indicating if a quadrilateral is being dragged.
        dragging_point_id (int | None): Index of the corner point being dragged.
        last_mouse_pos (QPointF | None): Last recorded mouse position.
    Methods:
        reset_edit(): Resets selection and editing state.
        reset_drawing_and_edit(): Resets drawing and editing state.
        reset_all(): Resets the entire view to its initial state.
        get_nb_quadrilateral() -> int: Returns the number of quadrilaterals.
        delete_selected_quadrilateral() -> int: Deletes the currently selected quadrilateral.
        delete_quadrilateral(quadrilateral_id: int) -> int: Deletes a quadrilateral by its ID.
        update_quadrilateral_ids(): Updates the IDs of all quadrilaterals.
        add_drawing_quadrilateral() -> int: Adds the currently drawn quadrilateral to the list.
        set_selected_quadrilateral(quadrilateral_id: int | None): Sets the selected quadrilateral.
        unselect_all(): Deselects all quadrilaterals.
        get_selected_quadrilateral() -> Quadrilateral | None: Gets the currently selected quadrilateral.
        load_image(pixmap: QPixmap): Loads an image into the view.
        close_image(): Closes the currently loaded image and resets the view.
        zoom_in_out(incremental_factor: float = 1.0): Zooms the view in or out.
        is_point_in_quadrilateral(point: QPointF) -> int | None: Checks if a point is inside any quadrilateral.
        get_selected_quadrilateral_close_corner(point: QPointF) -> int | None: Finds the closest corner of the selected quadrilateral to a point.
        set_mode(target_mode: ButtonRowMode): Sets the interaction mode.
        wheelEvent(event: QWheelEvent): Handles mouse wheel events for zooming.
        on_settings_changed(): Updates the view when settings change.
        mouseMoveEvent(event: QMouseEvent): Handles mouse movement events.
        mousePressEvent(event: QMouseEvent): Handles mouse press events.
        mouseReleaseEvent(event): Handles mouse release events.
        keyPressEvent(event): Handles key press events.
        drawForeground(painter: QPainter, rect: QRectF): Draws quadrilaterals and overlays in the foreground.
    Usage:
        Instantiate ImageView within a PyQt application, providing a reference to the main window.
        Use the provided methods to load images, draw, select, and edit quadrilaterals, and handle user interactions.
    """
    ZOOM_LOWER_LIMIT: float = 0.2
    ZOOM_UPPER_LIMIT: float = 5.0

    ZOOM_IN_FACTOR: float = 1.05
    ZOOM_OUT_FACTOR: float = 1.0 / ZOOM_IN_FACTOR

    def __init__(self, main_window, parent=None):
        """
        Initializes the ImageView widget with the given main window and optional parent.
        Args:
            main_window (QMainWindow): Reference to the main application window.
            parent (QWidget, optional): Parent widget. Defaults to None.
        Attributes:
            main_window (QMainWindow): Reference to the main application window.
            scene (QGraphicsScene): The graphics scene for displaying items.
            pixmap_item (QGraphicsPixmapItem | None): The current pixmap item displayed, if any.
            image_loaded (bool): Indicates whether an image is loaded.
            mode (ButtonRowMode): Current mode of the scene (e.g., edit mode).
            scale_factor (float): Current scale factor for zooming.
            quadrilaterals (list[Quadrilateral]): List of drawn quadrilaterals.
            drawing_quadrilateral (Quadrilateral | None): Quadrilateral currently being drawn, if any.
            selected_quadrilateral_id (int | None): ID of the currently selected quadrilateral, if any.
            dragging_quadrilateral (bool): Whether a quadrilateral is being dragged.
            dragging_point_id (int | None): ID of the point being dragged, if any.
            last_mouse_pos (QPointF | None): Last recorded mouse position.
        """
        super().__init__(parent)
        # Main window
        self.main_window: QMainWindow = main_window

        # Initialize scene
        self.scene: QGraphicsScene = QGraphicsScene(self)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        self.setScene(self.scene)

        # Pixel map
        self.pixmap_item: QGraphicsPixmapItem |  None = None
        self.image_loaded: bool = False

        # Scene mode
        self.mode: ButtonRowMode = ButtonRowMode.EDIT

        # Display
        self.scale_factor: float = 1.0
        self.quadrilaterals: list[Quadrilateral] = []
        self.resetTransform()

        # Drawing
        self.drawing_quadrilateral: Quadrilateral | None = None

        # Selection and modification
        self.selected_quadrilateral_id: int | None = None
        self.dragging_quadrilateral: bool = False
        self.dragging_point_id: int | None = None
        self.last_mouse_pos: QPointF | None = None

        # Cursor and Drag initialization
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.unsetCursor()

        # Update view
        self.viewport().update()

    def reset_edit(self) -> None:
        """
        Resets the editing state of the image view.
        This method clears any current selections, disables dragging operations,
        resets the cursor to its default state, and updates the viewport to reflect
        these changes.
        """
        # Reset selection and modification
        self.unselect_all()
        self.dragging_quadrilateral = False
        self.dragging_point_id = None
        self.last_mouse_pos = None

        # Reset cursor and Drag initialization
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.unsetCursor()

        # Update view
        self.viewport().update()

    def reset_drawing_and_edit(self) -> None:
        """
        Resets the current drawing and editing states.
        This method clears any ongoing quadrilateral drawing operation and resets the edit state
        by calling the `reset_edit` method.
        """
        # Reset drawing
        self.drawing_quadrilateral = None

        # Reset edit
        self.reset_edit()
 
    def reset_all(self) -> None:
        """
        Resets the state of the image view to its default values.
        This includes:
            - Setting the main window mode to EDIT.
            - Resetting the display scale factor and clearing any quadrilaterals.
            - Resetting the transformation applied to the view.
            - Resetting drawing and editing states.
            - Updating the main window labels to reflect the reset state.
        Returns:
            None
        """
        # Reset scene mode
        self.main_window.set_mode(ButtonRowMode.EDIT)

        # Reset display
        self.scale_factor: float = 1.0
        self.quadrilaterals: list[Quadrilateral] = []
        self.resetTransform()

        # Reset drawing and edit
        self.reset_drawing_and_edit()

        # Reset labels
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

        # Update ids
        self.update_quadrilateral_ids()

        # Clear selection
        self.unselect_all()

        return 0
    
    def update_quadrilateral_ids(self) -> None:
        """
        Updates the 'quadrilateral_id' attribute for each quadrilateral in the 'quadrilaterals' list.

        Iterates through all quadrilaterals and assigns each one a unique ID based on its position in the list.
        This ensures that the 'quadrilateral_id' attribute is synchronized with the current order of the quadrilaterals.
        """
        for quadrilateral_id, quadrilateral in enumerate(self.quadrilaterals):
            quadrilateral.quadrilateral_id = quadrilateral_id
    
    def add_drawing_quadrilateral(self) -> int:
        """
        Adds the currently drawn quadrilateral to the list of quadrilaterals.

        Returns:
            int: 0 if the quadrilateral was successfully added, -1 if there was no quadrilateral to add.
        """
        if self.drawing_quadrilateral is not None:
            self.quadrilaterals.append(self.drawing_quadrilateral)
            self.update_quadrilateral_ids()
            self.main_window.set_mode(ButtonRowMode.EDIT)
        else:
            return -1
        self.drawing_quadrilateral = None
        return 0

    def set_selected_quadrilateral(self, quadrilateral_id: int | None) -> None:
        """
        Sets the selected quadrilateral by its ID.

        If the provided quadrilateral_id is None or out of valid range, all quadrilaterals are unselected.
        Otherwise, marks the quadrilateral with the given ID as selected and unselects all others.

        Args:
            quadrilateral_id (int | None): The ID of the quadrilateral to select, or None to unselect all.

        Returns:
            None
        """
        # Check id value
        if quadrilateral_id is None:
            self.unselect_all()
        elif not 0 <= quadrilateral_id < self.get_nb_quadrilateral():
            self.unselect_all()
        else:
            self.selected_quadrilateral_id = quadrilateral_id
            for id, quadrilateral in enumerate(self.quadrilaterals):
                quadrilateral.is_selected = id == quadrilateral_id
    
    def unselect_all(self):
        """
        Deselects all quadrilaterals by setting their 'is_selected' attribute to False
        and clears the currently selected quadrilateral ID.
        """
        self.selected_quadrilateral_id = None
        for quadrilateral in self.quadrilaterals:
            quadrilateral.is_selected = False
      
    def get_selected_quadrilateral(self) -> Quadrilateral | None:
        """
        Returns the currently selected quadrilateral if a valid selection exists.
        Returns:
            Quadrilateral | None: The selected Quadrilateral object if the selection is valid,
            otherwise None.
        """
        if self.selected_quadrilateral_id is None:
            return None
        
        return self.quadrilaterals[self.selected_quadrilateral_id]
     
    def load_image(self, pixmap: QPixmap) -> None:
        """
        Loads a new image into the view by adding the provided QPixmap to the scene.
        Closes any previously loaded image before displaying the new one. Updates the scene rectangle
        to match the dimensions of the new image and marks the image as loaded.
        Args:
            pixmap (QPixmap): The image to be displayed in the view.
        """
        # Close previous image 
        self.close_image()

        # Add new image
        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.pixmap_item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.image_loaded = True

    def close_image(self) -> None:
        """
        Closes the currently loaded image by clearing the scene, updating the image_loaded flag,
        and resetting all relevant state in the viewer.
        """
        self.scene.clear()
        self.image_loaded = False
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


    def set_mode(self, target_mode: ButtonRowMode) -> None:
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
        self.mode = target_mode
        
        # Reset drawing and modification
        self.reset_drawing_and_edit()
        self.unselect_all()

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

    def on_settings_changed(self) -> None:
        """
        Called when the settings are changed. Triggers an update of the viewport to reflect the new settings.
        """
        # Update view
        self.viewport().update()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse movement events within the image view.
        This method updates the UI and internal state based on the current mouse position and interaction mode.
        It performs the following actions:
            - If no image is loaded, delegates the event to the parent class.
            - Updates mouse position labels in the main window.
            - In DRAW mode: (currently does nothing, placeholder for future quadrilateral preview).
            - In EDIT mode:
                - If a quadrilateral is selected and a corner is being dragged, updates the corner position.
                - If the quadrilateral itself is being dragged, moves it according to the mouse delta.
                - Otherwise, updates the cursor to indicate interactivity if hovering over a corner or the selected quadrilateral.
            - Refreshes the viewport to reflect any changes.
            - Calls the parent class's mouseMoveEvent for default processing.
        Args:
            event (QMouseEvent): The mouse move event containing the new mouse position and state.
        """
        # Do not continue if no image is loaded
        if not self.image_loaded:
            return super().mouseMoveEvent(event)
        
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
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        Handles mouse press events for the image view.
        Depending on the current mode (DRAW or EDIT), this method processes mouse clicks to:
        - DRAW mode:
            - Left click: Add points to a new or existing quadrilateral. Finalizes and adds the quadrilateral when complete.
            - Right click: Clears the current drawing quadrilateral.
        - EDIT mode:
            - Left click: 
                - If clicking on a quadrilateral corner, enables dragging of that corner.
                - If clicking on the selected quadrilateral, enables dragging of the entire quadrilateral.
                - If clicking elsewhere, enables scroll/drag mode.
                - If clicking on a different quadrilateral, changes the selection.
        Also updates mouse position labels, refreshes the view, and calls the parent class implementation.
        Args:
            event (QMouseEvent): The mouse press event containing information about the mouse action.
        """
        # Do not continue if no image is loaded
        if not self.image_loaded:
            return super().mouseMoveEvent(event)
        
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
                    self.reset_drawing_and_edit()
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

    def mouseReleaseEvent(self, event) -> None:
        """
        Handles the mouse release event.

        Resets the dragging point state by setting `dragging_point_id` to None,
        and then calls the base class implementation to ensure default behavior.

        Args:
            event (QMouseEvent): The mouse release event object.
        """
        self.dragging_quadrilateral = False
        self.dragging_point_id = None
        self.last_mouse_pos = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
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

    def drawForeground(self, painter: QPainter, rect: QRectF):
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
        # Get grid settings from main window
        draw_cells: bool = self.main_window.settings_row.is_display_on()
        nb_internal_rows: int = self.main_window.settings_row.get_nb_quadrilateral_rows()
        nb_internal_cols: int = self.main_window.settings_row.get_nb_quadrilateral_cols()

        # Draw finished quadrilaterals
        for quadrilateral in self.quadrilaterals:
            quadrilateral.drawForeground(
                painter,
                rect,
                draw_cells=draw_cells,
                nb_internal_rows=nb_internal_rows,
                nb_internal_cols=nb_internal_cols
            )
        
        # Draw unfinished quadrilateral
        if self.drawing_quadrilateral is not None:
            self.drawing_quadrilateral.drawForeground(painter, rect)