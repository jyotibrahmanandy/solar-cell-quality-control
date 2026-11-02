import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Layers,
  Activity,
  CheckCircle2,
  TrendingUp,
  Sliders,
  Sparkles,
  BarChart3,
  ShieldCheck,
  AlertTriangle,
  Zap,
  Eye,
  Check,
  Play
} from 'lucide-react';

export default function ModelSpecs() {
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [loadingSample, setLoadingSample] = useState(false);
  const [errorSample, setErrorSample] = useState(null);

  useEffect(() => {
    fetchSamples();
  }, []);

  const fetchSamples = async () => {
    try {
      const res = await fetch('/api/samples');
      if (res.ok) {
        const data = await res.json();
        setSamples(data.samples || []);
      }
    } catch (err) {
      console.error('Failed to load benchmark samples:', err);
    }
  };

  const handleTestPreset = async (sample) => {
    setSelectedSample(sample);
    setLoadingSample(true);
    setErrorSample(null);

    const formData = new FormData();
    formData.append('category', sample.classId);
    formData.append('filename', sample.filename);

    try {
      const res = await fetch('/api/predict-sample', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Inference error (${res.status})`);
      }

      const data = await res.json();
      setBenchmarkResult(data);
    } catch (err) {
      setErrorSample(err.message || 'Failed to inspect benchmark wafer');
    } finally {
      setLoadingSample(false);
    }
  };

  const confusionMatrix = [
    { label: "Halide Segregation", vals: [60, 0, 0, 0, 0], total: 60, recall: "100.0%" },
    { label: "Layer Delamination", vals: [0, 57, 0, 0, 3], total: 60, recall: "95.0%" },
    { label: "Phase Degradation", vals: [7, 0, 53, 0, 0], total: 60, recall: "88.3%" },
    { label: "Pinhole Defect", vals: [0, 0, 0, 60, 0], total: 60, recall: "100.0%" },
    { label: "Functional (Pass)", vals: [2, 0, 0, 0, 58], total: 60, recall: "96.7%" },
  ];

  const colHeaders = ["Halide", "Layer", "Phase", "Pinhole", "Functional"];

  const stages = [
    {
      stage: "Stage 1: Binary Frozen",
      accuracy: "56.17%",
      macroF1: "0.3333*",
      params: "2,259,265",
      dataset: "600 Images",
      badge: "Baseline Extractor",
      notes: "Initial transfer learning pass distinguishing general defective vs functional cells with frozen MobileNetV2 backbone."
    },
    {
      stage: "Stage 2: 5-Class Frozen",
      accuracy: "83.67%",
      macroF1: "0.8324",
      params: "2,264,389",
      dataset: "300 Images",
      badge: "Multi-Class Transfer",
      notes: "Classification head expanded to 5 discrete defect categories with MobileNetV2 frozen feature backbone."
    },
    {
      stage: "Stage 2: Fine-Tuned (Final)",
      accuracy: "96.00%",
      macroF1: "0.9603",
      params: "2,264,389",
      dataset: "300 Images",
      badge: "Production Model (Active)",
      notes: "Deep convolutional layers unrolled for end-to-end backpropagation, capturing subtle sub-surface electroluminescence contrast gradients."
    }
  ];

  return (
    <div className="model-specs-container">
      {/* Header */}
      <div className="section-header-discord">
        <div>
          <h2>Model Benchmark Lab &amp; Neural Specifications</h2>
          <p>Held-out test wafer evaluation, confusion matrix validation, and MobileNetV2 mathematical architecture.</p>
        </div>
      </div>

      {/* SECTION 1: QUICK BENCHMARK PRESETS (MOVED HERE) */}
      <div className="discord-panel benchmark-presets-section">
        <div className="panel-title-row">
          <div className="panel-title-group">
            <Zap className="accent-amber" size={18} />
            <h3>Held-Out Benchmark Presets (Test Wafers)</h3>
          </div>
          <span className="pill-badge">300 Held-Out Cells (60/Class)</span>
        </div>
        <p className="panel-desc">
          Select any real test cell from the held-out validation suite below to run instant inference against the production MobileNetV2 model.
        </p>

        {/* Preset Chips Grid */}
        <div className="preset-buttons-grid">
          {samples.map((s, idx) => {
            const isSelected = selectedSample?.filename === s.filename;
            return (
              <button
                key={idx}
                type="button"
                className={`preset-chip-btn ${isSelected ? 'active' : ''}`}
                onClick={() => handleTestPreset(s)}
                id={`sample-preset-${idx}`}
              >
                <div
                  className="preset-chip-icon"
                  style={{
                    backgroundColor: s.status === 'PASS' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: s.status === 'PASS' ? '#34D399' : '#F87171',
                  }}
                >
                  {s.status === 'PASS' ? <ShieldCheck size={16} /> : <AlertTriangle size={16} />}
                </div>
                <div className="preset-chip-info">
                  <span className="preset-chip-name">{s.displayName}</span>
                  <span className="preset-chip-filename">{s.filename}</span>
                </div>
                <div className="preset-chip-action">
                  <Play size={12} />
                </div>
              </button>
            );
          })}
        </div>

        {/* Preset Benchmark Evaluation Result View */}
        {loadingSample && (
          <div className="benchmark-eval-box loading">
            <Activity size={20} className="spin-icon" />
            <span>Evaluating benchmark wafer with MobileNetV2...</span>
          </div>
        )}

        {errorSample && (
          <div className="alert-error-box" style={{ marginTop: '1rem' }}>
            {errorSample}
          </div>
        )}

        {benchmarkResult && !loadingSample && (
          <div className="benchmark-eval-box success">
            <div className="benchmark-eval-grid">
              <div className="eval-preview-wrap">
                <img
                  src={benchmarkResult.overlays?.heatmap || benchmarkResult.overlays?.original}
                  alt={benchmarkResult.displayName}
                  className="eval-preview-img"
                />
                <span className="eval-preview-badge">Turbo Anomaly Heatmap</span>
              </div>
              <div className="eval-info-wrap">
                <div className="eval-status-line">
                  <span className={`eval-status-tag ${benchmarkResult.status === 'PASS' ? 'pass' : 'fail'}`}>
                    {benchmarkResult.status === 'PASS' ? 'BENCHMARK PASS' : 'DEFECT DETECTED'}
                  </span>
                  <span className="eval-conf-tag">
                    Confidence: <strong>{benchmarkResult.confidence}%</strong>
                  </span>
                </div>
                <h4>{benchmarkResult.displayName}</h4>
                <p className="eval-subtitle">{benchmarkResult.subtitle}</p>
                <div className="eval-metrics-row">
                  <div>
                    <span className="label">PCE Penalty</span>
                    <strong>{benchmarkResult.efficiencyImpact}</strong>
                  </div>
                  <div>
                    <span className="label">Fill Factor</span>
                    <strong>{benchmarkResult.fillFactorImpact}</strong>
                  </div>
                  <div>
                    <span className="label">Robotic Sorter</span>
                    <strong>{benchmarkResult.sortingBin.split(' - ')[0]}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Model Evolution Stages */}
      <div className="discord-panel" style={{ marginBottom: '1.5rem' }}>
        <div className="panel-title-group" style={{ marginBottom: '1rem' }}>
          <TrendingUp className="accent-amber" size={18} />
          <h3>Staged Model Training &amp; Performance Evolution</h3>
        </div>

        <div className="stages-grid">
          {stages.map((st, idx) => (
            <div
              key={idx}
              className={`stage-card ${idx === 2 ? 'stage-card-active' : ''}`}
            >
              <div className="stage-top-bar">
                <span className="stage-badge">{st.badge}</span>
                <span className="stage-dataset">{st.dataset}</span>
              </div>

              <h4>{st.stage}</h4>
              <p className="stage-notes">{st.notes}</p>

              <div className="stage-metrics-row">
                <div>
                  <span className="metric-label">TEST ACCURACY</span>
                  <strong className={idx === 2 ? 'text-green' : ''}>{st.accuracy}</strong>
                </div>
                <div>
                  <span className="metric-label">MACRO F1</span>
                  <strong className={idx === 2 ? 'text-green' : ''}>{st.macroF1}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Benchmarks Grid: Confusion Matrix & Architecture Summary */}
      <div className="benchmarks-grid">
        {/* Confusion Matrix */}
        <div className="discord-panel">
          <div className="panel-title-group" style={{ marginBottom: '0.4rem' }}>
            <BarChart3 className="accent-blue" size={18} />
            <h3>Final Confusion Matrix (300 Test Cells)</h3>
          </div>
          <p className="panel-desc" style={{ marginBottom: '1rem' }}>
            Balanced test validation: exactly 60 images evaluated per defect category.
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table className="confusion-matrix-table">
              <thead>
                <tr>
                  <th style={{ textAlign: 'left' }}>True \ Predicted</th>
                  {colHeaders.map((c, i) => (
                    <th key={i}>{c}</th>
                  ))}
                  <th>Recall</th>
                </tr>
              </thead>
              <tbody>
                {confusionMatrix.map((row, rIdx) => (
                  <tr key={rIdx}>
                    <td style={{ textAlign: 'left', fontWeight: 600 }}>{row.label}</td>
                    {row.vals.map((v, cIdx) => {
                      const isDiag = rIdx === cIdx;
                      return (
                        <td
                          key={cIdx}
                          className={isDiag ? 'cm-cell-diag' : 'cm-cell-off'}
                          style={{
                            background: isDiag ? `rgba(16, 185, 129, ${Math.max(v / 60, 0.25)})` : v > 0 ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
                            color: isDiag ? '#FFF' : v > 0 ? '#F87171' : 'var(--text-muted)',
                            fontWeight: isDiag ? 700 : 400,
                          }}
                        >
                          {v}
                        </td>
                      );
                    })}
                    <td style={{ fontWeight: 700, color: '#34D399' }}>{row.recall}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Model Architecture Specs */}
        <div className="discord-panel">
          <div className="panel-title-group" style={{ marginBottom: '1rem' }}>
            <Sliders className="accent-blue" size={18} />
            <h3>MobileNetV2 Architecture Specifications</h3>
          </div>

          <div className="specs-list">
            <div className="spec-item">
              <span className="spec-label">Neural Backbone</span>
              <strong className="spec-val">MobileNetV2 (Inverted Residuals)</strong>
            </div>

            <div className="spec-item">
              <span className="spec-label">Input Tensor</span>
              <strong className="spec-val">224 × 224 × 3 (RGB EL Image)</strong>
            </div>

            <div className="spec-item">
              <span className="spec-label">Total Parameters</span>
              <strong className="spec-val">2,264,389 (~9.1 MB Weights)</strong>
            </div>

            <div className="spec-item">
              <span className="spec-label">Trainable Parameters</span>
              <strong className="spec-val">1,201,285 Parameters</strong>
            </div>

            <div className="spec-item">
              <span className="spec-label">Inference Engine</span>
              <strong className="spec-val text-green">Apple M4 Metal Acceleration</strong>
            </div>

            <div className="spec-item">
              <span className="spec-label">Measured Latency</span>
              <strong className="spec-val text-green">~35 ms per cell (~28.5 FPS)</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
