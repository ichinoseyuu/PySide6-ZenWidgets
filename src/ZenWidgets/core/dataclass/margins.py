from typing import overload, Any
from PySide6.QtCore import QSize, QSizeF, QPoint, QPointF, QRect, QRectF

# region ZMargins
class ZMargins(object):

    @overload
    def __init__(self, /) -> None: ...

    @overload
    def __init__(self, padding: 'ZMargins', /) -> None: ...

    @overload
    def __init__(self, left: int, top: int, right: int, bottom: int, /) -> None: ...

    def __init__(self, *args) -> None:
        if not args:
            self._left = self._top = self._right = self._bottom = 0
        elif len(args) == 1 and isinstance(args[0], ZMargins):
            other = args[0]
            self._left = other._left
            self._top = other._top
            self._right = other._right
            self._bottom = other._bottom
        elif len(args) == 4 and all(isinstance(x, int) for x in args):
            self._left, self._top, self._right, self._bottom = args
        else:
            raise TypeError("Invalid arguments for ZMargin constructor")

    @overload
    def __add__(self, other: 'ZMargins', /) -> 'ZMargins': ...

    @overload
    def __add__(self, value: int, /) -> 'ZMargins': ...

    def __add__(self, other, /) -> 'ZMargins':
        if isinstance(other, ZMargins):
            return ZMargins(
                self._left + other._left,
                self._top + other._top,
                self._right + other._right,
                self._bottom + other._bottom
            )
        elif isinstance(other, int):
            return ZMargins(
                self._left + other,
                self._top + other,
                self._right + other,
                self._bottom + other
            )
        else:
            raise TypeError(f"Unsupported operand type(s) for +: 'ZMargin' and '{type(other).__name__}'")

    @overload
    def __sub__(self, other: 'ZMargins', /) -> 'ZMargins': ...

    @overload
    def __sub__(self, value: int, /) -> 'ZMargins': ...

    def __sub__(self, other, /) -> 'ZMargins':
        if isinstance(other, ZMargins):
            return ZMargins(
                self._left - other._left,
                self._top - other._top,
                self._right - other._right,
                self._bottom - other._bottom
            )
        elif isinstance(other, int):
            return ZMargins(
                self._left - other,
                self._top - other,
                self._right - other,
                self._bottom - other
            )
        else:
            raise TypeError(f"Unsupported operand type(s) for -: 'ZMargin' and '{type(other).__name__}'")

    @overload
    def __mul__(self, factor: int, /) -> 'ZMargins': ...

    @overload
    def __mul__(self, factor: float, /) -> 'ZMarginsF': ...

    def __mul__(self, factor: int | float, /) -> 'ZMargins | ZMarginsF':
        if isinstance(factor, (int, float)):
            left = self._left * factor
            top = self._top * factor
            right = self._right * factor
            bottom = self._bottom * factor

            if isinstance(factor, int):
                return ZMargins(int(left), int(top), int(right), int(bottom))
            else:
                return ZMarginsF(left, top, right, bottom)
        else:
            raise TypeError(f"Unsupported operand type(s) for *: 'ZMargin' and '{type(factor).__name__}'")

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, ZMargins):
            return (self._left == other._left and
                    self._top == other._top and
                    self._right == other._right and
                    self._bottom == other._bottom)
        elif isinstance(other, ZMarginsF):
            return (self._left == other.left() and
                    self._top == other.top() and
                    self._right == other.right() and
                    self._bottom == other.bottom())
        return False

    def __ne__(self, other: Any, /) -> bool: return not self.__eq__(other)

    def __neg__(self, /) -> 'ZMargins': return ZMargins(-self._left, -self._top, -self._right, -self._bottom)

    def __pos__(self, /) -> 'ZMargins': return ZMargins(self)

    def __or__(self, other: 'ZMargins', /) -> 'ZMargins':
        return ZMargins(
            max(self._left, other._left),
            max(self._top, other._top),
            max(self._right, other._right),
            max(self._bottom, other._bottom)
        )

    def __repr__(self, /) -> str: return f"ZMargin(left={self._left}, top={self._top}, right={self._right}, bottom={self._bottom})"

    @property
    def left(self, /) -> int: return self._left

    @left.setter
    def left(self, left: int, /) -> None: self._left = left

    @property
    def top(self, /) -> int: return self._top

    @top.setter
    def top(self, top: int, /) -> None: self._top = top

    @property
    def right(self, /) -> int: return self._right

    @right.setter
    def right(self, right: int, /) -> None: self._right = right

    @property
    def bottom(self, /) -> int: return self._bottom

    @bottom.setter
    def bottom(self, bottom: int, /) -> None: self._bottom = bottom

    def vertical(self, /) -> int: return self._top + self._bottom

    def horizontal(self, /) -> int: return self._left + self._right

    def size(self, /) -> QSize: return QSize(self._left + self._right, self._top + self._bottom)

    def topLeft(self, /) -> QPoint: return QPoint(self._left, self._top)

    def setLeft(self, left: int, /) -> None: self._left = left

    def setTop(self, top: int, /) -> None: self._top = top

    def setRight(self, right: int, /) -> None: self._right = right

    def setBottom(self, bottom: int, /) -> None: self._bottom = bottom

    @overload
    def setVertical(self, vertical: int, /) -> None: ...

    @overload
    def setVertical(self, top: int, bottom: int , /) -> None: ...

    def setVertical(self, *args) -> None:
        if len(args) == 1 and isinstance(args[0], int):
            self._top = self._bottom = args[0]
        elif len(args) == 2 and all(isinstance(x, int) for x in args):
            self._top, self._bottom = args
        else:
            raise TypeError("Invalid arguments for setVertical")

    @overload
    def setHorizontal(self, horizontal: int, /) -> None: ...

    @overload
    def setHorizontal(self, left: int, right: int , /) -> None: ...

    def setHorizontal(self, *args) -> None:
        if len(args) == 1 and isinstance(args[0], int):
            self._left = self._right = args[0]
        elif len(args) == 2 and all(isinstance(x, int) for x in args):
            self._left, self._right = args
        else:
            raise TypeError("Invalid arguments for setHorizontal")

    def isNull(self, /) -> bool: return self._left == 0 and self._top == 0 and self._right == 0 and self._bottom == 0

    def toMarginF(self, /) -> 'ZMarginsF': return ZMarginsF(self._left, self._top, self._right, self._bottom)

    def __copy__(self, /) -> 'ZMargins': return ZMargins(self)


# region ZMarginsF
class ZMarginsF(object):

    @overload
    def __init__(self, /) -> None: ...

    @overload
    def __init__(self, padding: 'ZMargins', /) -> None: ...

    @overload
    def __init__(self, padding: 'ZMarginsF', /) -> None: ...

    @overload
    def __init__(self, left: float, top: float, right: float, bottom: float, /) -> None: ...

    def __init__(self, *args) -> None:
        if not args:
            self._left = self._top = self._right = self._bottom = 0.0
        elif len(args) == 1 and isinstance(args[0], ZMargins):
            other = args[0]
            self._left = float(other.left())
            self._top = float(other.top())
            self._right = float(other.right())
            self._bottom = float(other.bottom())
        elif len(args) == 1 and isinstance(args[0], ZMarginsF):
            other = args[0]
            self._left = other._left
            self._top = other._top
            self._right = other._right
            self._bottom = other._bottom
        elif len(args) == 4 and all(isinstance(x, (int, float)) for x in args):
            self._left, self._top, self._right, self._bottom = map(float, args)
        else:
            raise TypeError("Invalid arguments for ZMarginF constructor")

    @overload
    def __add__(self, other: 'ZMargins | ZMarginsF', /) -> 'ZMarginsF': ...

    @overload
    def __add__(self, value: float, /) -> 'ZMarginsF': ...

    def __add__(self, other, /) -> 'ZMarginsF':
        if isinstance(other, (ZMargins, ZMarginsF)):
            return ZMarginsF(
                self._left + other.left(),
                self._top + other.top(),
                self._right + other.right(),
                self._bottom + other.bottom()
            )
        elif isinstance(other, (int, float)):
            return ZMarginsF(
                self._left + other,
                self._top + other,
                self._right + other,
                self._bottom + other
            )
        else:
            raise TypeError(f"Unsupported operand type(s) for +: 'ZMarginF' and '{type(other).__name__}'")

    @overload
    def __sub__(self, other: 'ZMargins | ZMarginsF', /) -> 'ZMarginsF': ...

    @overload
    def __sub__(self, value: float, /) -> 'ZMarginsF': ...

    def __sub__(self, other, /) -> 'ZMarginsF':
        if isinstance(other, (ZMargins, ZMarginsF)):
            return ZMarginsF(
                self._left - other.left(),
                self._top - other.top(),
                self._right - other.right(),
                self._bottom - other.bottom()
            )
        elif isinstance(other, (int, float)):
            return ZMarginsF(
                self._left - other,
                self._top - other,
                self._right - other,
                self._bottom - other
            )
        else:
            raise TypeError(f"Unsupported operand type(s) for -: 'ZMarginF' and '{type(other).__name__}'")

    def __mul__(self, factor: float, /) -> 'ZMarginsF':
        if isinstance(factor, (int, float)):
            return ZMarginsF(
                self._left * factor,
                self._top * factor,
                self._right * factor,
                self._bottom * factor
            )
        else:
            raise TypeError(f"Unsupported operand type(s) for *: 'ZMarginF' and '{type(factor).__name__}'")

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, ZMarginsF):
            return (self._left == other._left and
                    self._top == other._top and
                    self._right == other._right and
                    self._bottom == other._bottom)
        elif isinstance(other, ZMargins):
            return (self._left == other.left() and
                    self._top == other.top() and
                    self._right == other.right() and
                    self._bottom == other.bottom())
        return False

    def __ne__(self, other: Any, /) -> bool: return not self.__eq__(other)

    def __neg__(self, /) -> 'ZMarginsF': return ZMarginsF(-self._left, -self._top, -self._right, -self._bottom)

    def __pos__(self, /) -> 'ZMarginsF': return ZMarginsF(self)

    def __or__(self, other: 'ZMargins | ZMarginsF', /) -> 'ZMarginsF':
        return ZMarginsF(
            max(self._left, other.left()),
            max(self._top, other.top()),
            max(self._right, other.right()),
            max(self._bottom, other.bottom())
        )

    def __repr__(self, /) -> str: return f"ZMarginF(left={self._left}, top={self._top}, right={self._right}, bottom={self._bottom})"

    @property
    def left(self, /) -> float: return self._left

    @left.setter
    def left(self, left: float, /) -> None: self._left = left

    @property
    def top(self, /) -> float: return self._top

    @top.setter
    def top(self, top: float, /) -> None: self._top = top

    @property
    def right(self, /) -> float: return self._right

    @right.setter
    def right(self, right: float, /) -> None: self._right = right

    @property
    def bottom(self, /) -> float: return self._bottom

    @bottom.setter
    def bottom(self, bottom: float, /) -> None: self._bottom = bottom

    def vertical(self, /) -> float: return self._top + self._bottom

    def horizontal(self, /) -> float: return self._left + self._right

    def size(self, /) -> QSizeF: return QSizeF(self._left + self._right, self._top + self._bottom)

    def topLeft(self, /) -> QPointF: return QPointF(self._left, self._top)

    def setLeft(self, left: float, /) -> None: self._left = left

    def setTop(self, top: float, /) -> None: self._top = top

    def setRight(self, right: float, /) -> None: self._right = right

    def setBottom(self, bottom: float, /) -> None: self._bottom = bottom

    @overload
    def setVertical(self, vertical: float, /) -> None: ...

    @overload
    def setVertical(self, top: float, bottom: float, /) -> None: ...

    def setVertical(self, *args) -> None:
        if len(args) == 1 and isinstance(args[0], (int, float)):
            self._top = self._bottom = args[0]
        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self._top, self._bottom = args
        else:
            raise TypeError(f"Unsupported argument type(s) for setVertical: {args}")

    @overload
    def setHorizontal(self, horizontal: float, /) -> None: ...

    @overload
    def setHorizontal(self, left: float, right: float, /) -> None: ...

    def setHorizontal(self, *args) -> None:
        if len(args) == 1 and isinstance(args[0], (int, float)):
            self._left = self._right = args[0]
        elif len(args) == 2 and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
            self._left, self._right = args
        else:
            raise TypeError(f"Unsupported argument type(s) for setHorizontal: {args}")

    def isNull(self, /) -> bool: return self._left == 0.0 and self._top == 0.0 and self._right == 0.0 and self._bottom == 0.0

    def toMargin(self, /) -> 'ZMargins':
        return ZMargins(
            int(round(self._left)),
            int(round(self._top)),
            int(round(self._right)),
            int(round(self._bottom))
        )

    def __copy__(self, /) -> 'ZMarginsF': return ZMarginsF(self)
