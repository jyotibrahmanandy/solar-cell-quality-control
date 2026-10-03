import streamlit as st
import tensorflow as tf
import json
import numpy as np
from PIL import Image


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Solar Cell Quality Control",
    page_icon="☀️",
    layout="centered"
)


# ==========================================================
# LOAD MODEL
# ==========================================================

MODEL_PATH = "models/final_solar_cell_quality_model.keras"
CLASS_NAMES_PATH = "models/stage2_class_names.json"

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_NAMES_PATH, "r") as f:
    class_names = json.load(f)


# ==========================================================
# TITLE
# ==========================================================

st.title("☀️ Solar Cell Quality Control")

st.write(
    "Upload a solar cell EL image to detect its quality condition."
)


# ==========================================================
# IMAGE UPLOAD
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload an EL image",
    type=["jpg", "jpeg", "png"]
)


# ==========================================================
# PREDICTION
# ==========================================================

if uploaded_file is not None:

    image = Image.open(uploaded_file).convert("RGB")

    st.image(
        image,
        caption="Uploaded Solar Cell Image",
        use_container_width=True
    )

    # Resize image
    image_resized = image.resize((224, 224))

    # Convert to NumPy array
    image_array = np.array(image_resized)

    # Add batch dimension
    input_image = np.expand_dims(image_array, axis=0)

    # Prediction
    probabilities = model.predict(input_image, verbose=0)[0]

    predicted_index = np.argmax(probabilities)
    predicted_class = class_names[predicted_index]
    confidence = probabilities[predicted_index] * 100


    # ======================================================
    # RESULT
    # ======================================================

    st.subheader("Prediction")

    st.success(
        f"Detected: {predicted_class.replace('defect_', '').replace('_', ' ').title()}"
    )

    st.write(
        f"Confidence: **{confidence:.2f}%**"
    )