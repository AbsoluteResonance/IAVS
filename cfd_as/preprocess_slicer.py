"""Run in 3D Slicer's Python to smooth binary masks and export STL surfaces.

Example:
  Slicer --no-main-window --python-script preprocess_slicer.py -- --input-dir masks --output-dir work
"""

import argparse
from pathlib import Path

import SimpleITK as sitk
import slicer


def process_case(mask_path: Path, output_dir: Path) -> None:
    image = sitk.ReadImage(str(mask_path))
    if sitk.GetArrayFromImage(image).max() == 0:
        return

    volume = slicer.util.loadVolume(str(mask_path))
    segmentation = slicer.util.loadSegmentation(str(mask_path))
    editor_widget = slicer.qMRMLSegmentEditorWidget()
    editor_widget.setMRMLScene(slicer.mrmlScene)
    editor_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    editor_widget.setMRMLSegmentEditorNode(editor_node)
    editor_widget.setSegmentationNode(segmentation)
    editor_widget.setMasterVolumeNode(volume)

    editor_widget.setActiveEffectByName("Smoothing")
    editor_widget.activeEffect().setParameter("SmoothingMethod", "MEDIAN")
    editor_widget.activeEffect().setParameter("KernelSizeMm", 1)
    editor_widget.activeEffect().self().onApply()

    editor_widget.setActiveEffectByName("Islands")
    editor_widget.activeEffect().setParameter("MinimumSize", "1000")
    editor_widget.activeEffect().setParameter("Operation", "KEEP_LARGEST_ISLAND")
    editor_node.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
    editor_widget.activeEffect().self().onApply()

    labelmap = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    slicer.modules.segmentations.logic().ExportVisibleSegmentsToLabelmapNode(segmentation, labelmap, volume)
    output_mask = output_dir / "masks" / mask_path.name
    output_mask.parent.mkdir(parents=True, exist_ok=True)
    slicer.util.saveNode(labelmap, str(output_mask))

    segmentation.CreateClosedSurfaceRepresentation()
    stl_dir = output_dir / "stl"
    stl_dir.mkdir(parents=True, exist_ok=True)
    slicer.vtkSlicerSegmentationsModuleLogic.ExportSegmentsClosedSurfaceRepresentationToFiles(
        str(stl_dir), segmentation, None, "STL"
    )
    generated = stl_dir / f"{mask_path.name}_Segment_1.stl"
    generated.rename(stl_dir / mask_path.name.replace(".nii.gz", ".stl").replace(".nii", ".stl"))
    slicer.mrmlScene.Clear(0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    masks = sorted([*args.input_dir.glob("*.nii"), *args.input_dir.glob("*.nii.gz")])
    for mask in masks:
        process_case(mask, args.output_dir)


if __name__ == "__main__":
    main()
