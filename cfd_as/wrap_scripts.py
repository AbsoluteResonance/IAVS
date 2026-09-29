"""Geomagic Wrap automation used for IAVS surface repair and STEP fitting.

Run this script only inside a licensed Geomagic Wrap Python environment. Set the
paths in `main` for a batch run, or import the individual functions interactively.
"""

import os

import geomagic.app.v3
from geomagic.app.v3.imports import *


def doctor(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in sorted(name for name in os.listdir(input_dir) if name.endswith(".stl")):
        geo.open(0, 1, os.path.join(input_dir, filename))
        geo.mesh_doctor(
            "smallcompsize", 0.0034721, "smalltunnelsize", 0.0017361,
            "holesize", 0.0017361, "spikesens", 50, "spikelevel", 0.5,
            "defeatureoption", 2, "fillholeoption", 2, "autoexpand", 2,
            "operations", "IntersectionCheck+", "SmallComponentCheck+", "SpikeCheck+",
            "HighCreaseCheck+", "Update", "Auto-Repair", "Update", "Auto-Repair",
            "Update", "Auto-Repair", "Update", "Auto-Repair",
        )
        geo.saveas(os.path.join(output_dir, filename), 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def remesh(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in sorted(name for name in os.listdir(input_dir) if name.endswith(".stl")):
        geo.open(0, 1, os.path.join(input_dir, filename))
        geo.remesh(0.0003339, 0, 1, 45, 0.000806, 1, 0, 0, 0.0003339, 1)
        geo.refine_polygons(0, 0, 1)
        geo.optimize_edges()
        geo.enhance_mesh(5, 0, 50)
        geo.make_open_manifold()
        geo.saveas(os.path.join(output_dir, filename), 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def stl_to_step(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for filename in sorted(name for name in os.listdir(input_dir) if name.endswith(".stl")):
        geo.open(0, 1, os.path.join(input_dir, filename))
        geo.start_exact_surfacing(0, 0, 0, 0)
        geo.construct_patches(1, 1, 1000, 0)
        geo.construct_grids(20, 1)
        geo.fit_surfaces(0, 18, 8.05842e-06, 0.25, 0.5, 2, 0.5, 0, 0, 1, 0, 0)
        output = os.path.join(output_dir, os.path.splitext(filename)[0] + ".stp")
        geo.saveas(output, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


if __name__ == "__main__":
    # Edit these three paths for the local case directory before batch execution.
    ROOT_DIR = r"<IAVS_WORKDIR>"
    doctor(os.path.join(ROOT_DIR, "stl_2_cut"), os.path.join(ROOT_DIR, "stl_3_doctor"))
    remesh(os.path.join(ROOT_DIR, "stl_3_doctor"), os.path.join(ROOT_DIR, "stl_4_remesh"))
    stl_to_step(os.path.join(ROOT_DIR, "stl_4_remesh"), os.path.join(ROOT_DIR, "stp_1"))
