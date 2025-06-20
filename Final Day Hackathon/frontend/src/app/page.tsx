'use client';

import { useState, useRef } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [rawResult, setRawResult] = useState<string>('');
  const [lcncStructure, setLcncStructure] = useState<any>(null);
  const [analysisReport, setAnalysisReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleButtonClick = () => {
    inputRef.current?.click();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch('http://localhost:5000/upload', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    setRawResult(JSON.stringify(data, null, 2));
    setLcncStructure(data.lcnc_structure);
    setAnalysisReport(data.analysis_report);
    setLoading(false);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f8fafc 0%, #e0e7ff 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ background: '#fff', borderRadius: 16, boxShadow: '0 4px 24px rgba(0,0,0,0.08)', padding: 40, width: 400, maxWidth: '90vw', textAlign: 'center' }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 24, color: '#3730a3' }}>Upload HTML File</h1>
        <form onSubmit={handleSubmit}>
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            style={{
              border: dragActive ? '2px solid #6366f1' : '2px dashed #a5b4fc',
              borderRadius: 12,
              padding: 32,
              marginBottom: 20,
              background: dragActive ? '#eef2ff' : '#f1f5f9',
              cursor: 'pointer',
              transition: 'border 0.2s, background 0.2s',
            }}
            onClick={handleButtonClick}
          >
            <input
              type="file"
              accept=".html"
              onChange={handleFileChange}
              ref={inputRef}
              style={{ display: 'none' }}
            />
            {file ? (
              <span style={{ color: '#4f46e5', fontWeight: 500 }}>{file.name}</span>
            ) : (
              <span style={{ color: '#64748b' }}>Drag & drop your HTML file here, or <span style={{ color: '#4f46e5', textDecoration: 'underline' }}>browse</span></span>
            )}
          </div>
          <button
            type="submit"
            disabled={loading || !file}
            style={{
              background: loading || !file ? '#a5b4fc' : 'linear-gradient(90deg, #6366f1 0%, #818cf8 100%)',
              color: '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '12px 32px',
              fontWeight: 600,
              fontSize: 16,
              cursor: loading || !file ? 'not-allowed' : 'pointer',
              boxShadow: '0 2px 8px rgba(99,102,241,0.08)',
              transition: 'background 0.2s',
            }}
          >
            {loading ? 'Processing...' : 'Upload'}
          </button>
        </form>
        {rawResult && (
          <div style={{ marginTop: 32, textAlign: 'left' }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, color: '#3730a3', marginBottom: 8 }}>Result:</h2>
            <pre style={{ background: '#f3f4f6', borderRadius: 8, padding: 16, fontSize: 14, color: '#334155', overflowX: 'auto' }}>{rawResult}</pre>
          </div>
        )}

        {lcncStructure && (
          <div style={{ marginTop: 32, textAlign: 'left' }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, color: '#3730a3', marginBottom: 8 }}>LCNC Structure</h2>
            <pre style={{ background: '#f3f4f6', borderRadius: 8, padding: 16, fontSize: 14, color: '#334155', overflowX: 'auto' }}>{JSON.stringify(lcncStructure, null, 2)}</pre>
          </div>
        )}

        {analysisReport && (
          <div style={{ marginTop: 32, textAlign: 'left' }}>
            <h2 style={{ fontSize: 20, fontWeight: 600, color: '#3730a3', marginBottom: 8 }}>Analysis Report</h2>
            {Object.entries(analysisReport).map(([section, value]) => (
              <div key={section} style={{ marginBottom: 16 }}>
                <h3 style={{ fontSize: 16, fontWeight: 600, color: '#4f46e5', marginBottom: 4 }}>{section}</h3>
                {Array.isArray(value) ? (
                  value.length === 0 ? (
                    <p style={{ color: '#64748b' }}>No data</p>
                  ) : (
                    <ul style={{ listStyle: 'disc', paddingLeft: 20 }}>
                      {value.map((item, idx) => (
                        <li key={idx} style={{ marginBottom: 4 }}>
                          <pre style={{ background: '#f9fafb', borderRadius: 6, padding: 8, overflowX: 'auto' }}>{JSON.stringify(item, null, 2)}</pre>
                        </li>
                      ))}
                    </ul>
                  )
                ) : typeof value === 'object' && value !== null ? (
                  <pre style={{ background: '#f9fafb', borderRadius: 6, padding: 8, overflowX: 'auto' }}>{JSON.stringify(value, null, 2)}</pre>
                ) : (
                  <p>{String(value)}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}