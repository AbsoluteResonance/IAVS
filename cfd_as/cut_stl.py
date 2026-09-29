#!/usr/bin/env python3
"""Cut an STL at terminal centerline locations and save boundary metadata."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyvista as pv


def ras_to_lps(point: list[float] | np.ndarray) -> np.ndarray:
    point = np.asarray(point, dtype=float)
    return np.array((-point[0], -point[1], point[2]), dtype=float)


@dataclass
class Centerline:
    points: np.ndarray
    radii: np.ndarray
    terminal_index: int
    kind: str = "outlet"

    @property
    def length(self) -> float:
        return float(np.linalg.norm(np.diff(self.points, axis=0), axis=1).sum())

    def point_at_terminal_distance(
        self, cut_ratio: float, min_radius_mm: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Return two adjacent cut points and the terminal endpoint.

        `cut_ratio` is measured from the terminal endpoint toward the vessel.
        """
        if len(self.points) < 2:
            raise ValueError("A centerline needs at least two points")
        if not 0.0 < cut_ratio < 1.0:
            raise ValueError("cut_ratio must lie between zero and one")

        indices = np.arange(len(self.points))
        if self.terminal_index == 0:
            indices = indices[::-1]
        terminal_points = self.points[indices]
        terminal_radii = self.radii[indices]
        distances = np.concatenate(
            ([0.0], np.cumsum(np.linalg.norm(np.diff(terminal_points, axis=0), axis=1)))
        )
        position = int(np.argmin(np.abs(distances - self.length * cut_ratio)))
        position = min(position, len(indices) - 2)
        while position < len(indices) - 2 and terminal_radii[position] < min_radius_mm:
            position += 1
        return terminal_points[position], terminal_points[position + 1], terminal_points[0]


def read_centerline(path: Path) -> Centerline | None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    markup = payload["markups"][0]
    control_points = markup.get("controlPoints", [])
    if len(control_points) < 2:
        return None
    points = np.asarray([ras_to_lps(item["position"]) for item in control_points])
    radii = np.asarray(markup["measurements"][5]["controlPointValues"], dtype=float)
    if len(radii) != len(points):
        raise ValueError(f"{path}: centerline radius count does not match point count")
    return Centerline(points=points, radii=radii, terminal_index=-1)


def load_centerlines(centerline_dir: Path, endpoints_path: Path) -> list[Centerline]:
    lines = [line for path in sorted(centerline_dir.glob("*.json")) if (line := read_centerline(path))]
    if not lines:
        raise FileNotFoundError(f"No valid centerline JSON files found in {centerline_dir}")

    endpoint_payload = json.loads(endpoints_path.read_text(encoding="utf-8"))
    endpoint_points = endpoint_payload["markups"][0]["controlPoints"]
    if not endpoint_points:
        raise ValueError(f"{endpoints_path}: no endpoint control points")
    positions = np.asarray([ras_to_lps(item["position"]) for item in endpoint_points])
    selected = [bool(item.get("selected", False)) for item in endpoint_points]

    endpoint_membership: dict[tuple[float, float, float], list[tuple[int, int]]] = {}
    for line_id, line in enumerate(lines):
        for point_id in (0, len(line.points) - 1):
            endpoint_membership.setdefault(tuple(line.points[point_id]), []).append((line_id, point_id))

    for members in endpoint_membership.values():
        if len(members) != 1:
            continue
        line_id, terminal_index = members[0]
        line = lines[line_id]
        terminal = line.points[terminal_index]
        closest = int(np.argmin(np.linalg.norm(positions - terminal, axis=1)))
        line.terminal_index = terminal_index
        # The original Slicer markup convention labels selected endpoints as outlets.
        line.kind = "outlet" if selected[closest] else "inlet"

    terminal_lines = [line for line in lines if line.terminal_index >= 0]
    if not terminal_lines:
        raise ValueError("No terminal centerlines were identified")
    return terminal_lines


def largest_component(mesh: pv.PolyData) -> pv.PolyData:
    blocks = mesh.split_bodies().as_polydata_blocks()
    if not blocks:
        raise ValueError("Cutting produced an empty mesh")
    return max(blocks, key=lambda block: block.volume)


def cut_mesh(mesh: pv.PolyData, p1: np.ndarray, p2: np.ndarray, terminal: np.ndarray) -> pv.PolyData:
    normal = p2 - p1
    normal /= np.linalg.norm(normal)
    origin = (p1 + p2) / 2.0
    halves = (mesh.clip(normal=normal, origin=origin), mesh.clip(normal=-normal, origin=origin))
    if halves[0].n_cells == 0:
        return largest_component(halves[1])
    if halves[1].n_cells == 0:
        return largest_component(halves[0])

    # Remove the component adjacent to the terminal endpoint; retain the vascular model.
    candidates: list[tuple[float, pv.PolyData]] = []
    for half in halves:
        for component in half.split_bodies().as_polydata_blocks():
            candidates.append((float(np.min(np.linalg.norm(component.points - terminal, axis=1))), component))
    if not candidates:
        raise ValueError("Cutting produced no components")
    closest = min(candidates, key=lambda item: item[0])[1]
    retained = [component for _, component in candidates if component is not closest]
    if not retained:
        # Fall back to the larger half if clipping only produced one useful component.
        return largest_component(max(halves, key=lambda half: half.volume))
    result = retained[0]
    for component in retained[1:]:
        result = result.merge(component)
    return largest_component(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesh", type=Path, required=True, help="Input STL")
    parser.add_argument("--centerline-dir", type=Path, required=True)
    parser.add_argument("--endpoints", type=Path, required=True, help="Slicer endpoint markup JSON")
    parser.add_argument("--output-mesh", type=Path, required=True)
    parser.add_argument("--cut-info", type=Path, required=True)
    parser.add_argument("--cut-ratio", type=float, default=0.02)
    parser.add_argument("--min-radius-mm", type=float, default=0.3)
    args = parser.parse_args()

    mesh = pv.read(args.mesh)
    cut_info: list[dict[str, object]] = []
    for line in load_centerlines(args.centerline_dir, args.endpoints):
        p1, p2, terminal = line.point_at_terminal_distance(args.cut_ratio, args.min_radius_mm)
        mesh = cut_mesh(mesh, p1, p2, terminal)
        cut_info.append({"plane_origin": ((p1 + p2) / 2.0).tolist(), "in_out": line.kind})

    args.output_mesh.parent.mkdir(parents=True, exist_ok=True)
    args.cut_info.parent.mkdir(parents=True, exist_ok=True)
    mesh.save(args.output_mesh)
    args.cut_info.write_text(json.dumps(cut_info, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
