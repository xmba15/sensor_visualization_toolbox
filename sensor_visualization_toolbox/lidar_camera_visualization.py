#!/usr/bin/env python
import cv2
import numpy as np
import open3d as o3d
from matplotlib import pyplot as plt

from .types import CameraInfo, RigidTransformation

__all__ = ["LidarCameraVisualizationHandler"]


class LidarCameraVisualizationHandler:
    def __init__(self, camera_info: CameraInfo, extrinsic: RigidTransformation):
        self._camera_info = camera_info
        self._extrinsic = extrinsic
        self._cmap = plt.get_cmap("jet")

    @staticmethod
    def from_json(json_info_path: str) -> "LidarCameraVisualizationHandler":
        return LidarCameraVisualizationHandler(
            CameraInfo.from_json(json_info_path), RigidTransformation.from_json(json_info_path)
        )

    def project_point_cloud_on_image(self, image_path: str, cloud_path: str):
        image = cv2.imread(image_path)
        assert image is not None, f"failed to load {image_path}"

        pcd = o3d.t.io.read_point_cloud(cloud_path)
        assert not pcd.is_empty(), f"failed to load {cloud_path}"

        xyz = pcd.point["positions"].numpy()
        xyz = xyz[xyz[:, 0] > 0]

        projected_points, _ = cv2.projectPoints(
            xyz,
            self._extrinsic.rotation_vec,
            self._extrinsic.translation_vec,
            self._camera_info.K,
            self._camera_info.dist_coeffs,
        )

        projected_points = projected_points.astype(int).squeeze(axis=1)
        height, width = image.shape[:2]
        keep_condition = (
            (projected_points[:, 0] >= 0)
            & (projected_points[:, 0] <= width - 1)
            & (projected_points[:, 1] >= 0)
            & (projected_points[:, 1] <= height - 1)
        )
        projected_points = projected_points[keep_condition]
        xyz = xyz[keep_condition]
        colors = [np.array(self._cmap((int(point[0] % 20) / 20.0))) * 255 for point in xyz]

        [
            cv2.circle(image, point, radius=1, color=color, thickness=-1)
            for (point, color) in zip(projected_points, colors)
        ]

        return image
