#!/usr/bin/env python
from typing import List

import cv2

from .types import CameraInfo, Dataset, Object3D, RigidTransformation

__all__ = ["CameraVisualizationHandler"]


class CameraVisualizationHandler:
    def __init__(self, camera_info: CameraInfo, dataset: Dataset):
        self._camera_info = camera_info
        self._dataset = dataset

    def draw_object3d(self, image, object3d: Object3D, rigid_trans: RigidTransformation = RigidTransformation()):
        assert object3d.label_id >= 0
        projected_corners, _ = cv2.projectPoints(
            object3d.corners,
            rigid_trans.rotation_vec,
            rigid_trans.translation_vec,
            self._camera_info.K,
            self._camera_info.dist_coeffs,
        )
        projected_corners = projected_corners.astype(int).squeeze(axis=1)

        for k in range(0, 4):
            for (i, j) in ((k, (k + 1) % 4), (k + 4, (k + 1) % 4 + 4), (k, k + 4)):
                cv2.line(
                    image,
                    projected_corners[i],
                    projected_corners[j],
                    self._dataset.colors[object3d.label_id],
                    thickness=2,
                )

        return image

    def draw_object3ds(
        self, image, object3ds: List[Object3D], rigid_trans: RigidTransformation = RigidTransformation()
    ):
        for object3d in object3ds:
            self.draw_object3d(image, object3d, rigid_trans)
        return image

    @staticmethod
    def from_json(json_info_path: str, dataset) -> "CameraVisualizationHandler":
        return CameraVisualizationHandler(CameraInfo.from_json(json_info_path), dataset)
