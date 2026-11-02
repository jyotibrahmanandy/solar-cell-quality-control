# Solar Cell Quality Control

A Streamlit application that classifies an uploaded solar cell electroluminescence (EL) image as functional or as one of four defect classes. The app loads a trained Keras model and reports the predicted class, confidence, and a pass/fail quality status.

## Project contents

- `app/app.py` — Streamlit interface and image prediction flow.
- `models/final_solar_cell_quality_model.keras` — model loaded by the app.
- `models/stage2_class_names.json` — class names in the model's output order.
- `models/` — additional stage 1, stage 2, and fine-tuned model artifacts.
- `data/custom/perovskite_tandem/` — images arranged into `train`, `val`, and `test` splits, with one folder per class.
- `notebooks/01_dataset_exploration.ipynb` — dataset exploration notebook.

The five classes are `functional`, `defect_halide_segregation`, `defect_layer_delamination`, `defect_phase_degradation`, and `defect_pinhole`.

## Preprocessing & Exploratory Data Analysis (EDA)

The notebook explores the source EL dataset and the project’s curated perovskite/tandem dataset before model training. Its EDA includes:

- Counting supported image files and checking folder contents, file types, and image ID ranges.
- Reviewing class annotations, matching annotation files to available images, and checking for filename overlap between groups.
- Displaying sample images and inspecting class counts in the train, validation, and test folders.

The current five-class dataset is organized by split and class under `data/custom/perovskite_tandem/`. TensorFlow loads it from those class folders, resizes images to **224 × 224** pixels, and batches them in groups of **32**. Training data is shuffled with seed `42`; validation and test data are not shuffled.

The model applies preprocessing and augmentation internally: pixel values are rescaled by `1/255`, and training images may receive a random horizontal flip, rotation (up to 5%), or zoom (up to 10%). The Streamlit app resizes uploaded images to 224 × 224 and passes their RGB pixel values to the saved model, which includes the rescaling layer.

For the detailed workflow and reproducibility notes, see [Preprocessing & EDA documentation](docs/preprocessing-and-eda.md).

The model architecture, staged training strategy, and notebook-recorded evaluation are documented in [Feature Extraction & Model Training Analysis](docs/feature-extraction-and-model-training-analysis.md). A Word version is also available as [DOCX](docs/feature-extraction-and-model-training-analysis.docx).

## Requirements

Python 3.9 or newer is recommended. Install the application dependencies in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install streamlit tensorflow numpy pillow
```

## Run the app

Run from the repository root so the relative model paths resolve correctly:

```bash
streamlit run app/app.py
```

Open the local URL printed by Streamlit, then upload a `.jpg`, `.jpeg`, or `.png` EL image. The app converts it to RGB, resizes it to 224 × 224 pixels, and displays the model's top prediction and confidence.

## Model files

The application expects these files at the following paths relative to the repository root:

```text
models/final_solar_cell_quality_model.keras
models/stage2_class_names.json
```

If either file is missing, model loading will fail when the app starts. The class-name list must stay in the same order as the model's output classes.
