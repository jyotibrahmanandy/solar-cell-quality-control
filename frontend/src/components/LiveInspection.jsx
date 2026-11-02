import React, { useState, useRef } from 'react';
import confetti from 'canvas-confetti';
import {
  Upload,
  CheckCircle2,
  XCircle,
  Zap,
  Activity,
  Maximize2,
  Download,
  MessageSquare,
  Eye,
  Layers,
  Sliders,
  TrendingDown,
  Cpu,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function LiveInspection({ onOpenChatWithContext, onNavigateToBenchmark }) {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('heatmap'); // 'heatmap' | 'original' | 'edge' | 'inverted'
  const [dragActive, setDragActive] = useState(false);
  const [showGrid, setShowGrid] = useState(true);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (file) => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`Inference failed with status ${res.status}`);
      }

      const data = await res.json();
      setPrediction(data);

      if (data.status === 'PASS') {
        triggerPassConfetti();
      }
    } catch (err) {
      setError(err.message || 'Failed to analyze uploaded image');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadDemoSample = async () => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('category', 'functional');
      formData.append('filename', 'functional_test_0000.png');

      const res = await fetch('/api/predict-sample', {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) throw new Error('Could not load demo sample');
      const data = await res.json();
      setPrediction(data);
      if (data.status === 'PASS') triggerPassConfetti();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const triggerPassConfetti = () => {
    try {
      confetti({
        particleCount: 45,
        spread: 60,
        origin: { y: 0.65 },
        colors: ['#10B981', '#34D399', '#5865F2', '#F59E0B'],
      });
    } catch (e) {
      // ignore
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleExportCertificate = () => {
    if (!prediction) return;
    const cert = {
      title: "Solar Cell Electroluminescence Quality Inspection Certificate",
      timestamp: new Date().toISOString(),
      model: "MobileNetV2 Transfer Learning (96.0% Held-Out Test Accuracy)",
      result: {
        verdict: prediction.status,
        classification: prediction.displayName,
        confidence: `${prediction.confidence}%`,
        category: prediction.category,
        severity: prediction.severity,
        sortingBin: prediction.sortingBin,
        pceImpact: prediction.efficiencyImpact,
        fillFactorImpact: prediction.fillFactorImpact,
      },
      engineeringRemedies: prediction.manufacturingRemedy,
      signature: "Automated HelioScan AI System v2.0",
    };

    const blob = new Blob([JSON.stringify(cert, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SolarQC_Certificate_${prediction.predictedClass}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const currentOverlayImage = () => {
    if (!prediction || !prediction.overlays) return null;
    return prediction.overlays[viewMode] || prediction.overlays.original;
  };

  return (
    <div className="live-inspection-minimal">
      {/* Page Title & Minimal Subtitle */}
      <div className="minimal-page-header">
        <div>
          <h2>Live Electroluminescence Inspection</h2>
          <p>Drop or upload raw photovoltaic EL images for real-time defect diagnosis &amp; physical metrics.</p>
        </div>
        <div className="header-hint">
          <span>Looking for benchmark presets?</span>
          <button 
            type="button" 
            className="link-btn" 
            onClick={onNavigateToBenchmark}
            id="btn-goto-benchmarks"
          >
            Go to Model Benchmarks <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* Main Inspection Grid */}
      <div className="inspection-grid-minimal">
        {/* Left Column: Visualizer & Dropzone */}
        <div className="visualizer-section">
          {/* Visualizer Display Box */}
          <div className="image-canvas-frame">
            {currentOverlayImage() ? (
              <img
                src={currentOverlayImage()}
                alt="Solar Cell Inspection"
                id="inspection-display-image"
              />
            ) : (
              <div className="awaiting-image-box">
                <Activity size={36} className="awaiting-icon" />
                <h4>No Cell Loaded</h4>
                <p>Upload a cell image below or run a demo scan to inspect.</p>
                <button
                  type="button"
                  className="btn-discord-outline"
                  onClick={handleLoadDemoSample}
                  disabled={loading}
                >
                  <Sparkles size={14} />
                  <span>Load Demo Wafer</span>
                </button>
              </div>
            )}

            {/* Laser Scan Animation Line */}
            {loading && <div className="scan-laser-line" />}

            {/* HUD Reticles */}
            {showGrid && currentOverlayImage() && (
              <>
                <div className="crosshair-grid" />
                <div className="reticle-corner reticle-top-left" />
                <div className="reticle-corner reticle-top-right" />
                <div className="reticle-corner reticle-bottom-left" />
                <div className="reticle-corner reticle-bottom-right" />
              </>
            )}

            {/* HUD Metadata Overlay */}
            {currentOverlayImage() && (
              <div className="frame-hud-meta">
                <span>224×224 px • RGB</span>
                <span>MODE: {viewMode.toUpperCase()}</span>
                <span>~35ms (Apple M4 Metal)</span>
              </div>
            )}
          </div>

          {/* Mode Switcher Toolbar */}
          {prediction && (
            <div className="view-mode-bar">
              <div className="mode-btn-group">
                <button
                  className={`view-mode-pill ${viewMode === 'heatmap' ? 'active' : ''}`}
                  onClick={() => setViewMode('heatmap')}
                  id="btn-mode-heatmap"
                >
                  <Zap size={13} />
                  <span>Heatmap</span>
                </button>
                <button
                  className={`view-mode-pill ${viewMode === 'original' ? 'active' : ''}`}
                  onClick={() => setViewMode('original')}
                  id="btn-mode-raw"
                >
                  <Eye size={13} />
                  <span>Raw EL</span>
                </button>
                <button
                  className={`view-mode-pill ${viewMode === 'edge' ? 'active' : ''}`}
                  onClick={() => setViewMode('edge')}
                  id="btn-mode-edge"
                >
                  <Layers size={13} />
                  <span>Cracks</span>
                </button>
                <button
                  className={`view-mode-pill ${viewMode === 'inverted' ? 'active' : ''}`}
                  onClick={() => setViewMode('inverted')}
                  id="btn-mode-inverted"
                >
                  <Sliders size={13} />
                  <span>Inverted</span>
                </button>
              </div>

              <button
                className="btn-grid-toggle"
                onClick={() => setShowGrid(!showGrid)}
                id="btn-toggle-grid"
                title="Toggle inspection reticle"
              >
                <Maximize2 size={13} />
                <span>{showGrid ? 'Grid' : 'Clean'}</span>
              </button>
            </div>
          )}

          {/* Minimal Upload Dropzone */}
          <div
            className={`upload-dropzone-minimal ${dragActive ? 'drag-active' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            id="image-dropzone"
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept="image/png, image/jpeg, image/jpg"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileUpload(e.target.files[0]);
                }
              }}
            />
            <div className="dropzone-minimal-inner">
              <Upload size={20} className="upload-icon" />
              <div>
                <strong>Choose an EL image or drag it here</strong>
                <span>Supports InGaAs/Silicon camera captures (.png, .jpg)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Prediction Decision & Physics */}
        <div className="results-section">
          {error && (
            <div className="alert-error-box">
              <strong>Error:</strong> {error}
            </div>
          )}

          {loading && !prediction && (
            <div className="loading-card">
              <Activity size={28} className="spin-icon" />
              <h4>Running MobileNetV2 Neural Inference...</h4>
              <p>Analyzing sub-surface radiative recombination &amp; generating Turbo colormaps.</p>
            </div>
          )}

          {!prediction && !loading && (
            <div className="ready-guide-card">
              <h3>Ready for Inspection</h3>
              <p>
                Drop any electroluminescence image above to classify the solar wafer across 5 condition classes with <strong>96.0% accuracy</strong>.
              </p>
              <div className="supported-defects-list">
                <div className="defect-chip">⚡ Halide Segregation</div>
                <div className="defect-chip">💥 Layer Delamination</div>
                <div className="defect-chip">🌡️ Phase Degradation</div>
                <div className="defect-chip">🕳️ Micro-Pinholes</div>
                <div className="defect-chip pass">✅ Certified Pass</div>
              </div>
            </div>
          )}

          {prediction && (
            <>
              {/* Verdict Banner Card */}
              <div
                className={`verdict-card-minimal ${prediction.status === 'PASS' ? 'pass' : 'fail'}`}
                id="inspection-verdict-card"
              >
                <div className="verdict-head">
                  <div className="verdict-icon">
                    {prediction.status === 'PASS' ? (
                      <CheckCircle2 size={26} />
                    ) : (
                      <XCircle size={26} />
                    )}
                  </div>
                  <div className="verdict-titles">
                    <span className="verdict-tag">
                      {prediction.status === 'PASS' ? 'QUALITY PASS' : 'DEFECT DETECTED'}
                    </span>
                    <h3>{prediction.displayName}</h3>
                    <p>{prediction.subtitle}</p>
                  </div>
                  <div className="verdict-conf">
                    <strong>{prediction.confidence}%</strong>
                    <span>Confidence</span>
                  </div>
                </div>

                {/* Physics Metrics Pill Row */}
                <div className="metrics-pill-row">
                  <div className="pill-metric">
                    <span className="pill-label">PCE Impact</span>
                    <strong className={prediction.status === 'PASS' ? 'text-green' : 'text-red'}>
                      {prediction.efficiencyImpact}
                    </strong>
                  </div>
                  <div className="pill-metric">
                    <span className="pill-label">Fill Factor</span>
                    <strong className={prediction.status === 'PASS' ? 'text-green' : 'text-amber'}>
                      {prediction.fillFactorImpact}
                    </strong>
                  </div>
                  <div className="pill-metric">
                    <span className="pill-label">Routing</span>
                    <strong className="text-blue">{prediction.sortingBin.split(' - ')[0]}</strong>
                  </div>
                </div>
              </div>

              {/* Class Probability Distribution */}
              <div className="prob-minimal-card">
                <div className="prob-header">
                  <span>Class Confidence Breakdown</span>
                  <span className="mono-tag">5-Class Softmax</span>
                </div>
                {prediction.probabilities.map((item, idx) => (
                  <div key={idx} className="prob-item-row">
                    <span className="prob-item-name" style={{ color: item.color }}>
                      {item.displayName}
                    </span>
                    <div className="prob-item-track">
                      <div
                        className="prob-item-bar"
                        style={{
                          width: `${Math.max(item.probability, 2)}%`,
                          backgroundColor: item.color,
                        }}
                      />
                    </div>
                    <span className="prob-item-val">{item.probability.toFixed(1)}%</span>
                  </div>
                ))}
              </div>

              {/* Physical Failure & Fab Remediation */}
              <div className="physics-minimal-card">
                <h4>
                  <Activity size={15} />
                  <span>Physical Mechanism &amp; Fab Action</span>
                </h4>
                <p className="physics-text">{prediction.physicalMechanism}</p>

                {prediction.manufacturingRemedy && prediction.manufacturingRemedy.length > 0 && (
                  <div className="remedy-box">
                    <span className="remedy-title">Recommended Fab Action Plan:</span>
                    <ul>
                      {prediction.manufacturingRemedy.map((r, i) => (
                        <li key={i}>{r}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="minimal-actions-row">
                <button
                  type="button"
                  className="btn-discord-primary"
                  onClick={() => onOpenChatWithContext(prediction)}
                  id="btn-ask-helio-ai"
                >
                  <MessageSquare size={15} />
                  <span>Ask HelioBot About This Wafer</span>
                </button>
                <button
                  type="button"
                  className="btn-discord-secondary"
                  onClick={handleExportCertificate}
                  id="btn-export-certificate"
                >
                  <Download size={15} />
                  <span>Export JSON</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
