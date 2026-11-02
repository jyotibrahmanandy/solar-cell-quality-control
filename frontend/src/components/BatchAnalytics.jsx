import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  Cpu,
  Layers,
  ShieldCheck,
  FileSpreadsheet
} from 'lucide-react';

export default function BatchAnalytics({ onSelectCellForInspection }) {
  const [batchData, setBatchData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    runBatchInspection();
  }, []);

  const runBatchInspection = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/batch-inspect', { method: 'POST' });
      if (!res.ok) {
        throw new Error(`Batch inspection failed (${res.status})`);
      }
      const data = await res.json();
      setBatchData(data);
    } catch (err) {
      setError(err.message || 'Failed to execute batch test');
    } finally {
      setLoading(false);
    }
  };

  const getDefectName = (id) => {
    const map = {
      defect_halide_segregation: 'Halide Segregation',
      defect_layer_delamination: 'Layer Delamination',
      defect_phase_degradation: 'Phase Degradation',
      defect_pinhole: 'Pinhole Defect',
      functional: 'Functional',
    };
    return map[id] || id.replace('defect_', '').replace('_', ' ').toUpperCase();
  };

  return (
    <div className="batch-analytics-container">
      {/* Section Header */}
      <div className="section-header">
        <div className="title-group">
          <h2>
            <BarChart3 className="accent" size={24} />
            <span>Industrial Fleet & Batch Wafer Analytics</span>
          </h2>
          <p>Real-time statistical yield telemetry across production lots and held-out test datasets.</p>
        </div>
        <button
          className="btn-primary"
          style={{ padding: '0.65rem 1.25rem', fontSize: '0.85rem' }}
          onClick={runBatchInspection}
          disabled={loading}
          id="btn-rerun-batch"
        >
          <RefreshCw size={15} className={loading ? 'spin' : ''} />
          <span>{loading ? 'Running Telemetry...' : 'Re-Run Batch Audit'}</span>
        </button>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: '#F87171', borderRadius: '8px', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="analytics-grid">
        <div className="analytics-kpi-card glass-panel">
          <div className="kpi-icon-wrap cyan">
            <Cpu size={24} />
          </div>
          <div className="kpi-text">
            <h3>{batchData ? batchData.totalInspected : '--'}</h3>
            <p>Total Wafers Inspected</p>
          </div>
        </div>

        <div className="analytics-kpi-card glass-panel">
          <div className="kpi-icon-wrap green">
            <ShieldCheck size={24} />
          </div>
          <div className="kpi-text">
            <h3>{batchData ? `${batchData.yieldRate}%` : '--'}</h3>
            <p>Certified Yield Rate</p>
          </div>
        </div>

        <div className="analytics-kpi-card glass-panel">
          <div className="kpi-icon-wrap green">
            <CheckCircle2 size={24} />
          </div>
          <div className="kpi-text">
            <h3>{batchData ? batchData.passedCount : '--'}</h3>
            <p>Passed Modules (Bin A)</p>
          </div>
        </div>

        <div className="analytics-kpi-card glass-panel">
          <div className="kpi-icon-wrap red">
            <XCircle size={24} />
          </div>
          <div className="kpi-text">
            <h3>{batchData ? batchData.failedCount : '--'}</h3>
            <p>Rejected Wafers (Bin B/C/D)</p>
          </div>
        </div>
      </div>

      {/* Defect Distribution Breakdown */}
      {batchData && batchData.defectDistribution && (
        <div className="glass-panel" style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} className="accent" />
            <span>Defect Class Distribution in Current Inspection Lot</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
            {Object.entries(batchData.defectDistribution).map(([defId, count], idx) => {
              const totalDefects = batchData.failedCount || 1;
              const pct = Math.round((count / totalDefects) * 100);
              const colorMap = {
                defect_halide_segregation: '#F59E0B',
                defect_layer_delamination: '#EF4444',
                defect_phase_degradation: '#DC2626',
                defect_pinhole: '#F97316',
              };
              const color = colorMap[defId] || '#38BDF8';

              return (
                <div
                  key={idx}
                  style={{
                    padding: '1rem',
                    background: 'rgba(15, 23, 42, 0.7)',
                    borderRadius: '10px',
                    border: '1px solid var(--bg-card-border)',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem', fontSize: '0.85rem' }}>
                    <span style={{ fontWeight: 600, color }}>{getDefectName(defId)}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                      {count} cells ({pct}%)
                    </span>
                  </div>
                  <div className="prob-track">
                    <div
                      className="prob-fill"
                      style={{ width: `${pct}%`, backgroundColor: color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Batch Inspection Lot Table */}
      <div className="glass-panel">
        <h3 style={{ fontSize: '1.1rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileSpreadsheet size={18} className="accent" />
          <span>Lot Inspection Log (Individual Wafer Traceability)</span>
        </h3>

        <div className="data-table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Wafer ID</th>
                <th>True Ground Truth</th>
                <th>AI Model Prediction</th>
                <th>Confidence</th>
                <th>Severity</th>
                <th>Quality Status</th>
              </tr>
            </thead>
            <tbody>
              {batchData && batchData.items ? (
                batchData.items.map((row, idx) => (
                  <tr key={idx}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{row.filename}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{getDefectName(row.actual)}</td>
                    <td style={{ fontWeight: 600 }}>{row.displayName}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{row.confidence}%</td>
                    <td>
                      <span
                        style={{
                          fontSize: '0.75rem',
                          fontFamily: 'var(--font-mono)',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          background: row.severity === 'None' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                          color: row.severity === 'None' ? '#34D399' : '#F87171',
                        }}
                      >
                        {row.severity}
                      </span>
                    </td>
                    <td>
                      <span className={`badge-status ${row.status.toLowerCase()}`}>
                        {row.status === 'PASS' ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                        <span>{row.status}</span>
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    Loading wafer batch audit...
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
