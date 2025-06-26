from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QColor

class Quadrilateral:
    """
    A class representing a 2D quadrilateral with interactive editing, drawing, and geometric utilities.
    The Quadrilateral class manages a set of four points in 2D space, providing methods for:
    - Interactive construction and editing (adding, moving points with convexity checks)
    - Geometric queries (point-in-polygon, centroid calculation, convexity)
    - Drawing and visualization (with selection and drawing states, grid lines, and IDs)
    - Access to logical corners (top-left, top-right, bottom-left, bottom-right)
    - Grid subdivision (internal rows and columns for cell-like partitioning)
        NB_SIDE (int): Number of sides (always 4 for a quadrilateral).
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
        PEN_DRAWING_QUADRILATERAL (QPen): Pen for drawing quadrilateral in drawing mode.
        DRAWING_POINT_SIZE (int): Size of points while drawing.
    Instance Attributes:
        drawing_complete (bool): True if the quadrilateral has four points and is finalized.
        is_selected (bool): True if the quadrilateral is currently selected.
        top_left_id, top_right_id, bottom_left_id, bottom_right_id (int | None): Indices of logical corners.
    Methods:
        find_close_corner(point): Returns index of a corner near the given point, or None.
        is_convex(points): Static method to check if four points form a convex quadrilateral.
        append_point_to_quadrilateral(new_point): Adds a point if valid; checks for convexity and proximity.
        update_point(point_id, new_point_value): Updates a corner's position if convexity is preserved.
        is_point_in_quadrilateral(point): Checks if a point is inside the quadrilateral (ray casting).
        move_delta(delta): Moves all points by a given delta.
        get_centroid(): Returns the centroid (geometric center) if drawing is complete.
        update_corner_ids(): Updates logical corner indices based on geometry.
        get_corner(corner_id): Returns the QPointF for a given logical corner index.
        get_top_left(), get_top_right(), get_bottom_left(), get_bottom_right(): Accessors for logical corners.
        get_internal_rows(nb_internal_rows): Returns endpoints of internal horizontal rows (for grid).
        get_internal_cols(nb_internal_cols): Returns endpoints of internal vertical columns (for grid).
        drawForeground(painter, rect, draw_cells, nb_internal_rows, nb_internal_cols): Draws the quadrilateral and optional grid on a QPainter.
    Usage:
        - Construct and interactively build a quadrilateral by appending points.
        - Move, select, and visualize the quadrilateral in a GUI context.
        - Subdivide the quadrilateral into a grid for applications like table or chessboard detection.
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

        # Corners
        self.top_left_id: int | None = None
        self.top_right_id: int | None = None
        self.bottom_left_id: int | None = None
        self.bottom_right_id: int | None = None

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
            self.update_corner_ids()
        
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
        self.update_corner_ids()

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

    def update_corner_ids(self) -> None:
        """
        Updates the corner IDs (top-left, top-right, bottom-left, bottom-right) of the quadrilateral
        based on the current positions of its points.
        The method first checks if the quadrilateral drawing is complete. If not, it returns immediately.
        It then sorts the indices of the quadrilateral's points by their y-coordinate to distinguish
        between the top and bottom points. For both the top and bottom pairs, it compares their x-coordinates
        to determine left and right positions, and assigns the corresponding IDs.
        This ensures that the corner IDs always correspond to the correct geometric corners regardless
        of the order in which the points were originally defined.
        """
        if not self.drawing_complete:
            return

        # Sort point with y value
        sorted_indices: list[int] = sorted(range(self.NB_SIDE),key=lambda i: self.quadrilateral_points[i].y())
        top1_idx, top2_idx, bottom1_idx, bottom2_idx = sorted_indices

        # Compare x on top corners
        if self.quadrilateral_points[top1_idx].x() <= self.quadrilateral_points[top2_idx].x():
            self.top_left_id = top1_idx
            self.top_right_id = top2_idx
        else:
            self.top_left_id = top2_idx
            self.top_right_id = top1_idx

        # Compare x on bottom corners
        if self.quadrilateral_points[bottom1_idx].x() <= self.quadrilateral_points[bottom2_idx].x():
            self.bottom_left_id = bottom1_idx
            self.bottom_right_id = bottom2_idx
        else:
            self.bottom_left_id = bottom2_idx
            self.bottom_right_id = bottom1_idx
    
    def get_corner(self, corner_id: int | None) -> QPointF | None:
        """
        Returns the QPointF representing the specified corner of the quadrilateral.

        Args:
            corner_id (int | None): The index of the corner to retrieve. Should be in the range [0, NB_SIDE).

        Returns:
            QPointF | None: The QPointF object at the specified corner index, or None if the index is invalid or None.
        """
        if corner_id is None:
            return None
        if not (0 <= corner_id < self.NB_SIDE):
            return None
        return self.quadrilateral_points[corner_id]
    
    def get_top_left(self) -> QPointF | None:
        return self.get_corner(corner_id=self.top_left_id)
    
    def get_top_right(self) -> QPointF | None:
        return self.get_corner(corner_id=self.top_right_id)
    
    def get_bottom_left(self) -> QPointF | None:
        return self.get_corner(corner_id=self.bottom_left_id)
    
    def get_bottom_right(self) -> QPointF | None:
        return self.get_corner(corner_id=self.bottom_right_id)
    
    def get_internal_rows(self, nb_internal_rows: int) -> list[list[QPointF]] | None:
        """
        Computes the internal horizontal rows within the quadrilateral, returning the endpoints of each row as lists of QPointF.
        Args:
            nb_internal_rows (int): The total number of horizontal rows (including the outer edges) to divide the quadrilateral into.
        Returns:
            list[list[QPointF]] | None: 
                - A list of rows, where each row is represented as a list containing two QPointF objects (the left and right endpoints of the row).
                - Returns an empty list if nb_internal_rows == 1 (no internal rows).
                - Returns None if any corner point is missing or if nb_internal_rows < 1.
        Notes:
            - The rows are computed by linear interpolation between the top and bottom edges of the quadrilateral.
            - The outermost edges (top and bottom) are not included in the result; only internal rows are returned.
        """
        # Get points 
        pt_tl: QPointF | None = self.get_top_left()
        pt_tr: QPointF | None = self.get_top_right()
        pt_bl: QPointF | None = self.get_bottom_left()
        pt_br: QPointF | None = self.get_bottom_right()

        # Check points
        if (pt_tl is None) or (pt_tr is None) or (pt_bl is None) or (pt_br is None):
            return None
        
        # Check number of rows
        if nb_internal_rows < 1:
            return None
        elif nb_internal_rows == 1:
            return []

        # Draw horizontal grid lines
        internal_rows_list: list[list[QPointF]] = []
        for r in range(1, nb_internal_rows):
            t = r / nb_internal_rows
            internal_rows_list.append([
                pt_tl * (1 - t) + pt_bl * t,
                pt_tr * (1 - t) + pt_br * t
            ])
        
        return internal_rows_list
    
    def get_internal_cols(self, nb_internal_cols: int) -> list[list[QPointF]] | None:
        """
        Calculates the internal vertical columns within the quadrilateral, returning the points that define each internal column line.
        Args:
            nb_internal_cols (int): The total number of columns (including the outer edges). Must be at least 1.
        Returns:
            list[list[QPointF]] | None: 
                - A list of column lines, where each line is represented by a list of two QPointF objects (the start and end points of the line).
                - Returns an empty list if nb_internal_cols == 1 (no internal columns).
                - Returns None if any corner point is missing or if nb_internal_cols < 1.
        Notes:
            - The columns are interpolated between the top and bottom edges of the quadrilateral.
            - The outermost columns (edges) are not included in the result; only internal columns are returned.
        """
        # Get points 
        pt_tl: QPointF | None = self.get_top_left()
        pt_tr: QPointF | None = self.get_top_right()
        pt_bl: QPointF | None = self.get_bottom_left()
        pt_br: QPointF | None = self.get_bottom_right()

        # Check points
        if (pt_tl is None) or (pt_tr is None) or (pt_bl is None) or (pt_br is None):
            return None
        
        # Check number of rows
        if nb_internal_cols < 1:
            return None
        elif nb_internal_cols == 1:
            return []

        # Draw horizontal grid lines
        internal_cols_list: list[list[QPointF]] = []
        for r in range(1, nb_internal_cols):
            t = r / nb_internal_cols
            internal_cols_list.append([
                pt_tl * (1 - t) + pt_tr * t,
                pt_bl * (1 - t) + pt_br * t
            ])
        
        return internal_cols_list

    def drawForeground(self, 
            painter: QPainter,
            rect: QRectF, 
            draw_cells: bool = False,
            nb_internal_rows: int = 1,
            nb_internal_cols: int = 1
        ):
        """
        Draws the quadrilateral, its points, internal grid lines, and optional ID on the provided QPainter.
        Args:
            painter (QPainter): The painter object used for drawing.
            rect (QRectF): The rectangle area in which to draw.
            draw_cells (bool, optional): Whether to draw internal grid lines (cells) within the quadrilateral. Defaults to False.
            nb_internal_rows (int, optional): Number of internal rows to draw. Defaults to 1.
            nb_internal_cols (int, optional): Number of internal columns to draw. Defaults to 1.
        Behavior:
            - If the quadrilateral drawing is complete:
                - Draws the quadrilateral outline and its corner points.
                - Highlights the quadrilateral and its points if selected.
                - Optionally draws internal grid lines if `draw_cells` is True.
                - Draws the quadrilateral's numeric ID at its centroid if available.
            - If the quadrilateral is not complete:
                - Draws the currently defined points and polyline in a "drawing" style.
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
            
            # Draw internal lines            
            internal_rows_list: list[list[QPointF]] | None = self.get_internal_rows(nb_internal_rows=nb_internal_rows)
            internal_cols_list: list[list[QPointF]] | None = self.get_internal_cols(nb_internal_cols=nb_internal_cols)
            if draw_cells and (internal_rows_list is not None) and (internal_cols_list is not None):    
                for p1, p2 in internal_rows_list:
                    painter.drawLine(p1, p2)    
                for p1, p2 in internal_cols_list:
                    painter.drawLine(p1, p2)

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