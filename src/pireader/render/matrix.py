# pragma: exclude file
"""Affine transformation matrix manipulation."""

import math

import numpy as np

from pireader.common import models


class AffineMatrix:
    """An affine transformation matrix wrapping NumPy."""

    def __init__(self, matrix: object = None) -> None:
        if matrix is not None:
            self._mat = np.array(matrix, dtype=np.float32)
        else:
            self._mat = np.eye(3, dtype=np.float32)

    @property
    def data(self) -> tuple[float, float, float, float, float, float]:
        """Get the affine matrix data as a tuple of floats."""
        return (
            self._mat[0, 0],
            self._mat[0, 1],
            self._mat[0, 2],
            self._mat[1, 0],
            self._mat[1, 1],
            self._mat[1, 2],
        )

    @classmethod
    def translation(cls, tx: float, ty: float) -> AffineMatrix:
        """Return the translation matrix."""
        return cls(
            [
                [1, 0, tx],
                [0, 1, ty],
                [0, 0, 1],
            ]
        )

    @classmethod
    def rotation(cls, degrees: float) -> AffineMatrix:
        """Return the rotation matrix."""
        rad = math.radians(degrees)
        c, s = math.cos(rad), math.sin(rad)
        return cls(
            [
                [c, -s, 0],
                [s, c, 0],
                [0, 0, 1],
            ]
        )

    @classmethod
    def scaling(cls, sx: float, sy: float) -> AffineMatrix:
        """Return the scaling matrix."""
        return cls(
            [
                [sx, 0, 0],
                [0, sy, 0],
                [0, 0, 1],
            ]
        )

    def multiply(self, other: AffineMatrix) -> AffineMatrix:
        """Multiply two 3x3 matrices together."""
        return AffineMatrix(np.dot(self._mat, other._mat))

    def inverse(self) -> AffineMatrix:
        """Return the inverse of the matrix."""
        return AffineMatrix(np.linalg.inv(self._mat))

    def transform_point(self, x: float, y: float) -> models.Vector2D:
        """Apply matrix transformation to a 2D coordinate point."""
        res = np.dot(self._mat, np.array([x, y, 1.0]))
        return models.Vector2D(float(res[0]), float(res[1]))
