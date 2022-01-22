#!/usr/bin/env python
import argparse
import struct

import numpy as np
import open3d as o3d


def read_kitti_bin(kitti_bin_path: str):
    SIZE_FLOAT = 4
    pcd_data = []
    with open(kitti_bin_path, "rb") as f:
        byte = f.read(SIZE_FLOAT * 4)
        while byte:
            x, y, z, intensity = struct.unpack("ffff", byte)
            pcd_data.append([x, y, z, intensity])
            byte = f.read(SIZE_FLOAT * 4)
    return np.array(pcd_data)


def convert_kitti_bin_to_pcd(kitti_bin_path: str, output_pcd_path: str, write_ascii=True):
    pcd = o3d.t.geometry.PointCloud()
    pcd_data = read_kitti_bin(kitti_bin_path)
    pcd.point["positions"] = o3d.core.Tensor(pcd_data[:, :3], dtype=o3d.core.float32)
    pcd.point["intensity"] = o3d.core.Tensor(pcd_data[:, 3][:, None] * 255, dtype=o3d.core.uint16)
    o3d.t.io.write_point_cloud(output_pcd_path, pcd, write_ascii)


def get_args():
    parser = argparse.ArgumentParser("convert kitti bin to pcd")
    parser.add_argument("--kitti_bin_path", "-k", type=str, required=True)

    return parser.parse_args()


def main():
    args = get_args()
    output_pcd_path = args.kitti_bin_path[:-3] + "pcd"
    convert_kitti_bin_to_pcd(args.kitti_bin_path, output_pcd_path)


if __name__ == "__main__":
    main()
