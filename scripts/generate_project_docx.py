import os
from docx import Document
from docx.shared import Inches

def add_heading(doc, text, level=1):
    doc.add_heading(text, level=level)

def add_paragraph(doc, text):
    doc.add_paragraph(text)

def add_image(doc, image_path, width=Inches(6)):
    if os.path.exists(image_path):
        doc.add_picture(image_path, width=width)
    else:
        doc.add_paragraph(f"[Image not found: {image_path}]")

def generate_docx(output_path):
    doc = Document()
    add_heading(doc, "Solar Cell Quality Control – Project Documentation", level=0)
    add_paragraph(doc, "This document provides an overview of the project, including dataset visualizations, model evaluation metrics, backend specifications, and a brief frontend description.")
    
    # Dataset Visualization
    add_heading(doc, "Dataset Visualization", level=1)
    add_paragraph(doc, "The dataset consists of solar cell images labeled for quality assessment. Visual representations include sample images and distribution plots.")
    add_image(doc, os.path.join(os.path.dirname(__file__), "../visualizations/dataset_samples.png"))
    add_image(doc, os.path.join(os.path.dirname(__file__), "../visualizations/label_distribution.png"))
    
    # Model Evaluation Metrics
    add_heading(doc, "Model Evaluation Metrics", level=1)
    add_paragraph(doc, "The model performance is evaluated using metrics such as Accuracy, Precision, Recall, F1‑Score, and ROC‑AUC.")
    add_image(doc, os.path.join(os.path.dirname(__file__), "../visualizations/confusion_matrix.png"))
    add_paragraph(doc, "Detailed metric values can be found in the generated reports under the 'reports' directory.")
    
    # Backend Specification
    add_heading(doc, "Backend Specification", level=1)
    add_paragraph(doc, "The backend is built with FastAPI and provides the following key endpoints:")
    add_paragraph(doc, "- **/api/predict‑sample**: Accepts an image and returns quality prediction.\n- **/api/health**: Health check endpoint.\n- **/api/samples**: Returns a list of sample images.")
    add_paragraph(doc, "It runs on Python 3.11 within a virtual environment and listens on port 8000.")
    
    # Frontend Overview (minimal)
    add_heading(doc, "Frontend Overview (Minimal)", level=1)
    add_paragraph(doc, "The frontend is a Vite‑powered React application that consumes the backend APIs. It provides live inspection of samples and displays model evaluation results.")
    
    doc.save(output_path)

if __name__ == "__main__":
    output_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Solar_Cell_Quality_Control_Documentation.docx"))
    generate_docx(output_file)
    print(f"Documentation generated at {output_file}")
