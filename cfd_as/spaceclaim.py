"""Ansys SpaceClaim script for naming CFD boundary selections.

Run inside SpaceClaim's Python console. Configure the four paths in `main`.
"""

import json
import os


def match_faces_to_points(faces, points):
    matched = []
    for face in faces:
        nearest_point = min(
            range(len(points)),
            key=lambda index: min(
                ((vertex[0] * 1000.0 - points[index][0]) ** 2
                 + (vertex[1] * 1000.0 - points[index][1]) ** 2
                 + (vertex[2] * 1000.0 - points[index][2]) ** 2) ** 0.5
                for vertex in face
            ),
        )
        matched.append(nearest_point)
    return matched


def label_boundaries(stp_path, cut_info_path, output_path):
    DocumentOpen.Execute(stp_path)
    body = BodySelection.SelectAll()
    all_faces = list(body.ConvertToFaces().Faces)
    NamedSelection.Create(FaceSelection.Create(*all_faces), Selection.Empty())
    NamedSelection.Rename("group1", "wall")
    FixMissingFaces.FindAndFix(FixMissingFacesOptions())

    body = BodySelection.SelectAll()
    NamedSelection.Create(body, Selection.Empty())
    NamedSelection.Rename("group1", "fluid")
    fluid = Selection.CreateByGroups(SelectionType.Primary, "fluid")
    wall = Selection.CreateByGroups(SelectionType.Primary, "wall")
    inlet_outlet_faces = [face for face in fluid.ConvertToFaces().Faces if face not in wall.ConvertToFaces().Faces]
    face_vertices = [
        [[edge.Shape.EndPoint.X, edge.Shape.EndPoint.Y, edge.Shape.EndPoint.Z] for edge in list(face.Edges)]
        for face in inlet_outlet_faces
    ]

    cut_info = json.load(open(cut_info_path, "r"))
    points = [item["plane_origin"] for item in cut_info]
    inlet_ids = {index for index, item in enumerate(cut_info) if item["in_out"] == "inlet"}
    matched = match_faces_to_points(face_vertices, points)
    inlet_faces = [face for face, match in zip(inlet_outlet_faces, matched) if match in inlet_ids]
    outlet_faces = [face for face, match in zip(inlet_outlet_faces, matched) if match not in inlet_ids]

    NamedSelection.Create(FaceSelection.Create(*inlet_faces), Selection.Empty())
    NamedSelection.Rename("group1", "inlet")
    NamedSelection.Create(FaceSelection.Create(*outlet_faces), Selection.Empty())
    NamedSelection.Rename("group1", "outlet")
    DocumentSave.Execute(output_path)
    CloseWindow()


if __name__ == "__main__":
    STP_DIR = r"<IAVS_WORKDIR>\\stp_1"
    CUT_INFO_DIR = r"<IAVS_WORKDIR>\\cut_info"
    SCDOC_DIR = r"<IAVS_WORKDIR>\\scdoc"
    os.makedirs(SCDOC_DIR, exist_ok=True)
    for filename in sorted(name for name in os.listdir(STP_DIR) if name.endswith(".stp")):
        stem = filename[:-4]
        label_boundaries(
            os.path.join(STP_DIR, filename),
            os.path.join(CUT_INFO_DIR, stem + ".json"),
            os.path.join(SCDOC_DIR, stem + ".scdoc"),
        )
