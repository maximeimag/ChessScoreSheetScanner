from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor

class Quadrilateral:
    """
    A class representing a quadrilateral shape for interactive graphical applications.
    This class manages the state and behavior of a quadrilateral defined by four points.
    It provides methods for adding and updating points, checking if a point is inside the
    quadrilateral, moving the quadrilateral, computing its centroid, and rendering it
    using a QPainter. The class supports both in-progress (drawing) and completed states,
    and handles selection and visual feedback for user interaction.
    Attributes:
        NB_SIDE (int): Number of sides (corners) of the quadrilateral (always 4).
        CLOSE_POINT_DISTANCE (int): Pixel distance threshold for detecting proximity to a corner.
        COLOR_UNSELECTED_QUADRILATERAL_POINTS (QColor): Color for unselected quadrilateral points.
        COLOR_UNSELECTED_QUADRILATERAL_ID (QColor): Color for unselected quadrilateral ID text.
        PEN_UNSELECTED_QUADRILATERAL (QPen): Pen for drawing unselected quadrilateral outline.
        UNSELECTED_POINT_SIZE (int): Size of unselected corner points.
        COLOR_SELECTED_QUADRILATERAL_POINTS (QColor): Color for selected quadrilateral points.
        COLOR_SELECTED_QUADRILATERAL_ID (QColor): Color for selected quadrilateral ID text.
        PEN_SELECTED_QUADRILATERAL (QPen): Pen for drawing selected quadrilateral outline.
        SELECTED_POINT_SIZE (int): Size of selected corner points.
        COLOR_DRAWING_QUADRILATERAL_POINTS (QColor): Color for points while drawing.
        PEN_DRAWING_QUADRILATERAL (QPen): Pen for drawing in-progress quadrilateral.
        DRAWING_POINT_SIZE (int): Size of points while drawing.
    Instance Attributes:
        quadrilateral_points (list[QPointF]): List of QPointF objects representing the corners.
        drawing_complete (bool): True if the quadrilateral has four points and is complete.
        is_selected (bool): True if the quadrilateral is currently selected.
        quadrilateral_id (int | None): Optional identifier for the quadrilateral.
    Methods:
        find_close_corner(point: QPointF) -> int | None:
            Returns the index of a corner close to the given point, or None if none are close.
        append_point_to_quadrilateral(new_point: QPointF) -> int:
            Adds a new point if drawing is not complete and the point is not too close to existing corners.
        update_point(point_id: int, new_point_value: QPointF) -> int:
            Updates the value of a specific corner point.
        is_point_in_quadrilateral(point: QPointF) -> bool:
            Determines if a given point lies inside the quadrilateral using the ray casting algorithm.
        move_delta(delta: QPointF) -> None:
        get_centroid() -> QPointF | None:
            Calculates and returns the centroid of the quadrilateral.
        drawForeground(painter: QPainter, rect: QRectF):
            Draws the quadrilateral and its control points using the provided QPainter.
    """

    NB_SIDE: int = 4 
    CLOSE_POINT_DISTANCE: int = 10

    COLOR_UNSELECTED_QUADRILATERAL_POINTS: QColor = QColor(255, 255, 255)
    COLOR_UNSELECTED_QUADRILATERAL_ID: QColor = QColor(255, 0, 0)
    PEN_UNSELECTED_QUADRILATERAL: QPen = QPen(QColor(255, 0, 0), 2)
    UNSELECTED_POINT_SIZE: int = 5

    COLOR_SELECTED_QUADRILATERAL_POINTS: QColor = QColor(0, 255, 0)
    COLOR_SELECTED_QUADRILATERAL_ID: QColor = QColor(0, 255, 0)
    PEN_SELECTED_QUADRILATERAL: QPen = QPen(QColor(0, 255, 0), 2)
    SELECTED_POINT_SIZE: int = 7

    COLOR_DRAWING_QUADRILATERAL_POINTS: QColor = QColor(0, 0, 255)
    PEN_DRAWING_QUADRILATERAL: QPen = QPen(QColor(0, 0, 255), 2, Qt.PenStyle.DashLine)
    DRAWING_POINT_SIZE: int = 7

    def __init__(self):
        """
        Initializes a Quadrilateral object with default values.
        Attributes:
            quadrilateral_points (list[QPointF]): List of points defining the quadrilateral.
            drawing_complete (bool): Flag indicating if the quadrilateral drawing is complete.
            is_selected (bool): Flag indicating if the quadrilateral is currently selected.
            quadrilateral_id (int | None): Optional identifier for the quadrilateral.
        """
        # Quadrilateral points
        self.quadrilateral_points: list[QPointF] = []

        # Quadrilateral flags
        self.drawing_complete: bool = False
        self.is_selected: bool = False

        # ID 
        self.quadrilateral_id: int | None = None

    def find_close_corner(self, point: QPointF) -> int | None:
        """
        Finds the index of the corner in the quadrilateral that is within a certain distance from the given point.

        Args:
            point (QPointF): The point to check proximity against the quadrilateral's corners.

        Returns:
            int | None: The index of the close corner if found within CLOSE_POINT_DISTANCE, otherwise None.
        """
        close_point_id: int | None = None
        quadrilateral_point: QPointF
        for point_id, quadrilateral_point in enumerate(self.quadrilateral_points):
            if (point - quadrilateral_point).manhattanLength() < self.CLOSE_POINT_DISTANCE:
                close_point_id = point_id
                break
        return close_point_id
    
    def append_point_to_quadrilateral(self, new_point: QPointF) -> int:
        """
        Appends a new point to the quadrilateral if drawing is not complete and the point is not too close to existing corners.
        Args:
            new_point (QPointF): The point to be added to the quadrilateral.
        Returns:
            int: -1 if the drawing is complete or the new point is too close to an existing corner; otherwise, None.
        """
        # Check if drawing is competed
        if self.drawing_complete:
            return -1

        # Check if new point is near another point in the quadrilateral
        close_point_id = self.find_close_corner(new_point)
        if close_point_id is not None:
            return -1

        # Add point
        self.quadrilateral_points.append(new_point)

        # Raise flag if enough points are in the list
        if len(self.quadrilateral_points) == self.NB_SIDE:
            self.drawing_complete = True
    
    def update_point(self, point_id: int, new_point_value: QPointF) -> int:
        """
        Updates the value of a specific point in the quadrilateral.
        Args:
            point_id (int): The index of the point to update (must be between 0 and NB_SIDE - 1).
            new_point_value (QPointF): The new value to assign to the specified point.
        Returns:
            int: 0 if the point was successfully updated, -1 if the operation failed due to
                incomplete drawing or invalid point_id.
        """
        # Check flags
        if not self.drawing_complete:
            return -1
        
        # Check point id value
        if not 0 <= point_id < self.NB_SIDE:
            return -1
        
        # Modify point
        self.quadrilateral_points[point_id] = new_point_value

        return 0

    def is_point_in_quadrilateral(self, point: QPointF) -> bool:
        """
        Determines whether a given point lies inside the quadrilateral defined by the object's points.
        Uses the ray casting algorithm to check if the point is inside the quadrilateral.
        Returns False if the quadrilateral is not fully defined (drawing not complete).
        Args:
            point (QPointF): The point to test for inclusion within the quadrilateral.
        Returns:
            bool: True if the point is inside the quadrilateral, False otherwise.
        """
        if not self.drawing_complete:
            return False
        
        inside = False
        x, y = point.x(), point.y()
        points = self.quadrilateral_points

        p1x, p1y = points[0].x(), points[0].y()

        for i in range(self.NB_SIDE+1):
            p2x, p2y = points[i % self.NB_SIDE].x(), points[i % self.NB_SIDE].y()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def move_delta(self, delta: QPointF) -> None:
        """
        Moves all points of the quadrilateral by the specified delta.

        Args:
            delta (QPointF): The amount to move each point, represented as a QPointF.

        Returns:
            None
        """
        for i, point in enumerate(self.quadrilateral_points):
            self.update_point(i, point + delta)

    def get_centroid(self) -> QPointF | None:
        """
        Calculates and returns the centroid (geometric center) of the quadrilateral.
        Returns:
            QPointF | None: The centroid as a QPointF object if the quadrilateral drawing is complete;
            otherwise, returns None.
        """
        if not self.drawing_complete:
            return None

        cx = sum(pt.x() for pt in self.quadrilateral_points) / self.NB_SIDE
        cy = sum(pt.y() for pt in self.quadrilateral_points) / self.NB_SIDE
        return QPointF(cx, cy)

    def drawForeground(self, painter: QPainter, rect: QRectF):
        """
        Draws the quadrilateral and its control points on the given QPainter.
        This method handles both the completed and in-progress (unfinished) states of the quadrilateral:
        - If the quadrilateral drawing is complete, it draws the quadrilateral outline, its corner points,
          and the quadrilateral's numeric ID at its centroid. The appearance (pen, brush, point size, and colors)
          depends on whether the quadrilateral is currently selected.
        - If the quadrilateral is still being drawn (not complete), it draws the current polyline and its points
          using the drawing style.
        Args:
            painter (QPainter): The painter object used for rendering.
            rect (QRectF): The rectangle area in which to draw.
        """
        if self.drawing_complete:
            # Set pen and brush
            if self.is_selected:
                ellipse_size: int = self.SELECTED_POINT_SIZE
                painter.setBrush(self.COLOR_SELECTED_QUADRILATERAL_POINTS)
                painter.setPen(self.PEN_SELECTED_QUADRILATERAL)
            else:
                ellipse_size: int = self.UNSELECTED_POINT_SIZE
                painter.setBrush(self.COLOR_UNSELECTED_QUADRILATERAL_POINTS)
                painter.setPen(self.PEN_UNSELECTED_QUADRILATERAL)

            # Draw quadrilateral and points
            painter.drawPolyline(self.quadrilateral_points + [self.quadrilateral_points[0]])
            for point in self.quadrilateral_points:
                painter.drawEllipse(point, ellipse_size, ellipse_size)

            # Draw quadrilateral numeral ID at centroid
            centroid: QPointF = self.get_centroid()
            if (self.quadrilateral_id is not None) and (centroid is not None):
                painter.setPen(
                    self.COLOR_SELECTED_QUADRILATERAL_ID if self.is_selected else self.COLOR_UNSELECTED_QUADRILATERAL_ID
                )  # Black text for visibility
                painter.drawText(centroid, str(self.quadrilateral_id + 1))
        
        # Draw unfinished quadrilateral
        else:
            painter.setPen(self.PEN_DRAWING_QUADRILATERAL)
            painter.setBrush(self.COLOR_DRAWING_QUADRILATERAL_POINTS)

            painter.drawPolyline(self.quadrilateral_points)
            for pt in self.quadrilateral_points:
                painter.drawEllipse(pt, self.DRAWING_POINT_SIZE, self.DRAWING_POINT_SIZE)