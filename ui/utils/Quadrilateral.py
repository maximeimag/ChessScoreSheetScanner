from copy import deepcopy
from PyQt6.QtCore import Qt, QPointF

class Quadrilateral:

    NB_SIDE: int = 4 
    CLOSE_POINT_DISTANCE: int = 10

    def __init__(self):
        # Quadrilateral points
        self.quadrilateral_points: list[QPointF] = []

        # Quadrilateral flag
        self.drawing_complete: bool = False

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