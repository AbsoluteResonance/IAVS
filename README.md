# IAVS

**IAVS: A Multi-Center Dataset and Applicability Evaluation System for Computational Fluid Dynamics-Oriented Intracranial Aneurysm Segmentation**

> Feiyang Xiao, Yichi Zhang, Xigui Li, Yuanye Zhou, Chen Jiang, Xin Guo, Limei Han, Yuxin Li, Fengping Zhu, and Yuan Cheng. MICCAI 2026.

[[Paper](https://papers.miccai.org/miccai-2026/paper/6086_paper.pdf)] [[Project page](https://papers.miccai.org/miccai-2026/0485-Paper6086.html)] [[Data access](docs/DATA.md)]

IAVS is a multi-center benchmark for intracranial aneurysm (IA) and parent-vessel segmentation designed around a practical question: can a segmentation be converted into a simulation-ready computational fluid dynamics (CFD) model? Alongside conventional image-based metrics, IAVS introduces the **CFD-Applicability Score (CFD-AS)** to assess whether a correctly localized aneurysm prediction passes vascular topology inspection, mesh generation, and blood-flow computation.

## Dataset at a glance

IAVS contains 641 three-dimensional MRA examinations, 587 expert-verified aneurysm and IA-vessel annotations, and 124 aneurysm-negative examinations. Cases are annotated and quality-controlled for downstream CFD use. The complete IAVS data model comprises seven asset types:

1. Whole-brain MRA image
2. Intracranial-aneurysm mask
3. IA-vessel mask
4. STL surface model with cut inlet and outlet faces
5. Vascular centerlines
6. Mesh files with boundary annotations
7. CFD analysis outputs

| Partition | Images | Public-source cases | Private cases | Intended use |
| --- | ---: | ---: | ---: | --- |
| Train/validation | 467 | 175 | 292 | Method development |
| Set A | 76 | 76 | 0 | Public-source internal evaluation |
| Set B | 98 | 0 | 98 | Private clinical-scenario evaluation |
| **Total** | **641** | **251** | **390** | Benchmark |

The data were integrated from ADAM, INSTED, the Royal Brisbane TOF-MRA Intracranial Aneurysm Database, and an in-house cohort. IAVS-derived IA-vessel and CFD assets are not interchangeable with the original source annotations.

## Data access and redistribution

No patient-level image, annotation, mesh, or CFD-result file is stored in this Git repository. This is intentional: public access to a source dataset does not necessarily grant permission to redistribute it or its derivatives.

The [data card](docs/DATA.md) records the exact release boundary, source links, attribution requirements, and access restrictions. In particular, ADAM data and all data derived from it must be obtained directly from the challenge organizers; private IAVS cases are not released. The Royal Brisbane source dataset is CC0 and can be downloaded from [OpenNeuro ds005096](https://openneuro.org/datasets/ds005096). Any IAVS-derived public assets will be versioned and deposited separately rather than committed to Git.

## CFD applicability evaluation

For a predicted segmentation, IAVS defines three binary checks:

- **VTA** — vascular topology availability;
- **MGA** — mesh generation availability;
- **BFA** — blood-flow availability.

A true-positive prediction is CFD-applicable only when all three checks succeed. With `TdP` denoting the number of such predictions, CFD-AS is

```text
CFD-AS = TdP / (TP + FP + FN).
```

VTA, MGA, and BFA are diagnostic stages rather than stand-alone quality metrics. They identify whether a failure arose from a topological defect, unsuccessful meshing, or failure in the subsequent flow simulation. The reference pipeline comprises topology inspection, morphological preprocessing, surface and centerline extraction, inlet/outlet cutting, mesh enhancement and fitting, boundary assignment, meshing, and CFD computation.

The runnable CFD-AS implementation, its environment specification, and example inputs will be released in `cfd_as/` in a subsequent update. It is kept separate from this documentation-only initial release while the code and third-party dependencies are being cleaned for publication.

## Repository status

| Component | Status |
| --- | --- |
| Paper, citation, and dataset documentation | Available |
| Source-data access and redistribution policy | Available |
| Public IAVS derivative-data release | In preparation; see the data card |
| CFD-AS implementation | In preparation |
| Baseline training/inference code and weights | In preparation |

## Citation

```bibtex
@InProceedings{Xiao2026IAVS,
  author    = {Feiyang Xiao and Yichi Zhang and Xigui Li and Yuanye Zhou and
               Chen Jiang and Xin Guo and Limei Han and Yuxin Li and
               Fengping Zhu and Yuan Cheng},
  title     = {IAVS: A Multi-Center Dataset and Applicability Evaluation System
               for Computational Fluid Dynamics-Oriented Intracranial Aneurysm Segmentation},
  booktitle = {Medical Image Computing and Computer Assisted Intervention (MICCAI)},
  year      = {2026}
}
```

## Contact

For questions about IAVS, data access, or the CFD-AS release, please open a GitHub issue after the issue tracker is enabled, or contact the corresponding authors listed in the paper.
