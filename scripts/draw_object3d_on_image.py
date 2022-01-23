#!/usr/bin/env python
import argparse
import os
import sys

import cv2

_CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(_CURRENT_DIR, "../"))
if True:
    from sensor_visualization_toolbox import (
        CameraVisualizationHandler,
        Dataset,
        Object3D,
    )


def get_args():
    parser = argparse.ArgumentParser("draw object 3d on image")
    parser.add_argument("--json_info_path", "-j", type=str, required=True)
    parser.add_argument("--label_path", "-l", type=str, required=True)
    parser.add_argument("--image_path", "-i", type=str, required=True)

    return parser.parse_args()


def main():
    args = get_args()
    image = cv2.imread(args.image_path)
    assert image is not None, f"failed to load {args.image_path}"
    object3ds = Object3D.from_kitti_label_file(args.label_path)
    camera_visualizer = CameraVisualizationHandler.from_json(args.json_info_path, Dataset.Kitti())
    image = camera_visualizer.draw_object3ds(image, object3ds)
    cv2.imwrite("3d_bbox.jpg", image)


if __name__ == "__main__":
    main()
