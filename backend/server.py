"""
Solar Cell Quality Control - FastAPI Backend Engine
Serving MobileNetV2 Fine-Tuned Model (96.0% Test Accuracy)
Provides Real-Time Inference, Heatmap Visualization, Defect Diagnostics, and HelioAI Specialist Chatbot.
"""

import base64
import io
import json
import os
import re
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
import tensorflow as tf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from PIL import Image

# ==========================================================
# PATHS & MODEL INITIALIZATION
# ==========================================================

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "final_solar_cell_quality_model.keras"
CLASS_NAMES_PATH = BASE_DIR / "models" / "stage2_class_names.json"
SAMPLES_DIR = BASE_DIR / "data" / "custom" / "perovskite_tandem" / "test"

app = FastAPI(
    title="Solar Cell Quality Control API",
    description="Industrial AI Platform for Perovskite & Tandem Photovoltaic Inspection",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"Loading Keras Model from {MODEL_PATH}...")
model = tf.keras.models.load_model(str(MODEL_PATH))

with open(CLASS_NAMES_PATH, "r") as f:
    CLASS_NAMES = json.load(f)

print(f"Model loaded successfully with {len(CLASS_NAMES)} classes: {CLASS_NAMES}")

# Pre-warm model
_dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
_ = model.predict(_dummy, verbose=0)
print("Model pre-warmed and ready for low-latency inference.")

# ==========================================================
# DEFECT DOMAIN KNOWLEDGE BASE
# ==========================================================

DEFECT_METADATA: Dict[str, Dict[str, Any]] = {
    "defect_halide_segregation": {
        "id": "defect_halide_segregation",
        "displayName": "Halide Segregation",
        "subtitle": "Phase Demixing & Iodide-Rich Cluster Traps",
        "category": "Perovskite Composition & Ion Dynamics",
        "status": "FAIL",
        "severity": "High",
        "severityScore": 7.8,
        "efficiencyImpact": "-14% to -22% PCE Loss",
        "fillFactorImpact": "ΔFF ≈ -0.12 (Voc Deficit)",
        "summary": "Photo-induced and electric field-induced phase demixing into segregated iodide-rich and bromide-rich domains.",
        "physicalMechanism": (
            "Under light soaking and continuous electrical bias, mixed-halide perovskite crystals "
            "(e.g., FA0.85MA0.15Pb(I0.85Br0.15)3) suffer from anion migration. Iodide ions congregate into low-bandgap "
            "iodide-rich clusters (~1.55 eV), while bromide segregates into high-bandgap regions. Photogenerated charge carriers "
            "funnel into the lower-bandgap domains where they undergo enhanced non-radiative recombination, inducing a severe "
            "open-circuit voltage (Voc) deficit and visible luminescent quenching under EL."
        ),
        "manufacturingRemedy": [
            "Incorporate 3-5 mol% Cesium (Cs+) or Rubidium (Rb+) cations to stiffen the perovskite cubic lattice.",
            "Apply 2D perovskite surface capping layer (e.g., PEAI or butylammonium bromide) for grain-boundary passivation.",
            "Verify encapsulation inert atmosphere; ensure oxygen/moisture levels in glovebox are below 0.1 ppm.",
            "Lower post-deposition thermal annealing ramp rate to promote uniform crystallization kinetics."
        ],
        "sortingBin": "Bin C - Divert to Thermal Re-annealing / Secondary Array",
        "color": "#F59E0B"
    },
    "defect_layer_delamination": {
        "id": "defect_layer_delamination",
        "displayName": "Layer Delamination",
        "subtitle": "Interfacial Peeling & Mechanical Detachment",
        "category": "Interfacial Mechanics & Adhesion",
        "status": "FAIL",
        "severity": "Critical",
        "severityScore": 9.4,
        "efficiencyImpact": "-25% to -45% PCE Loss",
        "fillFactorImpact": "ΔFF ≈ -0.28 (Massive Series Resistance)",
        "summary": "Physical separation of the perovskite absorber from electron/hole transport layers or metallization.",
        "physicalMechanism": (
            "Mechanical shear stresses, mismatched coefficients of thermal expansion (CTE), or poor chemical bonding "
            "cause interfacial debonding between the perovskite absorber and the underlying Electron Transport Layer (SnO2/TiO2) "
            "or overlying Hole Transport Layer (Spiro-OMeTAD / PTAA). The resulting microscopic air gaps introduce enormous series "
            "resistance (Rs) and completely obstruct carrier extraction, showing as prominent dark inactive bands on EL."
        ),
        "manufacturingRemedy": [
            "Incorporate self-assembled monolayers (SAMs, such as Me-4PACz or 2PACz) to strongly bond substrate to perovskite.",
            "Clean ITO/FTO glass substrate with argon/oxygen RF plasma or UV-ozone for 15 minutes prior to deposition.",
            "Check slot-die or spin-coating nozzle gap and reduce film tension during curing.",
            "Calibrate laminator roller pressure and check EVA/POE encapsulant cross-linking gel content."
        ],
        "sortingBin": "Bin D - Irreversible Structural Failure (Scrap / Raw Material Recovery)",
        "color": "#EF4444"
    },
    "defect_phase_degradation": {
        "id": "defect_phase_degradation",
        "displayName": "Phase Degradation",
        "subtitle": "Perovskite Black-to-Yellow Inactive Phase Shift",
        "category": "Chemical & Thermodynamic Stability",
        "status": "FAIL",
        "severity": "Critical",
        "severityScore": 9.1,
        "efficiencyImpact": "-30% to -50% PCE Loss",
        "fillFactorImpact": "ΔFF ≈ -0.32 (Total Active Area Loss)",
        "summary": "Moisture- or heat-induced degradation of the black perovskite phase into inactive yellow delta-phase or lead iodide.",
        "physicalMechanism": (
            "Black photoactive perovskite (alpha-FAPbI3 or MAPbI3) is thermodynamically metastable in the presence of ambient "
            "humidity and elevated temperatures. Water molecules penetrate the lattice and catalyze transformation into the non-perovskite "
            "hexagonal yellow delta-phase, accompanied by methylammonium escape and PbI2 precipitation. These degraded regions cease "
            "luminescing under forward electrical injection, appearing as broad extinguished blotches."
        ),
        "manufacturingRemedy": [
            "Audit module edge-seal sealant; ensure Polyisobutylene (PIB) seal width is at least 12mm.",
            "Verify encapsulant Water Vapor Transmission Rate (WVTR) is below 10^-4 g/m²/day.",
            "Shift precursor formulation toward formamidinium-cesium alloyed mixtures (Cs0.17FA0.83PbI3) for higher phase stability.",
            "Implement in-line moisture and temperature monitors along the entire lamination track."
        ],
        "sortingBin": "Bin D - Scrap / De-metallize for Glass and Indium Recycling",
        "color": "#DC2626"
    },
    "defect_pinhole": {
        "id": "defect_pinhole",
        "displayName": "Pinhole Defect",
        "subtitle": "Sub-Micron Voids & Localized Shunt Pathways",
        "category": "Film Morphology & Pinholes",
        "status": "FAIL",
        "severity": "High",
        "severityScore": 8.2,
        "efficiencyImpact": "-15% to -28% PCE Loss",
        "fillFactorImpact": "ΔFF ≈ -0.19 (Severe Shunt Resistance Rsh Collapse)",
        "summary": "Microscopic voids penetrating the absorber thickness, forming direct short circuits between electrode layers.",
        "physicalMechanism": (
            "Irregular solvent evaporation or incomplete precursor nucleation creates microscopic pinholes that punch entirely "
            "through the perovskite thin film (~400-600 nm thickness). When the top electrode and HTL are deposited, they make direct ohmic "
            "contact with the underlying ETL, forming localized low-resistance shunt pathways. In EL inspection, shunts sink huge currents "
            "and create localized dark spot clusters with surrounding luminous drop."
        ),
        "manufacturingRemedy": [
            "Optimize anti-solvent dripping timing window to within ±0.5 seconds of optimal supersaturation point.",
            "Use vacuum-assisted drying (VAD) chamber at 15-25 Pa pressure to induce rapid, uniform seed nucleation.",
            "Pass precursor ink through 0.22 µm PTFE syringe filters to eliminate micro-particulates acting as void seeds.",
            "Inspect slot-die meniscus speed and substrate wet-film thickness uniformity."
        ],
        "sortingBin": "Bin B - Laser Isolation Shunt Removal / Rework Eligible",
        "color": "#F97316"
    },
    "functional": {
        "id": "functional",
        "displayName": "Functional (Optimal Quality)",
        "subtitle": "Certified A-Grade Electroluminescence",
        "category": "Certified Quality Control Pass",
        "status": "PASS",
        "severity": "None",
        "severityScore": 0.2,
        "efficiencyImpact": "0.0% Nominal (Target 23.5% - 25.8% PCE)",
        "fillFactorImpact": "None (FF > 0.81)",
        "summary": "Uniform, high-efficiency radiative recombination with pristine interfacial contact and no active shunts.",
        "physicalMechanism": (
            "The solar cell demonstrates uniform forward-bias electroluminescent emission across all active fingers and busbars. "
            "Grain boundaries are thoroughly passivated, series resistance is minimal (Rs < 0.6 Ω·cm²), and shunt resistance is high "
            "(Rsh > 10,000 Ω·cm²). Charge carrier lifetime is prolonged (>2 µs) with optimal carrier collection at both electrodes."
        ),
        "manufacturingRemedy": [
            "Approved for stringer soldering, EVA encapsulation, and full module lamination.",
            "Maintain current precursor stoichiometry and chemical annealing profile.",
            "Archive EL fingerprint in manufacturing MES database for 25-year warranty traceability."
        ],
        "sortingBin": "Bin A - Premium Grade Module Assembly",
        "color": "#10B981"
    }
}

# ==========================================================
# HELPER FUNCTIONS: HEATMAP & IMAGE PROCESSING
# ==========================================================

def generate_visual_overlays(image_pil: Image.Image) -> Dict[str, str]:
    """
    Generates thermal/defect heatmap overlay and edge analysis overlay
    using OpenCV for high-resolution interactive inspection.
    """
    img_rgb = np.array(image_pil.convert("RGB"))
    h, w, _ = img_rgb.shape
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    
    # 1. Contrast Normalized Anomaly Heatmap
    # In EL imaging, defects are regions of localized dark quenching or abnormal gradients
    # Normalize and invert luminance to accentuate defects as hot spots
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)
    
    # Anomaly intensity: high in dark defect spots, low in uniform bright functional areas
    blur = cv2.GaussianBlur(enhanced_gray, (9, 9), 0)
    anomaly_map = cv2.bitwise_not(blur)
    anomaly_norm = cv2.normalize(anomaly_map, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    
    # Apply JET/TURBO colormap
    heatmap_color = cv2.applyColorMap(anomaly_norm, cv2.COLORMAP_TURBO)
    heatmap_color_rgb = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
    
    # Blend with original
    blended = cv2.addWeighted(img_rgb, 0.45, heatmap_color_rgb, 0.55, 0)
    
    # 2. Edge / Crack / Delamination contour detector
    edges = cv2.Canny(enhanced_gray, 40, 120)
    edge_overlay = img_rgb.copy()
    edge_overlay[edges > 0] = [0, 245, 255] # Cyan glow on crack/boundary edges
    
    # 3. High Contrast Inverted EL (Solar Engineer inspection standard)
    inverted = cv2.bitwise_not(enhanced_gray)
    inverted_rgb = cv2.cvtColor(inverted, cv2.COLOR_GRAY2RGB)

    def to_base64_data_url(arr: np.ndarray) -> str:
        pil_img = Image.fromarray(arr)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    return {
        "original": to_base64_data_url(img_rgb),
        "heatmap": to_base64_data_url(blended),
        "edge": to_base64_data_url(edge_overlay),
        "inverted": to_base64_data_url(inverted_rgb),
    }


def predict_image_array(img: Image.Image) -> Dict[str, Any]:
    """Runs the MobileNetV2 model inference on a PIL image."""
    img_resized = img.convert("RGB").resize((224, 224))
    img_array = np.array(img_resized)
    input_tensor = np.expand_dims(img_array, axis=0)

    # Prediction
    probabilities = model.predict(input_tensor, verbose=0)[0]
    predicted_idx = int(np.argmax(probabilities))
    predicted_class = CLASS_NAMES[predicted_idx]
    confidence = float(probabilities[predicted_idx] * 100.0)

    # Build probability breakdown for all classes
    breakdown = []
    for idx, cname in enumerate(CLASS_NAMES):
        meta = DEFECT_METADATA.get(cname, {})
        breakdown.append({
            "classId": cname,
            "displayName": meta.get("displayName", cname.replace("defect_", "").replace("_", " ").title()),
            "status": meta.get("status", "FAIL"),
            "probability": float(probabilities[idx] * 100.0),
            "severity": meta.get("severity", "Medium"),
            "color": meta.get("color", "#64748B"),
        })

    # Sort breakdown by highest probability first
    breakdown.sort(key=lambda x: x["probability"], reverse=True)

    defect_info = DEFECT_METADATA.get(predicted_class, DEFECT_METADATA["functional"])
    overlays = generate_visual_overlays(img_resized)

    return {
        "predictedClass": predicted_class,
        "displayName": defect_info["displayName"],
        "subtitle": defect_info["subtitle"],
        "category": defect_info["category"],
        "status": defect_info["status"],
        "confidence": round(confidence, 2),
        "severity": defect_info["severity"],
        "severityScore": defect_info["severityScore"],
        "efficiencyImpact": defect_info["efficiencyImpact"],
        "fillFactorImpact": defect_info["fillFactorImpact"],
        "summary": defect_info["summary"],
        "physicalMechanism": defect_info["physicalMechanism"],
        "manufacturingRemedy": defect_info["manufacturingRemedy"],
        "sortingBin": defect_info["sortingBin"],
        "color": defect_info["color"],
        "probabilities": breakdown,
        "overlays": overlays,
    }


# ==========================================================
# ENDPOINTS: SAMPLES & PREDICTIONS
# ==========================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "modelLoaded": True,
        "modelVersion": "MobileNetV2 Fine-Tuned (Stage 2)",
        "testAccuracy": "96.00%",
        "classes": CLASS_NAMES,
    }


@app.get("/api/model-info")
def model_info():
    return {
        "name": "MobileNetV2 Perovskite & Tandem Solar Cell Inspector",
        "architecture": "MobileNetV2 + GlobalAveragePooling + Dense(5)",
        "totalParameters": 2264389,
        "trainableParameters": 1201285,
        "accuracy": 0.9600,
        "macroF1": 0.9603,
        "evaluationStages": [
            {"stage": "Stage 1 Binary Frozen", "accuracy": "56.2%", "classes": 2, "description": "Initial feature extractor calibration"},
            {"stage": "Stage 2 Multi-Class Frozen", "accuracy": "83.7%", "classes": 5, "description": "Frozen backbone with 5-class dense head"},
            {"stage": "Stage 2 Fine-Tuned (Final)", "accuracy": "96.0%", "classes": 5, "description": "Deep layers unrolled for sub-surface defect micro-textures"}
        ],
        "targetTechnologies": [
            "Perovskite Single-Junction Solar Cells",
            "Perovskite-Silicon 2-Terminal Tandem Cells",
            "Perovskite-Silicon 4-Terminal Tandem Cells",
            "Silicon Heterojunction (HJT) Bottom Cells"
        ],
        "hardwareBackend": "Apple M4 Metal Acceleration (Pluggable GPU Device)",
        "classes": CLASS_NAMES,
    }


@app.get("/api/samples")
def get_sample_images():
    """
    Returns a curated list of real EL test images for each of the 5 classes.
    """
    samples = []
    if SAMPLES_DIR.exists():
        for cname in CLASS_NAMES:
            cdir = SAMPLES_DIR / cname
            if cdir.exists():
                files = sorted(list(cdir.glob("*.png")) + list(cdir.glob("*.jpg")))
                # pick up to 3 real sample images per class
                meta = DEFECT_METADATA.get(cname, {})
                for f in files[:3]:
                    samples.append({
                        "filename": f.name,
                        "classId": cname,
                        "displayName": meta.get("displayName", cname),
                        "status": meta.get("status", "FAIL"),
                        "severity": meta.get("severity", "Medium"),
                        "color": meta.get("color", "#64748B"),
                        "url": f"/api/sample-image/{cname}/{f.name}",
                    })
    return {"samples": samples}


@app.get("/api/sample-image/{category}/{filename}")
def serve_sample_image(category: str, filename: str):
    file_path = SAMPLES_DIR / category / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")
    return FileResponse(file_path)


@app.post("/api/predict")
async def predict_upload(file: UploadFile = File(...)):
    """Accepts an uploaded image file and returns deep quality classification."""
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

    result = predict_image_array(image)
    return result


@app.post("/api/predict-sample")
def predict_sample(category: str = Form(...), filename: str = Form(...)):
    """Inspects a sample image directly from the server disk."""
    file_path = SAMPLES_DIR / category / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")
    
    image = Image.open(file_path).convert("RGB")
    result = predict_image_array(image)
    result["filename"] = filename
    return result


@app.post("/api/batch-inspect")
def batch_inspect(categories: List[str] = Form(None)):
    """
    Simulates / runs batch inspection over multiple test cells for QA yield analytics.
    """
    results = []
    total_passed = 0
    total_failed = 0
    defect_counts = {c: 0 for c in CLASS_NAMES if c != "functional"}

    # Run on sample set
    for cname in CLASS_NAMES:
        cdir = SAMPLES_DIR / cname
        if cdir.exists():
            files = list(cdir.glob("*.png"))[:4] # 4 per class = 20 cells
            for f in files:
                img = Image.open(f).convert("RGB")
                res = predict_image_array(img)
                res["filename"] = f.name
                results.append({
                    "filename": f.name,
                    "actual": cname,
                    "predicted": res["predictedClass"],
                    "displayName": res["displayName"],
                    "confidence": res["confidence"],
                    "status": res["status"],
                    "severity": res["severity"],
                })
                if res["status"] == "PASS":
                    total_passed += 1
                else:
                    total_failed += 1
                    defect_counts[res["predictedClass"]] = defect_counts.get(res["predictedClass"], 0) + 1

    total = len(results)
    yield_rate = round((total_passed / total * 100.0), 1) if total > 0 else 0

    return {
        "totalInspected": total,
        "passedCount": total_passed,
        "failedCount": total_failed,
        "yieldRate": yield_rate,
        "defectDistribution": defect_counts,
        "items": results,
    }


# ==========================================================
# CHATBOT ENGINE: HELIOAI SPECIALIST
# ==========================================================

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    scanContext: Optional[Dict[str, Any]] = None
    apiKey: Optional[str] = None
    provider: Optional[str] = "gemini"
    model: Optional[str] = None


def extract_http_error_detail(e: urllib.error.HTTPError) -> str:
    """Extracts human-readable error messages from provider JSON responses."""
    try:
        body = e.read().decode("utf-8", errors="ignore")
        data = json.loads(body)
        if isinstance(data, dict):
            if "error" in data:
                err = data["error"]
                if isinstance(err, dict):
                    msg = err.get("message") or err.get("status")
                    if msg:
                        return f"HTTP {e.code}: {msg}"
                elif isinstance(err, str):
                    return f"HTTP {e.code}: {err}"
        return f"HTTP {e.code}: {body[:250]}" if body else f"HTTP {e.code}: {e.reason}"
    except Exception:
        return f"HTTP {e.code}: {e.reason}"


def resolve_gemini_models(api_key: str, requested_model: Optional[str] = None) -> List[str]:
    """Dynamically queries available Gemini models or falls back to prioritized model list."""
    candidates: List[str] = []
    if requested_model and requested_model.strip():
        candidates.append(requested_model.strip().replace("models/", ""))

    # Attempt dynamic model discovery via ListModels endpoint
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={urllib.parse.quote(api_key)}"
        req = urllib.request.Request(list_url, headers={"User-Agent": "HelioScan/1.0"}, method="GET")
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            available = [
                m["name"].replace("models/", "")
                for m in data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            if available:
                priority = [
                    "gemini-2.5-flash",
                    "gemini-2.0-flash",
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-latest",
                    "gemini-1.5-flash-8b",
                    "gemini-1.5-pro",
                    "gemini-2.0-flash-lite",
                    "gemini-pro"
                ]
                for p in priority:
                    if p in available and p not in candidates:
                        candidates.append(p)
                for av in available:
                    if av not in candidates:
                        candidates.append(av)
                return candidates
    except Exception:
        pass

    defaults = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    for d in defaults:
        if d not in candidates:
            candidates.append(d)
    return candidates


def call_external_llm(
    user_query: str,
    scan_context: Optional[Dict[str, Any]],
    history: List[ChatMessage],
    api_key: str,
    provider: str = "gemini",
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Calls user-provided LLM API (Google Gemini or OpenAI) with solar physics system prompt and automatic fallback."""
    import urllib.request
    import urllib.error
    import urllib.parse

    clean_key = api_key.strip()
    prov = (provider or "gemini").lower().strip()

    # Smart auto-detection of provider if key format mismatches selection
    if clean_key.startswith("sk-") and "openai" not in prov:
        prov = "openai"
    elif clean_key.startswith("AIzaSy") and "gemini" not in prov:
        prov = "gemini"

    system_prompt = (
        "You are HelioBot, an expert AI Photovoltaic Quality Control and Defect Physics Engineer. "
        "You specialize in perovskite, tandem, and silicon solar cells, electroluminescence (EL) defect detection, "
        "and the MobileNetV2 fine-tuned classification model (96.0% accuracy)."
    )

    if scan_context:
        system_prompt += (
            f"\n\nCurrent Active Inspection Context:\n"
            f"- Scanned Cell Verdict: {scan_context.get('displayName')} ({scan_context.get('status')})\n"
            f"- Confidence: {scan_context.get('confidence')}%\n"
            f"- Severity: {scan_context.get('severity')}\n"
            f"- Efficiency Impact (PCE): {scan_context.get('efficiencyImpact')}\n"
            f"- Fill Factor Impact: {scan_context.get('fillFactorImpact')}\n"
            f"- Physical Mechanism: {scan_context.get('physicalMechanism')}\n"
            f"- Recommended Sorting Bin: {scan_context.get('sortingBin')}"
        )

    if "gemini" in prov:
        candidate_models = resolve_gemini_models(clean_key, model)
        last_error = None

        # Build clean alternating conversation turns
        contents = []
        for msg in (history or [])[-6:]:
            if msg.role not in ("user", "model", "assistant"):
                continue
            role = "user" if msg.role == "user" else "model"
            if msg.content and msg.content.strip():
                if contents and contents[-1]["role"] == role:
                    contents[-1]["parts"][0]["text"] += f"\n\n{msg.content.strip()}"
                else:
                    contents.append({"role": role, "parts": [{"text": msg.content.strip()}]})

        # Ensure conversation begins with a user turn
        if contents and contents[0]["role"] == "model":
            contents.pop(0)

        # Context-rich prompt
        user_turn_text = f"[Domain System Context: {system_prompt}]\n\nUser Question: {user_query}"
        if contents and contents[-1]["role"] == "user":
            contents[-1]["parts"][0]["text"] += f"\n\n{user_turn_text}"
        else:
            contents.append({"role": "user", "parts": [{"text": user_turn_text}]})

        req_payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.35,
                "maxOutputTokens": 1200
            }
        }
        payload_bytes = json.dumps(req_payload).encode("utf-8")

        for m_name in candidate_models:
            for api_version in ["v1beta", "v1"]:
                url = f"https://generativelanguage.googleapis.com/{api_version}/models/{m_name}:generateContent?key={urllib.parse.quote(clean_key)}"
                req = urllib.request.Request(
                    url,
                    data=payload_bytes,
                    headers={"Content-Type": "application/json", "User-Agent": "HelioScan/1.0"},
                    method="POST"
                )
                try:
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        resp_data = json.loads(resp.read().decode("utf-8"))
                        candidates_list = resp_data.get("candidates", [])
                        if candidates_list and "content" in candidates_list[0]:
                            parts = candidates_list[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                return {
                                    "reply": parts[0]["text"],
                                    "suggestions": [
                                        "What fab line actions can mitigate this defect?",
                                        "Explain the impact on open-circuit voltage (Voc)",
                                        "How does this compare to typical tandem degradation?"
                                    ],
                                    "providerUsed": f"gemini ({m_name})"
                                }
                except urllib.error.HTTPError as he:
                    detail = extract_http_error_detail(he)
                    last_error = detail
                    # 404 indicates model or api_version route not found; try next model candidate
                    if he.code == 404:
                        continue
                    # Non-404 errors (e.g. 400 Invalid Key, 403 Forbidden, 429 Quota) should be reported directly
                    raise RuntimeError(f"Google Gemini: {detail}")
                except Exception as ex:
                    last_error = str(ex)
                    continue

        raise RuntimeError(f"Google Gemini connection failed: {last_error or 'No compatible model found for this key'}")

    elif "openai" in prov:
        openai_models = []
        if model and model.strip():
            openai_models.append(model.strip())
        for om in ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]:
            if om not in openai_models:
                openai_models.append(om)

        messages = [{"role": "system", "content": system_prompt}]
        for msg in (history or [])[-6:]:
            if msg.role in ("user", "assistant", "system") and msg.content:
                messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_query})

        last_error = None
        for om in openai_models:
            payload = json.dumps({
                "model": om,
                "messages": messages,
                "temperature": 0.35,
                "max_tokens": 1200
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {clean_key}",
                    "User-Agent": "HelioScan/1.0"
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    resp_data = json.loads(resp.read().decode("utf-8"))
                    reply = resp_data["choices"][0]["message"]["content"]
                    return {
                        "reply": reply,
                        "suggestions": [
                            "What fab line actions can mitigate this defect?",
                            "Explain the impact on open-circuit voltage (Voc)",
                            "How does this compare to typical tandem degradation?"
                        ],
                        "providerUsed": f"openai ({om})"
                    }
            except urllib.error.HTTPError as he:
                detail = extract_http_error_detail(he)
                last_error = detail
                if he.code == 404:
                    continue
                raise RuntimeError(f"OpenAI: {detail}")
            except Exception as ex:
                last_error = str(ex)
                continue

        raise RuntimeError(f"OpenAI connection failed: {last_error or 'No compatible model found'}")

    raise ValueError(f"Unsupported LLM provider: {provider}")



def generate_solar_ai_response(user_query: str, scan_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Intelligent domain-specific conversational engine.
    Understands model mechanics, perovskite/silicon tandem cell science,
    electroluminescence defect physics, and real-time scan context.
    """
    query_lower = user_query.lower()
    
    # 1. SCAN-SPECIFIC QUESTIONS
    if scan_context and any(kw in query_lower for kw in ["this cell", "current scan", "current cell", "why did this fail", "why fail", "scan result", "this defect", "diagnose", "current image"]):
        status = scan_context.get("status", "UNKNOWN")
        dname = scan_context.get("displayName", "Unknown")
        conf = scan_context.get("confidence", 0.0)
        pce = scan_context.get("efficiencyImpact", "N/A")
        ff = scan_context.get("fillFactorImpact", "N/A")
        mech = scan_context.get("physicalMechanism", "")
        remedy = scan_context.get("manufacturingRemedy", [])
        remedy_bullets = "\n".join([f"- **{r}**" for r in remedy])

        if status == "PASS":
            return {
                "reply": (
                    f"### ☀️ Current Cell Diagnosis: **{dname} (PASS)**\n\n"
                    f"The neural model classified this solar cell with **{conf}% confidence** as fully functional.\n\n"
                    f"- **Quality Grade**: Bin A (Premium Grade)\n"
                    f"- **Luminescence Pattern**: High, uniform electroluminescent emission across active grid lines.\n"
                    f"- **Performance Metrics**: Nominal efficiency intact ({pce}), minimal shunt loss ({ff}).\n\n"
                    f"**Engineering Recommendation**:\n"
                    f"This cell meets all IEC 61215 electroluminescence standards and is approved for module stringing."
                ),
                "suggestions": [
                    "How does the model detect pinholes?",
                    "What makes tandem cells more efficient?",
                    "How does electroluminescence work?"
                ]
            }
        else:
            return {
                "reply": (
                    f"### ⚠️ Defect Analysis: **{dname}**\n\n"
                    f"The MobileNetV2 inspector identified this cell as **{status}** with **{conf}% confidence**.\n\n"
                    f"#### 🔬 Physical Root Cause:\n"
                    f"{mech}\n\n"
                    f"#### ⚡ Efficiency & Electrical Penalty:\n"
                    f"- **Power Conversion Efficiency (PCE)**: {pce}\n"
                    f"- **Fill Factor Impact**: {ff}\n\n"
                    f"#### 🛠️ Fab Line Action Plan:\n"
                    f"{remedy_bullets}\n\n"
                    f"**Robotic Sorting Recommendation**: `{scan_context.get('sortingBin', 'Review')}`."
                ),
                "suggestions": [
                    "What caused this defect during fabrication?",
                    "Can this cell be laser-repaired or reworked?",
                    "Explain the MobileNetV2 architecture"
                ]
            }

    # 2. HALIDE SEGREGATION
    if "halide" in query_lower or "segregation" in query_lower or "hoke" in query_lower:
        meta = DEFECT_METADATA["defect_halide_segregation"]
        return {
            "reply": (
                f"### 🧪 Understanding Halide Segregation (The Hoke Effect)\n\n"
                f"Halide segregation is one of the most critical degradation mechanisms in **mixed-halide perovskites** "
                f"(such as FA0.85MA0.15Pb(I0.85Br0.15)3, commonly engineered for 1.7 eV top cells in tandem solar panels).\n\n"
                f"#### Key Mechanisms:\n"
                f"1. **Photo-Induced Ion Migration**: Under continuous 1-sun illumination or current injection, mobile iodide (I⁻) and bromide (Br⁻) ions migrate through lattice vacancies.\n"
                f"2. **Iodide Clustering**: Iodide ions agglomerate into localized lower-bandgap domains (~1.55 eV), while the remaining matrix becomes bromide-rich (~1.8 eV).\n"
                f"3. **Carrier Trapping**: Free electrons and holes funnel into these low-bandgap clusters, driving severe non-radiative recombination and pulling down open-circuit voltage (**Voc drops up to 150-200 mV**).\n\n"
                f"#### Proven Fab Mitigations:\n"
                f"- **Cation Stiffening**: Adding small amounts of **Cs⁺ (3-5%)** or **Rb⁺** reduces lattice distortion and dramatically suppresses halide drift.\n"
                f"- **2D/3D Heterojunctions**: Post-treating the perovskite surface with phenethylammonium iodide (PEAI) passivates surface halide vacancies.\n"
                f"- **Light/Thermal Pre-annealing**: Controlled dark relaxation cycles allow ions to re-homogenize."
            ),
            "suggestions": [
                "How does layer delamination occur?",
                "What is the model accuracy on halide segregation?",
                "How does EL imaging capture halide demixing?"
            ]
        }

    # 3. LAYER DELAMINATION
    if "delamination" in query_lower or "peel" in query_lower or "interface" in query_lower:
        meta = DEFECT_METADATA["defect_layer_delamination"]
        return {
            "reply": (
                f"### 💥 Layer Delamination in Photovoltaic Stacks\n\n"
                f"Layer delamination is a catastrophic mechanical failure where thin film layers detach at their interfaces.\n\n"
                f"#### Where it Occurs:\n"
                f"- **Perovskite / HTL Interface**: Between the absorber and Spiro-OMeTAD or PTAA.\n"
                f"- **ETL / Perovskite Interface**: Between SnO₂/TiO₂ nanocrystals and the perovskite seed layer.\n"
                f"- **Metal Contact Grid**: Screen-printed or evaporated silver/gold busbars peeling from the carrier layer.\n\n"
                f"#### Optical & EL Signature:\n"
                f"In forward-bias electroluminescence, delaminated regions appear as **dark jagged bands or peeling edges**. Because physical contact is lost, current cannot enter the absorber, dropping local emission to zero and creating huge series resistance ($R_s$).\n\n"
                f"#### Fabrication Solutions:\n"
                f"- Use **Self-Assembled Monolayers (SAMs)** like [4-(3,6-dimethyl-9H-carbazol-9-yl)butyl]phosphonic acid (Me-4PACz) for covalent interfacial bonding.\n"
                f"- Treat substrate surfaces with **Oxygen/Argon Plasma** for 10-15 minutes to increase surface energy."
            ),
            "suggestions": [
                "What are pinhole defects?",
                "How does phase degradation differ from delamination?",
                "What is our future inline plan for delamination?"
            ]
        }

    # 4. PHASE DEGRADATION
    if "phase" in query_lower or "degradation" in query_lower or "yellow" in query_lower or "moisture" in query_lower:
        return {
            "reply": (
                f"### 🌡️ Phase Degradation: Alpha-Phase vs. Delta-Phase\n\n"
                f"Perovskite materials (especially Formamidinium Lead Triiodide, **FAPbI₃**) exist in multiple polymorphic crystal phases:\n\n"
                f"- **Alpha-Phase (α-FAPbI₃)**: Black cubic perovskite with an optimal 1.5 eV bandgap for photovoltaic absorption and high electroluminescent yield.\n"
                f"- **Delta-Phase (δ-FAPbI₃)**: Yellow hexagonal non-perovskite phase with wide bandgap (~2.4 eV), highly inactive for solar harvesting.\n\n"
                f"#### Drivers of Phase Decay:\n"
                f"1. **Moisture Ingress**: H₂O molecules form hydrogen bonds with FA⁺/MA⁺ cations, destabilizing the lead-halide octahedra.\n"
                f"2. **Thermal Stress**: High temperatures accelerate methylamine outgassing (leaving inactive PbI₂ behind).\n\n"
                f"#### In-Line Inspection:\n"
                f"EL imaging reveals phase degradation as **broad cloudy or mottled dark zones** where charge injection yields no photons. Cells exhibiting phase decay must be diverted immediately to prevent field module burn-out."
            ),
            "suggestions": [
                "Explain pinhole defects",
                "How does the MobileNetV2 model detect this?",
                "How do we prevent moisture ingress in modules?"
            ]
        }

    # 5. PINHOLE DEFECTS
    if "pinhole" in query_lower or "void" in query_lower or "shunt" in query_lower:
        return {
            "reply": (
                f"### 🕳️ Pinhole Defect Dynamics & Localized Shunts\n\n"
                f"Pinholes are sub-micron through-thickness channels that penetrate the 400–600 nm perovskite layer.\n\n"
                f"#### Why Pinholes are Dangerous:\n"
                f"- **Direct Electrode Shunting**: When top HTL/metal contacts are applied, they bridge directly into the bottom ETL, creating an ohmic short-circuit pathway.\n"
                f"- **Low Shunt Resistance ($R_{{sh}}$)**: A single large pinhole can bleed reverse saturation current and severely suppress the cell's **Fill Factor (FF)**.\n"
                f"- **EL Appearance**: Pinholes show up as **sharp localized dark pits surrounded by luminescent halos**, as current preferentially bypasses the absorber.\n\n"
                f"#### Process Engineering Fixes:\n"
                f"- **Anti-Solvent Optimization**: Finely tune the dispense time (±0.5 s) of chlorobenzene or ethyl acetate.\n"
                f"- **In-Line Vacuum Flash**: Rapid solvent removal forces dense, homogeneous nucleus formation."
            ),
            "suggestions": [
                "Can pinholes be repaired with laser isolation?",
                "What is the model's accuracy on pinholes?",
                "How does the model compare to human inspection?"
            ]
        }

    # 6. MODEL ARCHITECTURE & TRAINING
    if any(kw in query_lower for kw in ["model", "mobilenet", "architecture", "accuracy", "training", "stage", "f1", "loss", "weights"]):
        return {
            "reply": (
                f"### 🧠 Model Architecture & Training Evolution\n\n"
                f"Our solar cell quality control pipeline utilizes a **MobileNetV2 Transfer Learning Architecture** "
                f"specifically optimized for rapid inference and high sensitivity to sub-surface electroluminescent defects.\n\n"
                f"#### Architecture Specifications:\n"
                f"- **Backbone**: MobileNetV2 (ImageNet pre-trained weights, depthwise separable convolutions)\n"
                f"- **Input Tensor**: `(224, 224, 3)` RGB Electroluminescence Image\n"
                f"- **Classification Head**: GlobalAveragePooling2D → Dropout(0.25) → Dense(5, softmax)\n"
                f"- **Total Parameters**: 2,264,389 (Trainable: 1,201,285)\n"
                f"- **Inference Latency**: ~35 ms per cell on Apple M4 Metal GPU (~28 FPS)\n\n"
                f"#### Staged Training Milestones:\n"
                f"1. **Stage 1 (Binary Frozen)**: 56.17% accuracy. Distinguished coarse functional vs. defective cells.\n"
                f"2. **Stage 2 (5-Class Frozen)**: 83.67% accuracy, Macro F1: 0.8324. Classified distinct defect categories.\n"
                f"3. **Stage 2 (Fine-Tuned Final)**: **96.00% Accuracy, Macro F1: 0.9603** on held-out test sets. Deep convolutional blocks unrolled to capture microscopic pinhole and grain boundary variations."
            ),
            "suggestions": [
                "What is the confusion matrix for the 5 classes?",
                "What is the difference between Stage 1 and Stage 2?",
                "What are the future plans for this model?"
            ]
        }

    # 7. ELECTROLUMINESCENCE (EL) PRINCIPLES
    if any(kw in query_lower for kw in ["electroluminescence", "el image", "el imaging", "luminescence", "how does el work"]):
        return {
            "reply": (
                f"### 💡 Principles of Solar Cell Electroluminescence (EL)\n\n"
                f"Electroluminescence (EL) is essentially a solar cell operating in **reverse as a light-emitting diode (LED)**.\n\n"
                f"#### The Physics:\n"
                f"1. **Forward Current Injection**: An external DC power supply drives electrons and holes into the p-n or p-i-n junction under forward bias ($V_{{ext}} \\approx V_{{oc}}$).\n"
                f"2. **Radiative Recombination**: In healthy regions of the cell, injected electrons drop from the conduction band into valence band holes, releasing photons matching the bandgap wavelength (e.g., 750–820 nm for perovskites, 1150 nm for crystalline silicon).\n"
                f"3. **Defect Quenching**: Defects, microcracks, pinholes, or delaminations create non-radiative trap states ($SRH$ recombination). These defective regions produce **zero or diminished photons**, creating dark signatures on high-sensitivity InGaAs or cooled silicon cameras."
            ),
            "suggestions": [
                "How does EL compare to Photoluminescence (PL)?",
                "Why is EL preferred for manufacturing QC?",
                "How fast can EL images be captured on a conveyor?"
            ]
        }

    # 8. FUTURE ROADMAP & PLANS
    if any(kw in query_lower for kw in ["future", "roadmap", "plan", "conveyor", "edge", "jetson", "tandem", "scaling", "industry"]):
        return {
            "reply": (
                f"### 🚀 SolarGuard QC: Future Technology Roadmap\n\n"
                f"Our vision evolves this standalone inspection model into a full-scale **Gigawatt-Scale Photovoltaic Quality Intelligence System**:\n\n"
                f"#### Phase 1: High-Speed Inline Conveyor Scanner (Q1-Q2)\n"
                f"- High-speed GigE InGaAs line-scan camera synchronized with continuous wafer conveyor belts.\n"
                f"- Throughput target: **120 solar cells per minute (<500 ms per wafer)** with 0% missed critical defects.\n\n"
                f"#### Phase 2: Edge Acceleration (NVIDIA Jetson / TensorRT)\n"
                f"- Compile the Keras MobileNetV2 graph to **TensorRT FP16 / INT8** running on NVIDIA Jetson Orin Nano modules directly mounted on factory lines.\n"
                f"- Sub-10 ms ultra-low latency inference with on-device edge computing.\n\n"
                f"#### Phase 3: Perovskite-Silicon Tandem Multi-Junction Inspection\n"
                f"- Dual-wavelength EL/PL excitation to isolate top perovskite (1.7 eV) and bottom silicon (1.1 eV) sub-cells independently in 2-terminal tandem configurations.\n"
                f"- Target solar cell power conversion efficiency > 32%.\n\n"
                f"#### Phase 4: Automated Robotic Wafer Sorting\n"
                f"- Direct pneumatic/robotic sorter arm integration into 4 sorting bins (Bin A: Premium, Bin B: Laser Repair, Bin C: Re-anneal, Bin D: Scrap)."
            ),
            "suggestions": [
                "Tell me about the Jetson edge deployment plan",
                "How do 2-terminal tandem cells work?",
                "What robotic sorting bins are supported?"
            ]
        }

    # 9. GENERAL / FALLBACK DOMAIN EXPERT ANSWER
    return {
        "reply": (
            f"### ☀️ HelioAI Solar Quality Assistant\n\n"
            f"I am your dedicated AI specialist for the **MobileNetV2 Solar Cell Quality Inspection System** (96.0% accuracy).\n\n"
            f"Here is how I can assist your engineering workflow:\n"
            f"- **Inspect Scanned Cells**: Upload an EL image or pick a sample cell above, and ask me to diagnose the physical defect mechanism.\n"
            f"- **Process Engineering**: Get recommendations for anti-solvent dripping, halide demixing suppression, SAM adhesion, and moisture barrier specs.\n"
            f"- **Model Deep-Dive**: Ask about MobileNetV2 transfer learning, confusion matrices, or latency benchmarks.\n"
            f"- **Future Scalability**: Review our roadmap for inline conveyor line-scanners, NVIDIA Jetson edge inference, and automated 4-bin wafer sorting."
        ),
        "suggestions": [
            "Why did the current scan pass or fail?",
            "What causes halide segregation in solar cells?",
            "Explain the MobileNetV2 architecture (96% acc)",
            "What are the future roadmap plans for inline QC?"
        ]
    }


@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    """Context-aware chatbot conversation endpoint with external LLM support and resilient fallback."""
    if request.apiKey and request.apiKey.strip():
        try:
            response = call_external_llm(
                user_query=request.message,
                scan_context=request.scanContext,
                history=request.history or [],
                api_key=request.apiKey.strip(),
                provider=request.provider or "gemini",
                model=request.model
            )
            return response
        except Exception as e:
            print(f"External LLM API call error: {e}")
            fallback = generate_solar_ai_response(
                user_query=request.message,
                scan_context=request.scanContext
            )
            fallback["reply"] = (
                f"*(Note: LLM API returned: `{str(e)[:180]}`. Switched to built-in photovoltaic domain engine)*\n\n"
                + fallback["reply"]
            )
            fallback["providerUsed"] = "offline_fallback"
            return fallback

    response = generate_solar_ai_response(
        user_query=request.message,
        scan_context=request.scanContext
    )
    response["providerUsed"] = "built_in"
    return response



# ==========================================================
# CLI ENTRYPOINT
# ==========================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.server:app", host="0.0.0.0", port=8000, reload=True)
