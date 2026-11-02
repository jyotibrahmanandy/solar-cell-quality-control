import React from 'react';
import {
  Compass,
  Cpu,
  Layers,
  Zap,
  ShieldCheck,
  Activity,
  Maximize2,
  GitBranch,
  Bot,
  Truck,
  ArrowRight,
  Sparkles
} from 'lucide-react';

export default function FutureRoadmap() {
  const phases = [
    {
      phase: "Phase 1",
      timeline: "Q1 - Q2 2027",
      title: "High-Speed Inline Conveyor Line-Scan Integration",
      icon: <Activity size={22} color="#06B6D4" />,
      tag: "Gigawatt Fab Scale",
      description:
        "Transitioning from static laboratory inspection to synchronized high-speed conveyor imaging. Integrates 4096-pixel InGaAs line-scan cameras over continuous vacuum belts at 120 solar cells per minute (<500 ms per wafer). Direct industrial GigE Vision and GenICam PLC communication eliminates manufacturing bottlenecks.",
      deliverables: [
        "Continuous 120 wafers/min throughput testing",
        "Hardware-triggered forward-bias current injection pulse (5A, 50ms)",
        "Automated edge distortion and lens vignetting calibration",
        "Industrial OPC-UA / MQTT telemetry to Manufacturing Execution Systems (MES)"
      ],
      tags: ["InGaAs Line-Scan", "120 Wafers/Min", "GigE Vision", "OPC-UA MES"]
    },
    {
      phase: "Phase 2",
      timeline: "Q3 2027",
      title: "Edge Hardware Acceleration on NVIDIA Jetson & TensorRT",
      icon: <Cpu size={22} color="#F59E0B" />,
      tag: "Ultra-Low Latency Edge",
      description:
        "Compiling the trained MobileNetV2 TensorFlow model to NVIDIA TensorRT FP16/INT8 precision engines. Deploying directly on ruggedized NVIDIA Jetson Orin Nano / AGX Orin industrial edge computers located directly above the conveyor, dropping per-cell inference latency from 35ms to under 8ms.",
      deliverables: [
        "TensorRT INT8 Post-Training Quantization (PTQ) with zero accuracy degradation",
        "Sub-10ms end-to-end edge inference on Jetson Orin Nano",
        "Thermal-rated IP67 industrial edge enclosure for clean-room fab environments",
        "Local NVMe cyclic event buffer for micro-second traceability"
      ],
      tags: ["NVIDIA Jetson", "TensorRT INT8", "Sub-10ms Inference", "Edge Compute"]
    },
    {
      phase: "Phase 3",
      timeline: "Q4 2027 - Q1 2028",
      title: "Perovskite-Silicon Tandem Multi-Junction Spectral Inspection",
      icon: <Zap size={22} color="#10B981" />,
      tag: "Next-Gen Photovoltaics",
      description:
        "Extending the neural architecture to inspect 2-terminal (2T) and 4-terminal (4T) perovskite-on-silicon tandem cells targeting >32% power conversion efficiency (PCE). Implements dual-wavelength optical filtering to independently resolve defects in the wide-bandgap perovskite top cell (~780 nm emission) and the silicon bottom cell (~1150 nm emission).",
      deliverables: [
        "Dual-wavelength multi-spectral EL beam splitter optic system",
        "Independent sub-cell shunt and open-circuit voltage degradation mapping",
        "Inter-layer recombination junction (tunnel junction) tunnel-defect detection",
        "Support for Silicon Heterojunction (HJT) and TOPCon base substrates"
      ],
      tags: [">32% Tandem PCE", "Dual-Spectral EL", "2-Terminal & 4-Terminal", "Tunnel Junctions"]
    },
    {
      phase: "Phase 4",
      timeline: "Q2 2028",
      title: "Robotic High-Speed 4-Bin Wafer Sorting & Defect Rework",
      icon: <Bot size={22} color="#8B5CF6" />,
      tag: "Autonomous Robotics",
      description:
        "Closing the loop between deep learning quality classification and physical wafer routing. Direct pneumatic high-speed pick-and-place delta robot diverts wafers instantly into 4 automated quality bins with closed-loop laser isolation rework for local pinhole shunts.",
      deliverables: [
        "Bin A: Premium Grade (PCE > 24%, 0 defects) → Direct to module stringing",
        "Bin B: Laser Rework (Pinholes/edge shunts) → Divert to 532nm laser ablation",
        "Bin C: Thermal Annealing (Halide segregation) → Re-heat relaxation station",
        "Bin D: Structural Rejection (Delamination / phase decay) → Raw material reclamation"
      ],
      tags: ["Delta Pick-and-Place", "Laser Defect Isolation", "4-Bin Robotic Sorter", "Zero Waste"]
    },
    {
      phase: "Phase 5",
      timeline: "Q3 - Q4 2028",
      title: "Digital Twin & 25-Year Outdoor Degradation Forecasting",
      icon: <Sparkles size={22} color="#EC4899" />,
      tag: "Predictive Lifecycle Intelligence",
      description:
        "Coupling real-time EL defect fingerprints with physics-informed neural networks (PINNs) and weather telemetry. Forecasts the exact 25-year levelized cost of energy (LCOE) and annual degradation rate (target <0.5%/year) for every individual cell prior to module lamination.",
      deliverables: [
        "Physics-Informed Neural Network (PINN) lifetime decay modeling",
        "Integration with IEC 61215 accelerated damp-heat & thermal cycling benchmarks",
        "Individual wafer digital birth certificates stored in immutable cloud repository",
        "Automated module serial generation and bankability rating scores"
      ],
      tags: ["Digital Twin", "25-Year Degradation", "PINN AI", "LCOE Optimization"]
    }
  ];

  return (
    <div className="future-roadmap-container">
      {/* Header */}
      <div className="section-header">
        <div className="title-group">
          <h2>
            <Compass className="accent" size={24} />
            <span>Industrial Scaling & Technology Roadmap (2027 - 2028)</span>
          </h2>
          <p>Strategic deployment framework transforming our MobileNetV2 model into a gigawatt-scale autonomous fab system.</p>
        </div>
      </div>

      {/* Roadmap List */}
      <div className="roadmap-timeline">
        {phases.map((item, idx) => (
          <div key={idx} className="roadmap-card">
            <div className="phase-indicator">
              <span className="phase-number">{item.phase}</span>
              <span className="phase-timeline">{item.timeline}</span>
            </div>

            <div className="roadmap-content">
              <h3>
                {item.icon}
                <span>{item.title}</span>
              </h3>
              <p>{item.description}</p>

              <div style={{ marginBottom: '1rem', background: 'rgba(15, 23, 42, 0.6)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--solar-amber)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Target Milestones & Engineering Deliverables:
                </span>
                <ul style={{ marginTop: '0.4rem', marginLeft: '1.2rem', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                  {item.deliverables.map((deliv, dIdx) => (
                    <li key={dIdx} style={{ marginBottom: '0.2rem' }}>{deliv}</li>
                  ))}
                </ul>
              </div>

              <div className="roadmap-tags">
                {item.tags.map((t, tIdx) => (
                  <span key={tIdx} className="roadmap-tag">#{t}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
