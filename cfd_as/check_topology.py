#!/usr/bin/env python3
"""Screen binary NIfTI masks for Euler-number topology failures."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import nibabel as nib
from skimage.measure import euler_number


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--connectivity",
        type=int,
        default=3,
        choices=(1, 3),
        help="scikit-image connectivity for 3D Euler-number computation",
    )
    args = parser.parse_args()

    masks = sorted([*args.input_dir.glob("*.nii"), *args.input_dir.glob("*.nii.gz")])
    if not masks:
        raise FileNotFoundError(f"No NIfTI masks found in {args.input_dir}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("case_id", "euler_number", "vta"))
        writer.writeheader()
        for mask_path in masks:
            mask = nib.load(mask_path).get_fdata() > 0
            euler = int(euler_number(mask, connectivity=args.connectivity))
            writer.writerow(
                {
                    "case_id": mask_path.name.removesuffix(".nii.gz").removesuffix(".nii"),
                    "euler_number": euler,
                    "vta": int(euler > 0),
                }
            )


if __name__ == "__main__":
    main()
