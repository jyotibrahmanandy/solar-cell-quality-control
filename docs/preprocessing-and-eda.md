# Preprocessing & Exploratory Data Analysis (EDA)

This document describes the dataset inspection and image pipeline recorded in [`notebooks/01_dataset_exploration.ipynb`](../notebooks/01_dataset_exploration.ipynb), and how the final model receives images in [`app/app.py`](../app/app.py).

## Dataset organization

The notebook examines the source EL dataset and the curated five-class perovskite/tandem dataset. The training dataset used by the final classifier is organized as:

```text
data/custom/perovskite_tandem/
├── train/
│   ├── functional/
│   └── defect_*/
├── val/
│   ├── functional/
│   └── defect_*/
└── test/
    ├── functional/
    └── defect_*/
```

The five class folders are `functional`, `defect_halide_segregation`, `defect_layer_delamination`, `defect_phase_degradation`, and `defect_pinhole`. TensorFlow infers labels from these subfolder names; keep the folder names consistent across all splits and with the saved class-name list.

## Exploratory checks

The notebook's EDA workflow includes:

1. Checking dataset paths and summarizing folder contents.
2. Counting image files by extension, reviewing filenames and image ID ranges, and finding non-image files.
3. Reading class annotations, counting annotated defects, matching annotations to available images, and checking image-name overlap between groups.
4. Viewing representative images from source groups and from the curated training classes.
5. Counting images by class in the train, validation, and test splits and confirming that TensorFlow discovers the expected class folders.

These checks help reveal missing files, unexpected formats, label or folder inconsistencies, and possible overlap between groups. The notebook includes exploration of an original source dataset as well as the curated training data; the classifier app uses the five-class `data/custom/perovskite_tandem` dataset and the saved model artifacts under `models/`.

## Training data loading and preprocessing

The notebook loads each split with `tf.keras.utils.image_dataset_from_directory` using:

| Setting | Value |
| --- | --- |
| Image size | 224 × 224 pixels |
| Batch size | 32 |
| Training shuffle | Enabled, seed `42` |
| Validation/test shuffle | Disabled |

The model contains preprocessing layers, applied as part of the model's forward pass:

- **Rescaling:** maps pixel values from the image loader's 0–255 range to 0–1 using `1/255`.
- **Random horizontal flip:** applied during training.
- **Random rotation:** up to 5% as configured in the notebook.
- **Random zoom:** up to 10% as configured in the notebook.

These augmentation layers are included in the training model; the model's inference behavior does not apply random augmentation. The notebook's MobileNetV2 classifier uses 224 × 224 RGB inputs. Stage 2 adds a five-class softmax head and fine-tunes the later feature-extractor layers.

## Inference preprocessing

The Streamlit app accepts JPEG and PNG files. It converts each upload to RGB, resizes it to 224 × 224 pixels, turns it into a NumPy array, and adds a batch dimension before prediction. It does **not** divide the pixels by 255 in the app because the saved model includes the rescaling layer. Keep this behavior aligned with the model to avoid scaling input twice or omitting scaling.

## Reproducing the workflow

Open `notebooks/01_dataset_exploration.ipynb` in Jupyter and run cells in order, ensuring the dataset paths referenced by the notebook point to the local data. Some exploration cells refer to machine-specific absolute paths, so those paths may need adjustment on another computer. For model training, keep the `train`, `val`, and `test` folder structure and class names intact. The Streamlit app expects `models/final_solar_cell_quality_model.keras` and `models/stage2_class_names.json` relative to the repository root.
