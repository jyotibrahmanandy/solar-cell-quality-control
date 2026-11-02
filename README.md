# HelioScan AI — Solar Cell Electroluminescence Quality Control Platform

> Next-Generation Deep Learning Quality Inspection & Physics Diagnostics for Perovskite and Silicon Tandem Photovoltaics.

[![Model Accuracy](https://img.shields.io/badge/Model%20Accuracy-96.00%25-brightgreen.svg)](#)
[![Macro F1](https://img.shields.io/badge/Macro%20F1-0.9603-blue.svg)](#)
[![Latency](https://img.shields.io/badge/Latency-~35ms%20(Metal%20GPU)-orange.svg)](#)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-61DAFB.svg)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](#)

---

## 🌟 Overview

HelioScan AI replaces the legacy Streamlit interface with an industrial-grade **React Web Application** coupled with a high-performance **FastAPI backend** and a context-aware **HelioAI Specialist Chatbot**.

Powered by the fine-tuned **MobileNetV2 Keras model** (`models/final_solar_cell_quality_model.keras`), the platform classifies electroluminescence (EL) imagery across 5 categories with **96.00% accuracy** and a **0.9603 macro F1 score**.

---

## 🚀 Key Features

### 1. Real-Time Deep Quality Inspection
- **Drag-and-Drop Uploader**: Test any custom EL image (.png, .jpg, .jpeg) with live inference.
- **Held-Out Benchmark Presets**: 1-click evaluation of real test wafers for all 5 defect categories:
  - ⚡ **Halide Segregation** (Phase demixing / iodide cluster carrier traps)
  - 💥 **Layer Delamination** (Interfacial debonding between absorber and transport layers)
  - 🌡️ **Phase Degradation** (Photoactive black α-phase decaying to yellow δ-phase / PbI₂)
  - 🕳️ **Pinhole Defect** (Through-thickness voids creating localized low-resistance shunts)
  - ✅ **Functional Cell** (Optimal uniform luminescence, Certified Pass)
- **Interactive Multi-Mode Visualizer**:
  - **Turbo Colormap Anomaly Heatmap**: Highlights localized non-radiative quenching zones.
  - **Edge & Crack Tracing**: Detects interfacial cracks, busbar peeling, and delamination contours.
  - **High-Contrast Inverted EL**: Standard solar manufacturing inspection contrast mode.
  - **Raw EL**: Unfiltered electroluminescence capture.
- **Physical Root Cause & Fab Action Plan**:
  - Detailed physical and chemical failure mechanisms.
  - Expected Power Conversion Efficiency (PCE) loss and Fill Factor (ΔFF) penalty.
  - Immediate fab line corrective remedies (e.g., Cs⁺ stiffening, SAMs, anti-solvent timing).
  - Automated 4-bin robotic wafer routing (Bin A: Premium, Bin B: Laser Repair, Bin C: Re-anneal, Bin D: Scrap).

### 2. HelioAI Specialist Chatbot
- Trained specifically on this **MobileNetV2 model architecture** and perovskite/tandem solar physics.
- **Context-Aware**: Injects current scan metrics (confidence, defect category, severity) into the conversation.
- Available both as a **Full-Screen Tab** and as a **Quick Slide-Over Drawer** accessible anywhere in the app.
- Interactive question chips, markdown formatting, and fab troubleshooting advice.

### 3. Fleet & Batch Wafer Analytics
- Automated telemetry run across production batches.
- Certified yield rate gauge, defect class distribution, and individual wafer traceability logs.

### 4. Future Industrial Scaling Roadmap (2027–2028)
- **Phase 1**: High-Speed Inline Conveyor Line-Scan Integration (120 wafers/min, InGaAs cameras, GigE Vision).
- **Phase 2**: Edge Acceleration on NVIDIA Jetson & TensorRT (Sub-10ms on-device latency).
- **Phase 3**: Perovskite-Silicon Tandem Multi-Junction Inspection (>32% PCE targets, dual-spectral EL).
- **Phase 4**: Autonomous 4-Bin Wafer Sorting Delta Robot & Laser Isolation.
- **Phase 5**: Digital Twin & 25-Year Outdoor Degradation Forecasting.

### 5. Neural Architecture & Held-Out Test Benchmarks
- Staged training comparison: Stage 1 binary (56.17%) vs Stage 2 frozen (83.67%) vs Stage 2 fine-tuned (96.00%).
- Full confusion matrix on 300 held-out test images.

---

## 🛠️ Quick Start

### One-Command Startup
To start both the FastAPI backend and React frontend simultaneously:
```bash
./start_app.sh
```

### Manual Startup

#### 1. Start the FastAPI Backend (Port 8000)
```bash
./.venv/bin/python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
```
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 2. Start the React Frontend (Port 5173)
```bash
cd frontend
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)
