#!/usr/bin/env python
import json
from typing import Generic, TypeVar

import cv2
import numpy as np

__all__ = ["Array", "CameraInfo", "RigidTransformation"]


Shape = TypeVar("Shape")
DType = TypeVar("DType")


class Array(np.ndarray, Generic[Shape, DType]):
    pass


class CameraInfo:
    def __init__(self, K: np.ndarray, dist_coeffs: np.ndarray):
        assert K[0] != 0, "invalid camera matrix"
        self._K = K.reshape(3, 3)
        self._dist_coeffs = dist_coeffs

    @property
    def K(self):
        return self._K

    @property
    def dist_coeffs(self):
        return self._dist_coeffs

    @staticmethod
    def from_json(
        json_info_path: str, instrinsic_coeffs_key: str = "K", dist_coeffs_key: str = "dist_coeffs"
    ) -> "CameraInfo":
        with open(json_info_path, "r") as f:
            data = json.load(f)
            assert instrinsic_coeffs_key in data

        try:
            dist_coeffs = np.array(data[dist_coeffs_key])
        except KeyError:
            dist_coeffs = np.zeros(5, dtype=float)

        return CameraInfo(np.array(data[instrinsic_coeffs_key]), dist_coeffs)


class RigidTransformation:
    def __init__(
        self,
        rotation_mat: np.ndarray,
        translation_vec: np.ndarray,
    ):
        self._rotation_mat = rotation_mat.reshape(3, 3)
        self._translation_vec = translation_vec

        # optional properties
        self._transformation_mat = None
        self._rotation_vec = None
        self._rpy = None

    @property
    def rotation_mat(self):
        return self._rotation_mat

    @property
    def translation_vec(self):
        return self._translation_vec

    @property
    def transformation_mat(self):
        if self._transformation_mat is None:
            self._transformation_mat = np.eye(4)
            self._transformation_mat[:3, :3] = self._rotation_mat
            self._transformation_mat[:3, 3] = self._translation_vec
        return self._transformation_mat

    @property
    def rotation_vec(self):
        if self._rotation_vec is None:
            self._rotation_vec, _ = cv2.Rodrigues(self._rotation_mat)
        return self._rotation_vec

    @property
    def rpy(self):
        if self._rpy is None:
            self._rpy = np.deg2rad(cv2.RQDecomp3x3(self._rotation_mat)[0])
        return self._rpy

    @staticmethod
    def from_json(
        json_info_path: str, rotation_mat_key: str = "rotation_mat", translation_vec_key: str = "translation_vec"
    ) -> "RigidTransformation":
        with open(json_info_path, "r") as f:
            data = json.load(f)
            assert rotation_mat_key in data and translation_vec_key in data
        return RigidTransformation(np.array(data[rotation_mat_key]), np.array(data[translation_vec_key]))
