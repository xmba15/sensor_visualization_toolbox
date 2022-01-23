#!/usr/bin/env python
import argparse
import os
import sys

import cv2

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_CURRENT_DIR, "../"))
if True:
    from sensor_visualization_toolbox import LidarCameraVisualizationHandler


def get_args():
    parser = argparse.ArgumentParser("visualize lidar camera")
    parser.add_argument("--json_info_path", "-j", type=str, required=True)
    parser.add_argument("--image_path", "-i", type=str, required=True)
    parser.add_argument("--cloud_path", "-c", type=str, required=True)

    return parser.parse_args()


def main():
    args = get_args()
    lidar_camera_visualizer = LidarCameraVisualizationHandler.from_json(args.json_info_path)
    projected_image = lidar_camera_visualizer.project_point_cloud_on_image(args.image_path, args.cloud_path)
    assert projected_image is not None
    cv2.imwrite("test.png", projected_image)


if __name__ == "__main__":
    main()
