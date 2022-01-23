#!/usr/bin/env python
import json
from typing import Generic, List, Tuple, TypeVar

import cv2
import numpy as np

__all__ = ["Array", "CameraInfo", "RigidTransformation", "Object3D", "Dataset"]


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
        rotation_mat: np.ndarray = np.eye(3),
        translation_vec: np.ndarray = np.zeros(3),
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


class Object3D:
    def __init__(self, bottom_center, height, width, length, yaw, label_id=-1):
        self._bottom_center = bottom_center
        self._h = height
        self._w = width
        self._l = length
        self._yaw = yaw
        self._label_id = label_id

        self._R = Object3D.roty(self._yaw)
        self._get_corners()

    @property
    def label_id(self):
        return self._label_id

    @property
    def corners(self):
        return self._corners_3d

    def _get_corners(self):
        x_corners = [
            self._l / 2,
            self._l / 2,
            -self._l / 2,
            -self._l / 2,
            self._l / 2,
            self._l / 2,
            -self._l / 2,
            -self._l / 2,
        ]
        y_corners = [0, 0, 0, 0, -self._h, -self._h, -self._h, -self._h]
        z_corners = [
            self._w / 2,
            -self._w / 2,
            -self._w / 2,
            self._w / 2,
            self._w / 2,
            -self._w / 2,
            -self._w / 2,
            self._w / 2,
        ]
        corners_3d = self._R @ np.vstack([x_corners, y_corners, z_corners])
        self._corners_3d = corners_3d.T + self._bottom_center

    @staticmethod
    def from_kitti_label_line(label_line) -> "Object3D":
        data = label_line.split(" ")
        data[1:] = [float(elem) for elem in data[1:]]
        height = data[8]
        width = data[9]
        length = data[10]
        bottom_center = (data[11], data[12], data[13])
        yaw = data[14]
        label_id = Dataset.Kitti().labels.index(data[0]) if data[0] in Dataset.Kitti().labels else -1

        return Object3D(bottom_center, height, width, length, yaw, label_id)

    @staticmethod
    def from_kitti_label_file(label_file) -> List["Object3D"]:
        with open(label_file, "r") as _file:
            lines = _file.readlines()

        return [Object3D.from_kitti_label_line(line) for line in lines]

    @staticmethod
    def roty(t):
        """
        rotation about the y-axis.
        """
        c = np.cos(t)
        s = np.sin(t)
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


class Dataset:
    def __init__(self, labels: Tuple[str, ...], colors=None, seed=2022):
        assert len(labels) > 0
        self._labels = labels
        np.random.seed(seed)
        self._colors = (
            colors if colors is not None else np.random.choice(range(256), size=(len(self._labels), 3)).tolist()
        )
        assert len(self._labels) == len(self._colors), "mismatch sizes of labels and colors"

    @property
    def labels(self):
        return self._labels

    @property
    def colors(self):
        return self._colors

    @staticmethod
    def Kitti() -> "Dataset":
        labels = ("Car", "Pedestrian", "Cyclist", "Tram", "Person_sitting", "Misc", "DontCare")
        return Dataset(labels)
