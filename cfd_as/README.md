# CFD-AS reference implementation

This directory packages the computational-fluid-dynamics applicability workflow released with the IAVS supplementary material. It converts an IA-vessel segmentation into geometric assets and computes the **CFD-Applicability Score (CFD-AS)** from the outcomes of the topology, meshing, and flow stages.

## What is included

| Stage | Script | Runtime | Output |
| --- | --- | --- | --- |
| Topology screen | `check_topology.py` | Python | Per-mask Euler-number result (`VTA`) |
| Mask cleanup and surface extraction | `preprocess_slicer.py` | 3D Slicer | Smoothed label map and STL surface |
| Centerline and endpoint extraction | `extract_centerlines_slicer.py` | 3D Slicer + SlicerVMTK | Markups JSON and centerline JSON files |
| Inlet/outlet cutting | `cut_stl.py` | Python + PyVista | Cut STL and cut-plane metadata |
| Surface repair, remeshing, and STEP fitting | `wrap_scripts.py` | Geomagic Wrap | Repaired STL and STEP model |
| Boundary naming | `spaceclaim.py` | Ansys SpaceClaim | SCDOC with `wall`, `fluid`, `inlet`, and `outlet` named selections |
| Score aggregation | `score.py` | Python | `TP`, `FP`, `FN`, `TdP`, and CFD-AS |

The supplied supplementary code does not include a Fluent Meshing or OpenFOAM case-generation/solver script. Those proprietary or environment-specific stages feed their final binary status into `BFA`; `score.py` makes that final decision auditable and reproducible once the flow stage has been run.

## Formula

For an aneurysm-level prediction, let `VTA`, `MGA`, and `BFA` be the binary outcomes of vascular topology inspection, mesh generation, and blood-flow computation. A prediction is CFD-applicable only if all three are one. With `TdP` the number of CFD-applicable true-positive predictions,

```text
CFD-AS = TdP / (TP + FP + FN)
```

`VTA`, `MGA`, and `BFA` diagnose failure modes; they are not substitutes for Dice, HD95, clDice, or BIoU.

## Quick start: scoring

Install the dependencies needed by the open Python utilities:

```bash
python -m pip install -r cfd_as/requirements-open.txt
```

Create a CSV containing one row per evaluated case. The required columns are `case_id`, `ground_truth_positive`, and `predicted_positive`; `vta`, `mga`, and `bfa` are required for true-positive predictions. Use `0`/`1`, `true`/`false`, or `yes`/`no` for binary values.

```bash
python cfd_as/score.py \
  --input cfd_as/example_cases.csv \
  --output results/cfd_as_summary.json
```

## Geometry workflow

The Slicer scripts run in 3D Slicer's embedded Python, for example:

```bash
Slicer --no-main-window --python-script cfd_as/preprocess_slicer.py -- \
  --input-dir masks --output-dir work/preprocess
```

`extract_centerlines_slicer.py` requires the SlicerVMTK `ExtractCenterline` module. `wrap_scripts.py` and `spaceclaim.py` are intended for the Python consoles or batch runtimes of licensed Geomagic Wrap and Ansys SpaceClaim installations, respectively. They are included to document and reproduce the complete published geometry workflow; their commercial dependencies are not bundled.

The supplied supplementary script used a cut ratio of `0.02`. The final MICCAI paper describes a one-fifth terminal-segment position. `cut_stl.py` therefore exposes `--cut-ratio` explicitly and defaults to the supplementary-code value; set the value appropriate to the protocol being reproduced and report it with results.

## Input and output conventions

- Masks are binary NIfTI files (`.nii` or `.nii.gz`).
- Slicer markups are saved as JSON.
- STL coordinates and Slicer markups use the RAS/LPS conversion implemented in `cut_stl.py`.
- `cut_info.json` records each cut-plane origin and inlet/outlet assignment for later use in SpaceClaim.
- The score CSV must contain no patient identifiers. Use project-specific pseudonymous case IDs.

No patient-level data, meshes, or CFD outputs are included in this repository.

## License

The IAVS-authored code in this directory is released under the [MIT License](LICENSE). Please also cite IAVS and comply with the licenses of 3D Slicer, SlicerVMTK, PyVista/VTK, Geomagic Wrap, Ansys SpaceClaim, and any CFD solver used in your workflow.
