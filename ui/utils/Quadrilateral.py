from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor

class Quadrilateral:
    """
    A class representing a 2D quadrilateral with interactive editing and drawing capabilities.
    This class manages the geometric properties and interactive state of a quadrilateral defined by four points.
    It provides methods for constructing the quadrilateral point by point, ensuring convexity, updating points,
    testing point inclusion, moving the shape, and rendering it using Qt's QPainter.
        NB_SIDE (int): Number of sides/corners in a quadrilateral (constant: 4).
        CLOSE_POINT_DISTANCE (int): Pixel distance threshold for detecting proximity to a corner.
        COLOR_UNSELECTED_QUADRILATERAL_POINTS (QColor): Color for unselected quadrilateral corner points.
        COLOR_UNSELECTED_QUADRILATERAL_ID (QColor): Color for unselected quadrilateral ID text.
        PEN_UNSELECTED_QUADRILATERAL (QPen): Pen for drawing unselected quadrilateral outline.
        UNSELECTED_POINT_SIZE (int): Size of unselected corner points.
        COLOR_SELECTED_QUADRILATERAL_POINTS (QColor): Color for selected quadrilateral corner points.
        COLOR_SELECTED_QUADRILATERAL_ID (QColor): Color for selected quadrilateral ID text.
        PEN_SELECTED_QUADRILATERAL (QPen): Pen for drawing selected quadrilateral outline.
        SELECTED_POINT_SIZE (int): Size of selected corner points.
        COLOR_DRAWING_QUADRILATERAL_POINTS (QColor): Color for corner points while drawing.
        PEN_DRAWING_QUADRILATERAL (QPen): Pen for drawing the quadrilateral in progress.
        DRAWING_POINT_SIZE (int): Size of corner points while drawing.
    Instance Attributes:
        quadrilateral_points (list[QPointF]): List of QPointF objects defining the quadrilateral corners.
        drawing_complete (bool): True if the quadrilateral has four points and is finalized.
        is_selected (bool): True if the quadrilateral is currently selected in the UI.
    Methods:
        __init__():
            Initializes a new Quadrilateral with default state.
        find_close_corner(point: QPointF) -> int | None:
            Returns the index of a corner close to the given point, or None if none are close.
        is_convex(points: list[QPointF]) -> bool:
            Static method to check if a list of four points forms a convex quadrilateral.
        append_point_to_quadrilateral(new_point: QPointF) -> int:
            Attempts to add a new point to the quadrilateral, enforcing proximity and convexity constraints.
        update_point(point_id: int, new_point_value: QPointF) -> int:
            Updates the position of a specified corner, ensuring the quadrilateral remains convex.
        is_point_in_quadrilateral(point: QPointF) -> bool:
            Determines if a given point lies inside the quadrilateral using the ray casting algorithm.
        move_delta(delta: QPointF) -> None:
            Moves all corners of the quadrilateral by the specified delta.
        get_centroid() -> QPointF | None:
            Calculates and returns the centroid of the quadrilateral if it is complete.
        drawForeground(painter: QPainter, rect: QRectF):
            Renders the quadrilateral and its control points using the provided QPainter, with different
            styles for selected, unselected, and in-progress states.
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

    @staticmethod
    def is_convex(points: list[QPointF]) -> bool:
        """
        Checks if the given list of 4 points forms a convex quadrilateral.
        Args:
            points (list[QPointF]): List of 4 points.
        Returns:
            bool: True if convex, False otherwise.
        """
        # Check length
        if len(points) != 4:
            return False
        # 2D cross product
        def cross(a, b, c):
            abx, aby = b.x() - a.x(), b.y() - a.y()
            bcx, bcy = c.x() - b.x(), c.y() - b.y()
            return abx * bcy - aby * bcx
        # Check if cross product are all negative or all positive
        signs = []
        for i in range(4):
            z = cross(points[i], points[(i+1)%4], points[(i+2)%4])
            signs.append(z > 0)
        return all(signs) or not any(signs)
    
    def append_point_to_quadrilateral(self, new_point: QPointF) -> int:
        """
        Attempts to append a new point to the quadrilateral being constructed.
        This method checks several conditions before adding the new point:
        - If the quadrilateral drawing is already complete, the point is not added.
        - If the new point is too close to any existing corner, it is not added.
        - If adding the new point as the fourth corner would result in a non-convex quadrilateral, it is not added.
        If the point is successfully added and the quadrilateral now has the required number of sides,
        the drawing is marked as complete.
        Args:
            new_point (QPointF): The point to be added to the quadrilateral.
        Returns:
            int: 0 if the point was successfully added, -1 otherwise.
        """
        # Check if drawing is competed
        if self.drawing_complete:
            return -1

        # Check if new point is near another point in the quadrilateral
        close_point_id = self.find_close_corner(new_point)
        if close_point_id is not None:
            return -1

        # Check convexity if this is the 4th point
        temp_points = self.quadrilateral_points + [new_point]
        if len(temp_points) == self.NB_SIDE:
            if not self.is_convex(temp_points):
                return -1

        # Add point
        self.quadrilateral_points.append(new_point)

        # Raise drawing complete flag if enough points are in the list
        if len(self.quadrilateral_points) == self.NB_SIDE:
            self.drawing_complete = True
        
        return 0
    
    def update_point(self, point_id: int, new_point_value: QPointF) -> int:
        """
        Updates the position of a specified point in the quadrilateral if the update maintains convexity.
        Args:
            point_id (int): The index of the point to update (must be within valid range).
            new_point_value (QPointF): The new position for the specified point.
        Returns:
            int: 0 if the point was successfully updated;
                 -1 if the update was not performed due to incomplete drawing, invalid point index, or resulting in a non-convex quadrilateral.
        """
        # Check flags
        if not self.drawing_complete:
            return -1
        
        # Check point id value
        if not 0 <= point_id < self.NB_SIDE:
            return -1

        # Check convexity before updating
        temp_points = self.quadrilateral_points.copy()
        temp_points[point_id] = new_point_value
        if not self.is_convex(temp_points):
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