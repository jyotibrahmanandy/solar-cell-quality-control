"""Generate a DOCX analysis of feature extraction, training, and testing."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "feature_extraction_model_training_testing_analysis.docx"
ARTIFACTS = ROOT / "artifacts" / "model_analysis"


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Shading Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for cell, value in zip(table.rows[0].cells, headers):
        cell.text = str(value)
    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = str(value)


def add_figure(doc, path):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(6.2))


def make_charts():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    stages = ["Stage 1\nbinary", "Stage 2\nfrozen", "Fine-tuned\n(final)"]
    accuracy = [0.562, 0.837, 0.960]
    macro_f1 = [0.333, 0.832, 0.960]
    x = np.arange(len(stages))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(x - 0.18, accuracy, width=0.36, label="Accuracy", color="#5b9bd5")
    ax.bar(x + 0.18, macro_f1, width=0.36, label="Macro F1", color="#ed7d31")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Measured test performance")
    ax.set_xticks(x, stages)
    ax.legend()
    fig.tight_layout()
    path = ARTIFACTS / "model_performance.png"
    fig.savefig(path, dpi=160)
    plt.close(fig)

    cm = np.array([[60, 0, 0, 0, 0], [0, 57, 0, 0, 3], [7, 0, 53, 0, 0], [0, 0, 0, 60, 0], [2, 0, 0, 0, 58]])
    labels = ["Halide", "Layer", "Phase", "Pinhole", "Functional"]
    fig, ax = plt.subplots(figsize=(5.5, 5))
    image = ax.imshow(cm, cmap="Blues")
    fig.colorbar(image, ax=ax, fraction=0.046)
    ax.set(xticks=range(5), yticks=range(5), xticklabels=labels, yticklabels=labels, xlabel="Predicted", ylabel="True", title="Final-model confusion matrix")
    for i in range(5):
        for j in range(5):
            ax.text(j, i, cm[i, j], ha="center", va="center", color="white" if cm[i, j] > 30 else "black")
    fig.tight_layout()
    path_cm = ARTIFACTS / "final_confusion_matrix.png"
    fig.savefig(path_cm, dpi=160)
    plt.close(fig)
    return path, path_cm


def build_report():
    performance, confusion = make_charts()
    doc = Document()
    doc.styles["Normal"].font.name = "Aptos"
    doc.styles["Normal"].font.size = Pt(10)
    title = doc.add_heading("Feature Extraction, Model Training & Testing Analysis", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_paragraph("Solar Cell Quality Control | Evidence from saved Keras models and held-out test sets")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("1. Executive summary", level=1)
    doc.add_paragraph(
        "The project uses MobileNetV2 transfer learning for solar-cell electroluminescence image classification. "
        "A binary model is trained first, then a five-class model reuses the feature extractor for defect-type "
        "classification. Fine-tuning the deeper feature extractor improves the measured five-class test accuracy "
        "from 83.67% to 96.00% and macro F1 from 0.8324 to 0.9603."
    )
    add_table(doc, ["Model", "Test images", "Accuracy", "Macro F1", "Parameters"], [
        ["Stage 1 binary", 600, "56.17% (Keras evaluate)", "0.3333*", "2,259,265"],
        ["Stage 2 frozen", 300, "83.67%", "0.8324", "2,264,389"],
        ["Stage 2 fine-tuned / final", 300, "96.00%", "0.9603", "2,264,389"],
    ])
    doc.add_paragraph("*The Stage 1 classification report produced 50.00% accuracy and all-positive-class predictions, while Keras evaluate returned 56.17%. This inconsistency is documented as a reproducibility issue requiring a deterministic evaluation pass.")
    add_figure(doc, performance)

    doc.add_heading("2. Feature extraction architecture", level=1)
    doc.add_paragraph(
        "The model pipeline uses image augmentation, normalization, a MobileNetV2 convolutional backbone, "
        "global average pooling, dropout, and a dense classification head. The backbone provides learned visual "
        "features such as edges, textures, cell boundaries, and defect patterns; global average pooling converts "
        "feature maps into a compact vector before classification."
    )
    add_table(doc, ["Component", "Role"], [
        ["Input", "224 × 224 RGB electroluminescence image"],
        ["Data augmentation", "Training-only variation to improve robustness"],
        ["Normalization", "Aligns input pixel distribution with model training"],
        ["MobileNetV2 backbone", "Pre-trained convolutional feature extractor"],
        ["GlobalAveragePooling2D", "Reduces spatial feature maps to a feature vector"],
        ["Dropout (0.3)", "Regularization before classification"],
        ["Dense head", "2 outputs for Stage 1; 5 softmax outputs for Stage 2"],
    ])

    doc.add_heading("3. Training strategy", level=1)
    doc.add_paragraph(
        "Stage 1 performs binary Correct/Defective classification. Stage 2 replaces the binary head with a five-class "
        "softmax head for functional, halide segregation, layer delamination, phase degradation, and pinhole classes. "
        "The notebook freezes the Stage 1 feature extractor during initial Stage 2 training. A later fine-tuning phase "
        "unfreezes deeper layers and recompiles with Adam at a learning rate of 1e-5."
    )
    add_table(doc, ["Phase", "Objective", "Loss / optimizer", "Observed outcome"], [
        ["Stage 1", "Learn binary quality representations", "Sparse categorical cross-entropy / Adam", "Saved MobileNetV2 binary model"],
        ["Stage 2 transfer", "Map frozen features to five defect classes", "Sparse categorical cross-entropy / Adam", "83.67% test accuracy"],
        ["Fine-tuning", "Adapt deeper features to perovskite/tandem defects", "Sparse categorical cross-entropy / Adam, 1e-5", "96.00% test accuracy"],
    ])

    doc.add_heading("4. Final-model testing analysis", level=1)
    doc.add_paragraph(
        "The final model was loaded from both final_solar_cell_quality_model.keras and the fine-tuned Stage 2 model; "
        "both produced the same 300-image test results. The test set is balanced with 60 images per class."
    )
    add_table(doc, ["Class", "Precision", "Recall", "F1", "Support"], [
        ["Halide segregation", "0.8696", "1.0000", "0.9302", 60],
        ["Layer delamination", "1.0000", "0.9500", "0.9744", 60],
        ["Phase degradation", "1.0000", "0.8833", "0.9381", 60],
        ["Pinhole", "1.0000", "1.0000", "1.0000", 60],
        ["Functional", "0.9508", "0.9667", "0.9587", 60],
        ["Macro average", "0.9641", "0.9600", "0.9603", 300],
    ])
    add_figure(doc, confusion)
    doc.add_paragraph(
        "The dominant residual error is confusion of phase degradation with halide segregation: 7 phase-degradation "
        "images were predicted as halide segregation. Three layer-delamination images and two functional images were "
        "also misclassified. Pinhole detection was perfect on this test set."
    )

    doc.add_heading("5. Interpretation", level=1)
    for item in [
        "Fine-tuning is materially beneficial: accuracy rises by 12.33 percentage points over the frozen Stage 2 model.",
        "The final model is strongest on pinhole and layer-delamination images and weakest on phase-degradation recall.",
        "Balanced test support makes macro-averaged metrics representative of the class-level behavior.",
        "The result is a five-class diagnostic model; the functional class is the pass condition used by the application.",
    ]:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("6. Validation caveats and recommendations", level=1)
    for item in [
        "The Stage 1 evaluation is internally inconsistent: Keras evaluate and the separately generated classification report disagree. Re-run evaluation with augmentation disabled or deterministic preprocessing before using Stage 1 metrics in a publication.",
        "Keep augmentation layers inactive during validation and testing, and verify that the deployed preprocessing exactly matches training.",
        "Report confidence calibration and class-specific error costs before production use, especially for false functional predictions.",
        "Expand the held-out test set with images from different acquisition conditions and manufacturers to measure domain robustness.",
        "Track model version, class-name order, image manifest, random seeds, and preprocessing configuration with every training run.",
    ]:
        doc.add_paragraph(item, style="List Bullet")
    doc.add_paragraph("Source artifacts: models/*.keras, models/stage2_class_names.json, and notebooks/01_dataset_exploration.ipynb.")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(REPORT)
    print(REPORT)


if __name__ == "__main__":
    build_report()
