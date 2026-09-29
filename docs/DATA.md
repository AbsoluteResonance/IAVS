# IAVS data card and access policy

## Scope

IAVS combines 641 three-dimensional MRA examinations from three external resources and an in-house cohort. It contains 587 expert-verified intracranial aneurysm and parent-vessel annotations; 124 examinations are aneurysm-negative. For CFD-oriented cases, the data model additionally includes surface models, centerlines, boundary-labelled meshes, and hemodynamic-analysis outputs.

The repository contains documentation and, in future versions, reproducible processing code. It does **not** contain raw images, masks, meshes, centerlines, CFD outputs, trained weights, or patient-level metadata.

## Benchmark partitions

| Partition | Images | Public-source cases | Private cases | Access status |
| --- | ---: | ---: | ---: | --- |
| Train/validation | 467 | 175 | 292 | Mixed-source; not distributed as a bundle |
| Set A | 76 | 76 | 0 | Source data must be obtained from the original providers |
| Set B | 98 | 0 | 98 | Not public |
| **Total** | **641** | **251** | **390** | — |

The 587 figure counts individual aneurysms, not examinations. A single examination can contain more than one aneurysm; negative examinations have no aneurysm annotation.

## Source datasets and redistribution boundary

| Source | IAVS use | How to obtain the original data | Redistribution through IAVS |
| --- | --- | --- | --- |
| ADAM challenge | External source data; original IA annotations were harmonized for IAVS | [ADAM challenge](https://adam.isi.uu.nl/details/) | **Not permitted.** ADAM terms prohibit giving the downloaded data, reference standard, or derived data to people outside the registered team. Users must obtain access directly from ADAM. |
| INSTED challenge | External source data; original IA annotations were harmonized for IAVS | [INSTED challenge record](https://doi.org/10.5281/zenodo.10990482) and its [CodaBench page](https://www.codabench.org/competitions/2139/) | No IAVS binary copy is provided. Access and any reuse must follow the current terms set by the dataset owners. |
| Royal Brisbane TOF-MRA Intracranial Aneurysm Database | External source data, including IA-vessel information where available | [OpenNeuro ds005096](https://openneuro.org/datasets/ds005096) | The original record declares CC0. IAVS does not mirror it; use the canonical source and cite its dataset paper. Versioned IAVS derivative assets, where released, will identify this provenance and their own license. |
| In-house cohort | Clinical data and IAVS-specific expert verification | Not applicable | **Not public.** No private image, annotation, geometry, CFD output, identifier, or split membership is released. |

This table takes precedence over a broad label such as “public data.” A source may be publicly reachable while still prohibiting redistribution. The ADAM restriction applies to its data and derivatives, so no ADAM-derived crop, mask, mesh, centerline, CFD result, case list, or result file may be added to this repository or a public release.

## Release plan for public IAVS derivatives

Publicly releasable IAVS-derived artifacts will be deposited as versioned archives outside Git after provenance, license compatibility, and de-identification review. Each archive will include:

- a dataset version and release date;
- a data dictionary and file manifest;
- source provenance and required citations;
- a license for the new derivative material;
- a description of preprocessing and quality control; and
- checksums for archive integrity.

Until a release DOI is added here, the only supported route to source images and labels is the original provider. The absence of a file from this repository does not grant permission to reconstruct or redistribute it from an IAVS-derived artifact.

## Intended use

IAVS is intended for research on aneurysm localization, IA-vessel segmentation, geometric robustness, and CFD applicability evaluation. It is not a clinical decision-support product and does not establish a patient-specific treatment workflow.

## Required citations

Please cite the IAVS paper for this benchmark. When using a source dataset, also cite and acknowledge that source according to its terms:

- ADAM: Timmins et al., *NeuroImage* 238, 118216 (2021).
- INSTED: Chen et al., *Intracranial Aneurysm and Intracranial Artery Stenosis Detection and Segmentation Challenge* (2024), [doi:10.5281/zenodo.10990482](https://doi.org/10.5281/zenodo.10990482).
- Royal Brisbane: de Nys et al., *Scientific Data* (2024), [doi:10.1038/s41597-024-03397-8](https://doi.org/10.1038/s41597-024-03397-8).
