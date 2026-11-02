# Feature Extraction & Model Training Analysis

This document explains how the project uses transfer learning to classify solar-cell electroluminescence images, how training proceeds from binary screening to five-class recognition, and what the notebook's recorded evaluation shows. The notebook reports **96.00% accuracy** on its 300-image five-class test split after fine tuning; class-level recall shows that halide segregation and phase degradation remain the main sources of missed defects.

## Feature extraction architecture

The classifier uses **MobileNetV2** initialized with ImageNet weights and configured for 224 × 224 × 3 RGB inputs. The ImageNet classification top is removed (`include_top=False`), leaving a convolutional feature extractor. At this resolution, its final feature map is 7 × 7 × 1,280.

The feature map is reduced with global average pooling to a 1,280-element vector. A dropout layer with rate 0.3 is applied before the task-specific dense output. The notebook places random image augmentation and pixel rescaling ahead of MobileNetV2 as part of the Keras model.

## Training stages

### Stage 1 binary screening

The first model separates `Correct` from `Defective`. MobileNetV2 is frozen, so training updates the new classification head while reusing the pretrained image features. The output layer has one sigmoid unit; training uses Adam at learning rate `0.0001`, binary cross-entropy, and accuracy.

The notebook trains for up to 10 epochs and monitors validation loss. Early stopping uses patience 3 and restores the best weights; model checkpointing saves the best validation-loss model. On the recorded 600-image test set (300 per class), Stage 1 reached **56.17% accuracy**. Defective-class recall was **13.00%**, indicating that this binary checkpoint is not a suitable final defect detector on its own.

### Stage 2 five-class classifier

For the project-specific task, the notebook keeps the MobileNetV2 feature extractor frozen and replaces the output with a five-unit softmax head. It trains with sparse categorical cross-entropy and Adam at `0.0001`, for up to 20 epochs. Early stopping and checkpointing monitor validation loss, with patience 5 and best-weight restoration.

The recorded Stage 2 test report shows **83.67% accuracy** over 300 images, with 60 examples per class. Phase degradation recall was **50.00%**, the lowest of the five classes. This error analysis motivated the subsequent fine-tuning step.

### Fine tuning

The notebook then unfreezes the last 20 MobileNetV2 layers while leaving earlier layers frozen. Batch normalization layers remain frozen. It recompiles the model using a lower Adam learning rate of `0.00001` and continues training for up to 15 epochs. Early stopping and checkpointing again monitor validation loss, use patience 5, and restore/save the best weights.

The fine-tuned model is saved as `models/solar_cell_mobilenetv2_stage2_finetuned.keras`. The final model used by the app is saved as `models/final_solar_cell_quality_model.keras`, alongside the matching output order in `models/stage2_class_names.json`.

## Recorded test evaluation

The notebook's fine-tuned Stage 2 classification report gives the following results on the 300-image test split:

| Class | Precision | Recall | F1 score | Support |
| --- | ---: | ---: | ---: | ---: |
| Halide segregation | 0.8696 | 1.0000 | 0.9302 | 60 |
| Layer delamination | 1.0000 | 0.9500 | 0.9744 | 60 |
| Phase degradation | 1.0000 | 0.8833 | 0.9381 | 60 |
| Pinhole | 1.0000 | 1.0000 | 1.0000 | 60 |
| Functional | 0.9508 | 0.9667 | 0.9587 | 60 |
| **Overall accuracy** |  |  | **0.9600** | **300** |

The confusion matrix records seven phase-degradation images predicted as halide segregation, three delamination images predicted as functional, and two functional images predicted as halide segregation. No pinhole examples were misclassified in this split. Despite the high aggregate score, the results show that class-specific errors remain and should be considered when evaluating the classifier for inspection use.

## Interpretation and reproducibility

The notebook results show a substantial improvement from the frozen five-class model to the fine-tuned model on this test split. Fine tuning lets higher-level pretrained features adapt to the solar-cell image domain while the low learning rate limits large changes to the pretrained weights. This comparison is observational; it does not establish performance on images from other sources or production conditions.

To reproduce training, use the notebook's configured 224 × 224 inputs and `data/custom/perovskite_tandem/{train,val,test}` folders, preserving the class directory names. The notebook stores training histories, confusion matrices, and classification reports in cell outputs. Some notebook cells use local absolute paths and may need path updates on another machine. The Streamlit app loads the final model and class-name JSON, so keep these artifacts paired.
