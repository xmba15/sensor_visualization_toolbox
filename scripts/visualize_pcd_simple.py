#!/usr/bin/env python
import argparse

import open3d as o3d


def get_args():
    parser = argparse.ArgumentParser("simple visualization of a single pcd")
    parser.add_argument("--pcd_path", "-p", type=str, required=True)

    return parser.parse_args()


def main():
    args = get_args()
    pcd = o3d.io.read_point_cloud(args.pcd_path)
    o3d.visualization.draw_geometries([pcd])


if __name__ == "__main__":
    main()
