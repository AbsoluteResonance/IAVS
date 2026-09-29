"""Run in 3D Slicer with SlicerVMTK to extract endpoints and centerlines.

Example:
  Slicer --python-script extract_centerlines_slicer.py -- --mesh model.stl --output-dir work/centerlines
"""

import argparse
from pathlib import Path

import ExtractCenterline
import slicer
import vtk


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mesh", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    model = slicer.util.loadModel(str(args.mesh))
    logic = ExtractCenterline.ExtractCenterlineLogic()
    endpoints = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLMarkupsFiducialNode", args.mesh.stem + "_endpoints"
    )
    network = logic.extractNetwork(model.GetPolyData(), endpoints)
    positions = logic.getEndPoints(network, startPointPosition=None)
    endpoints.RemoveAllControlPoints()
    for position in positions:
        endpoints.AddControlPoint(vtk.vtkVector3d(position))
    slicer.util.saveNode(endpoints, str(args.output_dir / "endpoints.json"))

    # The ExtractCenterline module creates one or more centerline curve nodes.
    # Save every generated curve; inspect endpoint inlet/outlet selection in Slicer
    # before passing these files to cut_stl.py.
    for node in slicer.util.getNodesByClass("vtkMRMLMarkupsCurveNode"):
        name = node.GetName().replace("/", "_")
        slicer.util.saveNode(node, str(args.output_dir / f"{name}.json"))


if __name__ == "__main__":
    main()
