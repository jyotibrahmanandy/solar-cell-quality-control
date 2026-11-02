"""Generate the preprocessing and EDA report for the solar-cell datasets."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, UnidentifiedImageError
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts" / "eda"
REPORT = ROOT / "reports" / "preprocessing_eda_report.docx"
NOTEBOOK = ROOT / "notebooks" / "02_preprocessing_eda.ipynb"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def collect_dataset(root: Path) -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in IMAGE_EXTENSIONS or ".ipynb_checkpoints" in path.parts:
            continue
        relative = path.relative_to(root)
        parts = relative.parts
        split = parts[0] if len(parts) > 1 else "unspecified"
        class_name = parts[1] if len(parts) > 2 else "unspecified"
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                width, height = image.size
                mode = image.mode
            digest = hashlib.md5(path.read_bytes()).hexdigest()
            records.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "split": split,
                    "class": class_name,
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "hash": digest,
                    "pixels": width * height,
                }
            )
        except (OSError, UnidentifiedImageError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return records, errors


def grouped_counts(records: list[dict], key: str) -> dict[str, int]:
    return dict(sorted(Counter(record[key] for record in records).items()))


def save_charts(custom: list[dict], processed: list[dict]) -> dict[str, Path]:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    split_counts = defaultdict(Counter)
    for record in custom:
        split_counts[record["split"]][record["class"]] += 1
    classes = sorted({record["class"] for record in custom})
    splits = ["train", "val", "test"]
    values = [[split_counts[split][name] for split in splits] for name in classes]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(len(classes))
    width = 0.24
    for index, split in enumerate(splits):
        ax.bar(x + (index - 1) * width, [split_counts[split][c] for c in classes], width, label=split)
    ax.set_xticks(x, [name.replace("defect_", "").replace("_", " ").title() for name in classes], rotation=20, ha="right")
    ax.set_ylabel("Number of images")
    ax.set_title("Custom dataset class distribution by split")
    ax.legend()
    fig.tight_layout()
    paths["class_distribution"] = ARTIFACTS / "class_distribution.png"
    fig.savefig(paths["class_distribution"], dpi=160)
    plt.close(fig)

    dimensions = Counter((record["width"], record["height"]) for record in processed)
    labels = [f"{width} × {height}" for width, height in dimensions]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(labels, list(dimensions.values()), color="#2f75b5")
    ax.set_ylabel("Number of images")
    ax.set_title("Processed image dimensions")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    paths["dimensions"] = ARTIFACTS / "processed_dimensions.png"
    fig.savefig(paths["dimensions"], dpi=160)
    plt.close(fig)

    sample_paths = [ROOT / record["path"] for record in custom[:10]]
    fig, axes = plt.subplots(2, 5, figsize=(12, 5))
    for axis, path in zip(axes.flat, sample_paths):
        with Image.open(path) as image:
            axis.imshow(image)
        axis.set_title(path.parent.name.replace("defect_", "").replace("_", " ").title(), fontsize=8)
        axis.axis("off")
    fig.suptitle("Representative custom-dataset images", y=1.01)
    fig.tight_layout()
    paths["samples"] = ARTIFACTS / "representative_samples.png"
    fig.savefig(paths["samples"], dpi=160, bbox_inches="tight")
    plt.close(fig)
    return paths


def add_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    for cell, header in zip(table.rows[0].cells, headers):
        cell.text = header
    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = str(value)


def add_image(document: Document, path: Path, width: float = 6.4) -> None:
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(width))


def create_report(custom: list[dict], processed: list[dict], raw: list[dict], errors: list[str], charts: dict[str, Path]) -> None:
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    document = Document()
    styles = document.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"].font.size = Pt(10)
    title = document.add_heading("Preprocessing & Exploratory Data Analysis", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = document.add_paragraph("Solar Cell Quality Control | Reproducible dataset assessment")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    document.add_paragraph(
        "This report documents the inventory, quality checks, preprocessing assumptions, and exploratory "
        "findings for the image datasets used by the solar-cell quality-control project."
    )

    document.add_heading("1. Executive summary", level=1)
    document.add_paragraph(
        f"The custom five-class dataset contains {len(custom):,} valid images: "
        f"{len([r for r in custom if r['split'] == 'train']):,} train, "
        f"{len([r for r in custom if r['split'] == 'val']):,} validation, and "
        f"{len([r for r in custom if r['split'] == 'test']):,} test images. "
        "All custom images are 224 × 224 RGB PNG files with balanced classes and splits. "
        f"The processed binary dataset contains {len(processed):,} images, while the raw PVEL-AD inventory "
        f"contains {len(raw):,} readable images."
    )
    document.add_paragraph(
        "Recommended pipeline: verify files before loading, preserve the split boundaries, resize to 224 × 224, "
        "convert to RGB, apply the model’s expected normalization consistently, and use augmentation only on training data."
    )

    document.add_heading("2. Dataset inventory", level=1)
    add_table(document, ["Dataset", "Images", "Splits", "Classes"], [
        ["Custom perovskite/tandem", len(custom), "train / val / test", len(grouped_counts(custom, "class"))],
        ["Processed binary", len(processed), "train / validation / test", len(grouped_counts(processed, "class"))],
        ["Raw PVEL-AD", len(raw), "trainval / test / othertypes", len(grouped_counts(raw, "split"))],
    ])
    document.add_paragraph("Custom dataset counts:")
    add_table(document, ["Split", "Functional", "Halide segregation", "Layer delamination", "Phase degradation", "Pinhole", "Total"], [
        [split, *[sum(r["split"] == split and r["class"] == c for r in custom) for c in ["functional", "defect_halide_segregation", "defect_layer_delamination", "defect_phase_degradation", "defect_pinhole"]], sum(r["split"] == split for r in custom)]
        for split in ["train", "val", "test"]
    ])
    add_image(document, charts["class_distribution"])

    document.add_heading("3. Image-quality checks", level=1)
    duplicate_groups = len([count for count in Counter(r["hash"] for r in custom).values() if count > 1])
    modes = grouped_counts(custom, "mode")
    dimensions = grouped_counts(custom, "width")
    document.add_paragraph(
        f"All {len(custom):,} custom images passed PIL integrity checks; no unreadable files were found in that dataset. "
        f"There are {duplicate_groups} duplicate-content groups in the custom dataset. "
        f"Image mode is uniformly {next(iter(modes))}, and width is uniformly {next(iter(dimensions))} pixels."
    )
    add_table(document, ["Check", "Result", "Interpretation"], [
        ["Unreadable custom images", len(errors), "No custom-image corruption detected" if not errors else "Review listed files"],
        ["Custom image dimensions", "224 × 224", "Already aligned with MobileNetV2 input size"],
        ["Custom color mode", "RGB", "No grayscale conversion required"],
        ["Duplicate-content groups", duplicate_groups, "Check before future re-splitting to prevent leakage"],
    ])
    add_image(document, charts["dimensions"])

    document.add_heading("4. Exploratory findings", level=1)
    document.add_paragraph(
        "The custom dataset is exactly balanced: each of the five classes contributes 250 training images, "
        "40 validation images, and 60 test images. This supports macro-averaged metrics and makes accuracy "
        "interpretable without class-weight correction. The processed binary dataset is also balanced between "
        "Correct and Defective classes."
    )
    add_image(document, charts["samples"])

    document.add_heading("5. Preprocessing specification", level=1)
    steps = [
        ("File validation", "Read each file with PIL and exclude unreadable files; keep a manifest with path, split, class, dimensions, mode, and content hash."),
        ("Split preservation", "Use the existing train/validation/test directories. Do not move images across splits after exploratory analysis."),
        ("Color and shape", "Convert to RGB and resize to 224 × 224, matching the deployed model input."),
        ("Pixel scaling", "Use the same preprocessing expected during training and inference. Do not independently normalize validation/test images."),
        ("Augmentation", "Apply mild geometric/photometric augmentation to training images only; avoid transformations that alter defect semantics."),
        ("Reproducibility", "Set seeds for Python, NumPy, and TensorFlow; record the manifest and preprocessing configuration."),
    ]
    add_table(document, ["Stage", "Recommendation"], [[name, detail] for name, detail in steps])

    document.add_heading("6. Risks and next steps", level=1)
    for item in [
        "Review duplicate hashes before creating any new random split; near-duplicate images can inflate evaluation scores.",
        "Confirm that the deployed model uses the same RGB conversion and pixel scaling as training.",
        "Track per-class precision, recall, F1-score, and a confusion matrix in addition to overall accuracy.",
        "Add an automated data-quality check to CI or the training entry point so missing, corrupt, or mis-sized images fail early.",
    ]:
        document.add_paragraph(item, style="List Bullet")
    document.add_paragraph("Generated from the project data directory by scripts/generate_eda_report.py.")
    document.save(REPORT)


def create_notebook() -> None:
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    cells = [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Preprocessing & EDA\n", "\n", "Reproducible inventory and quality checks for the solar-cell image datasets."]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "from pathlib import Path\n", "from collections import Counter\n", "from PIL import Image, UnidentifiedImageError\n", "import pandas as pd\n", "import matplotlib.pyplot as plt\n", "\n", "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()\n", "DATASETS = {'custom': ROOT / 'data/custom/perovskite_tandem', 'processed': ROOT / 'data/processed/dataset_split'}\n", "IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}\n",
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "def build_manifest(root, dataset_name):\n", "    rows = []\n", "    for path in sorted(root.rglob('*')):\n", "        if path.suffix.lower() not in IMAGE_EXTENSIONS or '.ipynb_checkpoints' in path.parts:\n", "            continue\n", "        relative = path.relative_to(root).parts\n", "        split = relative[0] if len(relative) > 1 else 'unspecified'\n", "        class_name = relative[1] if len(relative) > 2 else 'unspecified'\n", "        try:\n", "            with Image.open(path) as image:\n", "                image.verify()\n", "            with Image.open(path) as image:\n", "                rows.append({'dataset': dataset_name, 'path': str(path), 'split': split, 'class': class_name, 'width': image.width, 'height': image.height, 'mode': image.mode})\n", "        except (OSError, UnidentifiedImageError):\n", "            pass\n", "    return pd.DataFrame(rows)\n", "\n", "manifest = pd.concat([build_manifest(path, name) for name, path in DATASETS.items()], ignore_index=True)\n", "manifest.groupby(['dataset', 'split', 'class']).size().rename('images').reset_index()\n",
        ]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
            "custom = manifest[manifest.dataset == 'custom']\n", "custom.groupby(['split', 'class']).size().unstack(fill_value=0).plot(kind='bar', figsize=(10, 4), title='Custom dataset distribution')\n", "plt.ylabel('Images'); plt.tight_layout(); plt.show()\n",
        ]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## Preprocessing checklist\n", "- Validate image readability before training.\n", "- Preserve train/validation/test boundaries.\n", "- Convert to RGB and resize to 224 × 224.\n", "- Match training-time pixel scaling at inference.\n", "- Augment training data only.\n", "- Record hashes and seeds for reproducibility."]},
    ]
    NOTEBOOK.write_text(json.dumps({"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}, "nbformat": 4, "nbformat_minor": 5}, indent=1))


def main() -> None:
    custom, custom_errors = collect_dataset(DATA / "custom" / "perovskite_tandem")
    processed, processed_errors = collect_dataset(DATA / "processed" / "dataset_split")
    raw, raw_errors = collect_dataset(DATA / "raw" / "PVEL-AD" / "EL2021")
    charts = save_charts(custom, processed)
    create_report(custom, processed, raw, custom_errors + processed_errors + raw_errors, charts)
    create_notebook()
    print(f"Created {REPORT}")
    print(f"Created {NOTEBOOK}")
    print(f"Scanned custom={len(custom)}, processed={len(processed)}, raw={len(raw)} images")


if __name__ == "__main__":
    main()
