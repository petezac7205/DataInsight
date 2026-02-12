import React, { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const chartExamples = {
  line:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23fff8ed'/><polyline points='15,95 70,62 125,74 180,36 245,50' fill='none' stroke='%23ef6f1f' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  scatter:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23edf8ff'/><circle cx='40' cy='84' r='8' fill='%231f5673'/><circle cx='86' cy='54' r='8' fill='%231f5673'/><circle cx='126' cy='72' r='8' fill='%231f5673'/><circle cx='178' cy='40' r='8' fill='%231f5673'/><circle cx='222' cy='64' r='8' fill='%231f5673'/></svg>",
  bar:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23effcef'/><rect x='26' y='58' width='36' height='40' fill='%2322633e'/><rect x='82' y='44' width='36' height='54' fill='%2322633e'/><rect x='138' y='28' width='36' height='70' fill='%2322633e'/><rect x='194' y='50' width='36' height='48' fill='%2322633e'/></svg>",
};

function App() {
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [dataset, setDataset] = useState([]);
  const [chartType, setChartType] = useState("line");
  const [xColumn, setXColumn] = useState("");
  const [yColumn, setYColumn] = useState("");
  const [imageUrl, setImageUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);

  const canGenerate = useMemo(
    () => dataset.length > 0 && xColumn && yColumn && chartType,
    [dataset, xColumn, yColumn, chartType]
  );

  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  const uploadFile = async (selectedFile) => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    setError("");
    setStatus("Uploading CSV...");

    try {
      const res = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error(`Upload failed (${res.status})`);
      }
      const data = await res.json();

      setColumns(data.columns || []);
      setDataset(data.data || []);
      setXColumn(data.columns?.[0] || "");
      setYColumn(data.columns?.[1] || data.columns?.[0] || "");
      setStatus(`Loaded ${selectedFile.name}`);
    } catch (err) {
      setError(err.message || "Upload failed.");
      setStatus("");
    }
  };

  const handleUpload = async () => {
    await uploadFile(file);
  };

  const handleFilePick = async (event) => {
    const selectedFile = event.target.files?.[0];
    if (!selectedFile) return;
    setFile(selectedFile);
    await uploadFile(selectedFile);
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files?.[0];
    setIsDragging(false);
    if (!droppedFile) return;
    setFile(droppedFile);
    await uploadFile(droppedFile);
  };

  const handleGenerate = async () => {
    setError("");
    setStatus("Generating plot...");

    try {
      const res = await fetch("http://127.0.0.1:8001/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          data: dataset,
          chart_type: chartType,
          x_column: xColumn,
          y_column: yColumn,
        }),
      });
      if (!res.ok) {
        throw new Error(`Plot generation failed (${res.status})`);
      }

      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setImageUrl(url);
      setStatus("Plot generated.");
    } catch (err) {
      setError(err.message || "Plot generation failed.");
      setStatus("");
    }
  };

  const assignColumn = (columnName, axis) => {
    if (axis === "x") {
      setXColumn(columnName);
      return;
    }
    setYColumn(columnName);
  };

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="kicker">DataInsight</p>
        <h1>Turn CSV data into visuals in one smooth scroll.</h1>
        <p className="subtext">
          Upload your file, map two columns, choose a chart style, and render
          the result in a single dashboard.
        </p>
      </section>

      <section className="panel panel-upload">
        <h2>1. Drop Your CSV</h2>
        <div
          className={`dropzone ${isDragging ? "dragging" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(event) => {
            if (event.key === "Enter" || event.key === " ") {
              fileInputRef.current?.click();
            }
          }}
        >
          <p className="dropzone-title">Drag and drop a CSV file here</p>
          <p className="dropzone-subtitle">or click to browse files</p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleFilePick}
            className="hidden-input"
          />
          {file && <p className="file-chip">{file.name}</p>}
        </div>
        <button className="action-btn" onClick={handleUpload} disabled={!file}>
          Upload CSV
        </button>
      </section>

      {columns.length > 0 && (
        <section className="panel">
          <h2>2. Pick Columns</h2>
          <p className="panel-note">Click any column to set X and Y axes.</p>
          <div className="column-row">
            {columns.map((columnName) => (
              <div className="column-chip" key={columnName}>
                <span>{columnName}</span>
                <div className="chip-actions">
                  <button
                    className={`chip-btn ${xColumn === columnName ? "active-x" : ""}`}
                    onClick={() => assignColumn(columnName, "x")}
                  >
                    Set X
                  </button>
                  <button
                    className={`chip-btn ${yColumn === columnName ? "active-y" : ""}`}
                    onClick={() => assignColumn(columnName, "y")}
                  >
                    Set Y
                  </button>
                </div>
              </div>
            ))}
          </div>
          <div className="selected-columns">
            <span>
              <strong>X:</strong> {xColumn || "Not selected"}
            </span>
            <span>
              <strong>Y:</strong> {yColumn || "Not selected"}
            </span>
          </div>
        </section>
      )}

      {columns.length > 0 && (
        <section className="panel">
          <h2>3. Choose Chart Type</h2>
          <div className="chart-grid">
            {Object.entries(chartExamples).map(([type, preview]) => (
              <button
                key={type}
                className={`chart-card ${chartType === type ? "selected" : ""}`}
                onClick={() => setChartType(type)}
              >
                <img src={preview} alt={`${type} chart example`} />
                <span>{type[0].toUpperCase() + type.slice(1)}</span>
              </button>
            ))}
          </div>
          <button
            className="action-btn generate-btn"
            onClick={handleGenerate}
            disabled={!canGenerate}
          >
            Generate Plot
          </button>
        </section>
      )}

      <section className="panel">
        <h2>4. Plot Output</h2>
        <div className="plot-frame">
          {imageUrl ? (
            <img src={imageUrl} alt="Generated plot" className="plot-image" />
          ) : (
            <p className="plot-placeholder">
              Your generated chart will appear in this framed area.
            </p>
          )}
        </div>
        {(status || error) && (
          <div className="status-wrap">
            {status && <p className="status success">{status}</p>}
            {error && <p className="status error">{error}</p>}
          </div>
        )}
      </section>

      <section className="spacer">
        <div>
          <h3>Built for quick exploratory analysis</h3>
          <p>Upload, map, generate, compare. Repeat with another CSV.</p>
        </div>
      </section>
    </main>
  );
}

export default App;
