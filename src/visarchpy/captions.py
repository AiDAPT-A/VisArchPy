"""
Extracts captions from PDF pages
"""

import re
from pdfminer.layout import LTTextContainer, LTImage
from typing import List
from shapely.geometry import Polygon
from dataclasses import dataclass, field
from visarchpy.utils import convert_mm_to_point, convert_dpi_to_point
from typing import Optional


@dataclass
class BoundingBox:
    """
    represents a bounding box of a PDF element in the form (x0, y0, x1, y1).
    Coordinates represent the lower-left corner (x0, y0) and the upper-right
    corner (x1, y1). Units are in points (pt) by default. Supports other units
    such as dots-per-inch (dpi), in which case the coordinates are in pixels
    (px) and millimeters (mm).
    """

    coords: tuple
    unit: str | int = "pt"
    width: Optional[float] = field(init=False)
    height: Optional[float] = field(init=False)

    def __post_init__(self):
        if len(self.coords) != 4:
            raise ValueError("bounding box must be a tupple of 4 elements \
                             (x0, y0, x1, y1)")

        if not isinstance(self.unit, int) and self.unit not in ["mm", "pt"]:
            raise TypeError("unit must be either 'mm', 'pt' (points), or an\
                            integer representing DPI")

        self.width = self.coords[2] - self.coords[0]
        self.height = self.coords[3] - self.coords[1]

    def bbox(self) -> tuple:
        """
        Method to return the coordinates of the bounding box

        Returns
        -------
        tuple
            coordinates of the bounding box in points (pt)
        """

        if self.unit == "mm":
            return self._convert_mm_to_point()
        elif self.unit == "pt":
            return self.coords  # points
        else:  # when a dpi is provided
            return self._convert_dpi_to_point(self.unit)

    def bbox_px(self) -> tuple:
        """
        Returns the coordinates of the bounding box in pixels (px)
        """

        if isinstance(self.unit, int):
            return self.coords
        else:
            raise TypeError(f"only units with DPI can be converted to\
                            pixels (px). Got {self.unit} instead.")

    def _convert_mm_to_point(self) -> tuple:
        """converts the coordinates of the bounding box from millimeters (mm)\
            to points (pt)"""

        return tuple(convert_mm_to_point(coord) for coord in self.coords)

    def _convert_dpi_to_point(self, dpi=int) -> tuple:
        """converts the coordinates of the bounding box from pixels (px)\
            to points (pt)"""

        return tuple(convert_dpi_to_point(coord, dpi)
                     for coord in self.coords)


@dataclass
class Offset:
    """
    represents an offset in the form (distance, unit).
    """

    distance: float
    unit: str

    def __post_init__(self):
        if self.unit not in ["mm", "px"]:
            raise ValueError("unit must be either mm or px (pixels)")


def find_caption_by_text(text_element: LTTextContainer,
                         keywords: List = ['figure', 'caption', 'figuur']
                         ) -> LTTextContainer | bool:
    """Does text analysis by matching caption keywords (e.g, figure, caption,
    Figure) in a PDF document element of type text using regular expressions.
    Matches are case insentive.

    Parameters
    ----------
    text_element: LTTextContainer object
        text element to be analyzed
    keywords: list
        list of keywords to match in the text element

    Returns
    -------
    LTTextContainer object or bool
        False if no match is found, otherwise the
        text element that matches any of the keywords

    Raises
    ------
    ValueError
        if list of keywords is empty
    TypeError
        if keyword is not a string
    """

    if len(keywords) == 0:
        raise ValueError("List of keywords cannot be empty. Try adding adding\
                         at least one keyword")
    else:
        # constructs regular expression to match
        # textboxes that start with
        words = []
        separator = '|'
        for word in keywords:
            if not isinstance(word, str):
                raise TypeError(f"Keyword must be of type string. {word} has \
                                 type {type(word)}")
            words.append('^'+word.lower())
        regex = separator.join(words)

    if isinstance(text_element, LTTextContainer) and re.search(regex, text_element.get_text().lower()):
        return text_element
    else:
        return False


def find_caption_by_distance(image_object: LTImage | BoundingBox,
                             text_object: LTTextContainer | BoundingBox,
                             offset: Offset, direction: str = None
                             ) -> LTTextContainer | bool:
    """
    Finds a text element withing a certain distance (offset)
    from the bounding box of an Image element. The area covered by the image
    itself is excluded.

    Parameters
    ----------
    image_object: LTImage object or tuple
        Image whose bounding box will be used as reference.
        Either a single LTImage object or a list of coordinates
        of the form (x0, y0, x1, y1), where (x0, y0) is the lower-left
        corner and (x1, y1) the upper-right corner.
    text_object: LTTextContainer object
        text element whose bounding box will be compared with the image
        bounding box.
        Either a single LTTextContainer object or a list of coordinates
        of the form (x0, y0, x1, y1), where (x0, y0) is the lower-left
        corner and (x1, y1) the upper-right corner.
    offset: OffsetDistance object
        distance from image within which the text element will be searched.
        All distances are converted to points (pt) before being applied.
    direction: str
        the directions the offeset will be applied around the image bounding
        box. Default None, which applies offect in 'all' directions.
        Posibile values: right, left, down, up, right-down, left-up, all.

    Returns
    -------
    LTTextContainer | BoundingBox or bool
        False if no match is found, otherwise the
        text element within offset distance is returned

    Raises
    ------
    ValueError
        if direction is not one of the following: right, left, down, up,
        right-down, left-up, all
    TypeError
        if offset is in pixels and image_object is not a BoundingBox object.
        This is to insure that the offset is applied in the same units as the
        image bounding box.
    """

    image_coords = image_object.bbox
    text_coords = text_object.bbox

    if offset.unit == "mm":  # Bbox from pdfminer are in points
        offset_distance = convert_mm_to_point(offset.distance)

    if direction not in ["right", "left", "down", "up", "right-down",
                         "left-up", "all", None]:
        raise ValueError("direction must be either right, left, down, up, \
                         right-down, left-up, all")

    if offset.unit == "px":
        offset_distance = offset.distance

    if isinstance(image_object, BoundingBox):

        if image_object.unit in ["mm", "pt"]:
            image_coords = image_object.bbox()
        elif isinstance(image_object.unit, int):
            image_coords = image_object.bbox_px()

            # Inverting the directions is necessary for OCR because
            # the origin of the coordinate is on the top-left corner of
            # the image. In layout analysis the origin is on the bottom-left
            # corner of the image.
            if direction == 'down':
                direction = 'up'
            elif direction == 'up':
                direction = 'down'
            else:
                pass
                # TODO: add other directions, and test

        else:
            raise TypeError("combination of units not supported")

    if isinstance(text_object, BoundingBox):

        if text_object.unit in ["mm", "pt"]:
            text_coords = text_object.bbox()
        elif isinstance(text_object.unit, int):
            text_coords = text_object.bbox_px()

        else:
            raise TypeError("combination of units not supported")

    width = abs(image_coords[2] - image_coords[0])
    height = abs(image_coords[3] - image_coords[1])

    if direction is None or direction == "all":
        '''
         ____________________
        |    search area     |
        |  ++++++++++++++++  |
        |  +              +  |
        |  +  image box   +  |
        |  +              +  |
        |  +              +  |
        |  ++++++++++++++++  |
        |____________________|

        '''

        search_area = Polygon((
                              # bottom
                              # coodinates [x, y, x, y]
                              (image_coords[0] - offset_distance,
                               image_coords[1] - offset_distance),
                              (image_coords[2] + offset_distance,
                               image_coords[1] - offset_distance),
                              # top:
                              (image_coords[2] + offset_distance,
                               image_coords[3] + offset_distance),
                              (image_coords[0] - offset_distance,
                               image_coords[3] + offset_distance),
                              (image_coords[0] - offset_distance,
                               image_coords[1] - offset_distance),),
                              holes=[((
                               (image_coords[0], image_coords[1]),
                               (image_coords[2], image_coords[1]),
                               (image_coords[2], image_coords[3]),
                               (image_coords[0], image_coords[3]),
                               (image_coords[0], image_coords[1]),
                                ))]
                              )

    if direction == "up":
        '''
         ______________
        |  search area |
        ++++++++++++++++
        +              +
        +  image box   +
        +              +
        +              +
        ++++++++++++++++

        '''
        search_area = Polygon([
                              # bottom
                              # coodinates [x, y, x, y]
                              (image_coords[0], image_coords[1] + height),
                              (image_coords[2], image_coords[1] + height),
                              # top:
                              (image_coords[2], image_coords[3] +
                               offset_distance),
                              (image_coords[0], image_coords[3] +
                               offset_distance),
                              (image_coords[0], image_coords[1] + height)
                              ])

    if direction == "down":
        '''
        ++++++++++++++++
        +              +
        + image bbox   +
        +              +
        +              +
        ++++++++++++++++
        |_search_area__|

        '''
        search_area = Polygon([
                              # bottom
                              # coodinates [x, y, x, y]
                              (image_coords[0], image_coords[1]),
                              (image_coords[2], image_coords[3] - height),
                              # top:
                              (image_coords[2], image_coords[3] -
                               height - offset_distance),
                              (image_coords[0], image_coords[1] -
                               offset_distance),
                              (image_coords[0], image_coords[1])
                              ])

    if direction == "right":
        '''
        ++++++++++++++++ --
        +              + s |
        + image bbox   + e |
        +              + a |
        +              + r |
        ++++++++++++++++ --

        '''
        search_area = Polygon([
                              # bottom
                              (image_coords[0] + width, image_coords[1]),
                              (image_coords[2] + width + offset_distance,
                               image_coords[1]),
                              # top:
                              (image_coords[2] + width + offset_distance,
                               image_coords[3]),
                              (image_coords[0] + width, image_coords[3]),
                              (image_coords[0] + width, image_coords[1]),
                              ])

    if direction == "left":
        '''
         -- ++++++++++++++++
        | s +              +
        | e + image bbox   +
        | a +              +
        | r +              +
         -- ++++++++++++++++

        '''
        search_area = Polygon((
                              # bottom
                              (image_coords[0] - offset_distance,
                               image_coords[1]),
                              (image_coords[2] - width, image_coords[1]),
                              # top:
                              (image_coords[2] - width, image_coords[3]),
                              (image_coords[0] - offset_distance,
                               image_coords[3]),
                              (image_coords[0] - offset_distance,
                               image_coords[1])
                              ))

    if direction == "down-right":
        '''
        ++++++++++++++++---
        +              +  |
        + image bbox   +  |
        +              +  |
        +              +  |
        ++++++++++++++++  |
        |__search_area____|

        '''
        search_area = Polygon((
                            # bottom
                            # coodinates [x, y, x, y]
                            (image_coords[0], image_coords[1] -
                             offset_distance),
                            (image_coords[2] + offset_distance,
                             image_coords[1] - offset_distance),
                            # top:
                            (image_coords[2] + offset_distance,
                             image_coords[3]),
                            (image_coords[2], image_coords[3]),
                            (image_coords[2], image_coords[3] - height),
                            (image_coords[0], image_coords[3] - height),
                            (image_coords[0], image_coords[1] -
                             offset_distance)
        ))

    if direction == "up-left":

        '''
          _________________
         |   search area   |
         |  ++++++++++++++++
         |  +              +
         |  + image bbox   +
         |  +              +
         |  +              +
         ---++++++++++++++++

        '''
        search_area = Polygon((
                            # bottom
                            # coodinates [x, y, x, y]
                            (image_coords[0] - offset_distance,
                             image_coords[1]),
                            (image_coords[0], image_coords[1]),
                            (image_coords[2] - width, image_coords[3]),
                            (image_coords[2], image_coords[3]),
                            (image_coords[2], image_coords[3] +
                             offset_distance),
                            (image_coords[0] - offset_distance,
                             image_coords[3] + offset_distance),
                            (image_coords[0] - offset_distance,
                             image_coords[1]),
        ))

    text_bbox = Polygon([
                            (text_coords[0], text_coords[1]),
                            (text_coords[2], text_coords[1]),
                            (text_coords[2], text_coords[3]),
                            (text_coords[0], text_coords[3]),
                            (text_coords[0], text_coords[1])
                    ])

    if search_area.intersects(text_bbox):
        return text_object
    else:
        return False


if __name__ == '__main__':
    pass
