import React from 'react';
import { 
  ArrowRight, 
  ShieldAlert, 
  Zap, 
  Layers, 
  Activity, 
  Eye, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles,
  BarChart2,
  Atom,
  Flame
} from 'lucide-react';
import landingStoryImg from '../assets/landing_story.jpg';
import helioBotImg from '../assets/helio_bot.jpg';

export default function LandingPage({ onEnterInspection, onEnterBenchmark }) {
  return (
    <div className="landing-story-container">
      {/* Hero Chapter: The Dawn of Tandem Photovoltaics */}
      <section className="story-hero-section">
        <div className="story-hero-content">
          <div className="story-pill">
            <Sparkles size={14} className="story-pill-icon" />
            <span>The Next-Generation Clean Energy Metrology</span>
          </div>
          <h1 className="story-hero-title">
            The Terawatt Era vs. <span className="story-highlight">The Invisible Flaw</span>
          </h1>
          <p className="story-hero-description">
            Perovskite-silicon tandem cells hold the golden promise of breaking past silicon's 
            theoretical 29.4% efficiency limit. But in the microscopic crystalline lattice, 
            dormant anomalies threaten gigawatts of clean energy before modules even ship.
          </p>

          <div className="story-cta-group">
            <button 
              className="story-btn-primary" 
              onClick={onEnterInspection}
              id="landing-hero-cta-inspection"
            >
              <span>Launch Live Inspection</span>
              <ArrowRight size={18} />
            </button>
            <button 
              className="story-btn-secondary" 
              onClick={onEnterBenchmark}
              id="landing-hero-cta-benchmark"
            >
              <BarChart2 size={18} />
              <span>Model Evaluation</span>
            </button>
          </div>

          <div className="story-stats-row">
            <div className="story-stat-card">
              <span className="stat-value">33.7%</span>
              <span className="stat-label">Tandem Lab Efficiency</span>
            </div>
            <div className="story-stat-divider" />
            <div className="story-stat-card">
              <span className="stat-value">&lt; 35ms</span>
              <span className="stat-label">Inline MobileNetV2 Latency</span>
            </div>
            <div className="story-stat-divider" />
            <div className="story-stat-card">
              <span className="stat-value">96.0%</span>
              <span className="stat-label">Held-Out Test Accuracy</span>
            </div>
          </div>
        </div>

        <div className="story-hero-visual">
          <div className="story-image-frame">
            <img 
              src={landingStoryImg} 
              alt="Perovskite-Silicon Tandem Defect Inspection Visual" 
              className="story-hero-img"
            />
            <div className="story-image-badge">
              <Atom size={16} />
              <span>Electroluminescence Sub-Surface Diagnostic</span>
            </div>
          </div>
        </div>
      </section>

      {/* Chapter 1: The Modern Dilemma */}
      <section className="story-chapter-section">
        <div className="chapter-header">
          <div className="chapter-tag">CHAPTER 01</div>
          <h2>The Fragile Miracle of Perovskite &amp; Tandem Cells</h2>
          <p>
            Standard single-junction silicon wafers are nearing their fundamental thermodynamic limit. 
            By stacking a high-bandgap perovskite crystal top layer over traditional silicon bottom absorbers, 
            tandem modules capture both blue and red solar spectra. Yet perovskites are notoriously vulnerable.
          </p>
        </div>

        <div className="chapter-grid">
          <div className="problem-card">
            <div className="problem-card-icon red">
              <Flame size={24} />
            </div>
            <h3>Thermal &amp; Moisture Decomposition</h3>
            <p>
              Organic halide perovskites undergo lattice phase segregation when subjected to heat cycling 
              or sub-ppm ambient humidity during fabrication, inducing dark micro-quenched zones.
            </p>
          </div>

          <div className="problem-card">
            <div className="problem-card-icon amber">
              <AlertTriangle size={24} />
            </div>
            <h3>Sub-Visual Micro-Cracking</h3>
            <p>
              Thermal mismatch between the silicon bottom wafer and perovskite thin-films causes microscopic 
              shear stresses. These invisible hairline fissures propagate into complete electrical open-circuits under mechanical loads.
            </p>
          </div>

          <div className="problem-card">
            <div className="problem-card-icon purple">
              <Layers size={24} />
            </div>
            <h3>Interfacial Shunts &amp; Solder Anomalies</h3>
            <p>
              Misaligned multi-busbars or localized pinholes allow reverse bias leakage currents, 
              leading to hot-spots capable of burning module encapsulants in utility-scale solar farms.
            </p>
          </div>
        </div>
      </section>

      {/* Chapter 2: The Metrology Gap */}
      <section className="story-chapter-section alternate">
        <div className="chapter-header">
          <div className="chapter-tag">CHAPTER 02</div>
          <h2>Why Conventional Quality Control Fails</h2>
          <p>
            Traditional optical camera inspection only sees the cell's physical surface. The true killer defects 
            lie buried beneath the anti-reflective coating and within the charge extraction interfaces.
          </p>
        </div>

        <div className="comparison-container">
          <div className="comparison-column legacy">
            <div className="comparison-header">
              <ShieldAlert size={20} className="icon-legacy" />
              <h3>Conventional RGB Vision</h3>
            </div>
            <ul className="comparison-list">
              <li>❌ Blind to sub-surface carrier recombination</li>
              <li>❌ Cannot detect electrical shunt current pathways</li>
              <li>❌ High false-negative rate on hair-thin crystalline micro-cracks</li>
              <li>❌ Manual operator fatigue on high-speed 3,600 wafers/hour conveyors</li>
            </ul>
          </div>

          <div className="comparison-column modern">
            <div className="comparison-header">
              <Zap size={20} className="icon-modern" />
              <h3>HelioScan Electroluminescence AI</h3>
            </div>
            <ul className="comparison-list">
              <li>✅ Direct radiative emission capture under forward-bias excitation</li>
              <li>✅ Real-time MobileNetV2 neural feature extraction (~35ms per cell)</li>
              <li>✅ Automated physical defect quantification (dead area, crack length)</li>
              <li>✅ Zero-drift edge inference directly on assembly line GPUs</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Chapter 3: Interactive Call to Action */}
      <section className="story-cta-section">
        <div className="cta-card">
          <div className="cta-content">
            <div className="cta-badge">EXPERIENCE THE PLATFORM</div>
            <h2>Ready to Inspect Production Wafers?</h2>
            <p>
              Step into the high-precision live inspection workbench. Upload actual electroluminescence wafer 
              captures or evaluate held-out test benchmarks across various defect topologies.
            </p>
            <div className="cta-buttons">
              <button 
                className="story-btn-primary" 
                onClick={onEnterInspection}
                id="btn-landing-to-inspection"
              >
                <span>Go to Live Inspection</span>
                <ArrowRight size={18} />
              </button>
              <button 
                className="story-btn-secondary" 
                onClick={onEnterBenchmark}
                id="btn-landing-to-benchmark"
              >
                <span>View Model Evaluation</span>
              </button>
            </div>
          </div>
          <div className="cta-character">
            <img src={helioBotImg} alt="HelioBot Assistant" className="cta-bot-img" />
            <div className="cta-bot-tip">
              "Need help understanding perovskite defect physics? Click me anytime in the top header!"
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
