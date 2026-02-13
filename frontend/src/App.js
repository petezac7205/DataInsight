import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const chartExamples = {
  line:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23fff8ed'/><polyline points='15,95 70,62 125,74 180,36 245,50' fill='none' stroke='%23ef6f1f' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/></svg>",
  scatter:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23edf8ff'/><circle cx='40' cy='84' r='8' fill='%231f5673'/><circle cx='86' cy='54' r='8' fill='%231f5673'/><circle cx='126' cy='72' r='8' fill='%231f5673'/><circle cx='178' cy='40' r='8' fill='%231f5673'/><circle cx='222' cy='64' r='8' fill='%231f5673'/></svg>",
  bar:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23effcef'/><rect x='26' y='58' width='36' height='40' fill='%2322633e'/><rect x='82' y='44' width='36' height='54' fill='%2322633e'/><rect x='138' y='28' width='36' height='70' fill='%2322633e'/><rect x='194' y='50' width='36' height='48' fill='%2322633e'/></svg>",
  histogram:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23fff8ed'/><rect x='24' y='60' width='22' height='38' fill='%23ef6f1f'/><rect x='52' y='45' width='22' height='53' fill='%23ef6f1f'/><rect x='80' y='30' width='22' height='68' fill='%23ef6f1f'/><rect x='108' y='18' width='22' height='80' fill='%23ef6f1f'/><rect x='136' y='35' width='22' height='63' fill='%23ef6f1f'/><rect x='164' y='52' width='22' height='46' fill='%23ef6f1f'/><rect x='192' y='67' width='22' height='31' fill='%23ef6f1f'/></svg>",
  box:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23edf8ff'/><line x1='44' y1='18' x2='44' y2='100' stroke='%231f5673' stroke-width='3'/><rect x='24' y='44' width='40' height='36' fill='%23b7d6e8' stroke='%231f5673' stroke-width='3'/><line x1='24' y1='62' x2='64' y2='62' stroke='%231f5673' stroke-width='3'/><line x1='128' y1='24' x2='128' y2='96' stroke='%231f5673' stroke-width='3'/><rect x='108' y='40' width='40' height='32' fill='%23b7d6e8' stroke='%231f5673' stroke-width='3'/><line x1='108' y1='56' x2='148' y2='56' stroke='%231f5673' stroke-width='3'/></svg>",
  heatmap:
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='120'><rect width='260' height='120' fill='%23effcef'/><rect x='42' y='22' width='36' height='26' fill='%23f8d3bf'/><rect x='80' y='22' width='36' height='26' fill='%23f2a57f'/><rect x='118' y='22' width='36' height='26' fill='%23ea7a4f'/><rect x='42' y='50' width='36' height='26' fill='%23b8d8c0'/><rect x='80' y='50' width='36' height='26' fill='%237ab08a'/><rect x='118' y='50' width='36' height='26' fill='%234b8a61'/><rect x='42' y='78' width='36' height='20' fill='%23d8e7dd'/><rect x='80' y='78' width='36' height='20' fill='%23a9cbb4'/><rect x='118' y='78' width='36' height='20' fill='%2378ad8a'/></svg>",
};

function App() {
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [previewRows, setPreviewRows] = useState([]);
  const [rowCount, setRowCount] = useState(0);
  const [stats, setStats] = useState(null);
  const [chartType, setChartType] = useState("line");
  const [xColumn, setXColumn] = useState("");
  const [yColumn, setYColumn] = useState("");
  const [colorColumn, setColorColumn] = useState("");
  const [aggregation, setAggregation] = useState("");
  const [plotSpec, setPlotSpec] = useState(null);
  const [plotInsights, setPlotInsights] = useState("");
  const [columnStats, setColumnStats] = useState(null);
  const [insights, setInsights] = useState("");
  const [question, setQuestion] = useState("");
  const [queryResult, setQueryResult] = useState(null);
  const [plotlyReady, setPlotlyReady] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const fileInputRef = useRef(null);
  const plotRef = useRef(null);

  const insightLines = useMemo(() => {
    if (Array.isArray(insights)) {
      return insights.map((item) => String(item).trim()).filter(Boolean);
    }
    if (typeof insights === "string") {
      return insights
        .split(/\r?\n/)
        .map((line) => line.replace(/^[\s\-*•]+/, "").trim())
        .filter(Boolean);
    }
    return [];
  }, [insights]);

  const plotInsightLines = useMemo(() => {
    if (Array.isArray(plotInsights)) {
      return plotInsights.map((item) => String(item).trim()).filter(Boolean);
    }
    if (typeof plotInsights === "string") {
      return plotInsights
        .split(/\r?\n/)
        .map((line) => line.replace(/^[\s\-*â€¢]+/, "").trim())
        .filter(Boolean);
    }
    return [];
  }, [plotInsights]);

  const canGenerate = useMemo(() => {
    if (!columns.length) return false;
    if (chartType === "heatmap") return true;
    if (chartType === "histogram") return Boolean(xColumn);
    return Boolean(xColumn && yColumn && chartType);
  }, [columns.length, xColumn, yColumn, chartType]);

  useEffect(() => {
    const scriptId = "plotly-cdn-script";
    const existing = document.getElementById(scriptId);
    if (existing) {
      setPlotlyReady(Boolean(window.Plotly));
      return;
    }

    const script = document.createElement("script");
    script.id = scriptId;
    script.src = "https://cdn.plot.ly/plotly-2.35.2.min.js";
    script.async = true;
    script.onload = () => setPlotlyReady(Boolean(window.Plotly));
    script.onerror = () => {
      setError("Plotly failed to load. Check network access and refresh.");
      setPlotlyReady(false);
    };
    document.body.appendChild(script);
  }, []);

  useEffect(() => {
    if (!plotRef.current || !plotSpec || !plotlyReady || !window.Plotly) return;
    const nextLayout = {
      autosize: true,
      margin: { l: 56, r: 24, t: 48, b: 56 },
      ...((plotSpec && plotSpec.layout) || {}),
    };

    window.Plotly.newPlot(plotRef.current, plotSpec.data || [], nextLayout, {
      responsive: true,
      displayModeBar: true,
    });

    // Ensure Plotly recalculates after the container settles in layout.
    setTimeout(() => {
      if (plotRef.current && window.Plotly) {
        window.Plotly.Plots.resize(plotRef.current);
      }
    }, 0);
  }, [plotSpec, plotlyReady]);


  const fetchDatasetStats = useCallback(async () => {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error(`Stats failed (${res.status})`);
    const data = await res.json();
    setStats(data);
  }, []);

  const fetchColumnStats = useCallback(async (columnName) => {
    if (!columnName) {
      setColumnStats(null);
      return;
    }
    const res = await fetch(`${API_BASE}/column-stats?column=${encodeURIComponent(columnName)}`);
    if (!res.ok) throw new Error(`Column stats failed (${res.status})`);
    const data = await res.json();
    setColumnStats(data);
  }, []);

  const fetchOverviewInsights = useCallback(async () => {
    setError("");
    setStatus("Generating AI overview insights...");
    try {
      const res = await fetch(`${API_BASE}/ai/overview-insights`);
      if (!res.ok) throw new Error(`Insights failed (${res.status})`);
      const data = await res.json();
      setInsights(data.insights ?? "");
      setStatus("AI insights ready.");
    } catch (err) {
      setError(err.message || "AI insights failed.");
      setStatus("");
    }
  }, []);

  useEffect(() => {
    if (!xColumn) return;
    fetchColumnStats(xColumn).catch(() => {
      setColumnStats(null);
    });
  }, [xColumn, fetchColumnStats]);

  const uploadFile = async (selectedFile) => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    setError("");
    setStatus("Uploading CSV...");

    try {
      const res = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        throw new Error(`Upload failed (${res.status})`);
      }
      const data = await res.json();

      setColumns(data.columns || []);
      setPreviewRows(data.preview || []);
      setRowCount(data.row_count || 0);
      setXColumn(data.columns?.[0] || "");
      setYColumn(data.columns?.[1] || data.columns?.[0] || "");
      setColorColumn("");
      setAggregation("");
      setPlotSpec(null);
      setPlotInsights("");
      setInsights([]);
      setQueryResult(null);

      await fetchDatasetStats();
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
      const payload = {
        chart_type: chartType,
      };
      if (xColumn) payload.x = xColumn;
      if (yColumn) payload.y = yColumn;
      if (colorColumn) payload.color = colorColumn;
      if (aggregation) payload.aggregation = aggregation;

      const res = await fetch(`${API_BASE}/plot`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        throw new Error(`Plot generation failed (${res.status})`);
      }

      const data = await res.json();
      setPlotSpec(data.plot || null);
      setPlotInsights(data.insights ?? "");
      setStatus("Plot generated.");
    } catch (err) {
      setError(err.message || "Plot generation failed.");
      setStatus("");
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setError("");
    setStatus("Running AI query...");
    try {
      const res = await fetch(`${API_BASE}/ai/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: question.trim() }),
      });
      if (!res.ok) throw new Error(`AI query failed (${res.status})`);
      const data = await res.json();
      setQueryResult(data);
      setStatus("AI query complete.");
    } catch (err) {
      setError(err.message || "AI query failed.");
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
          <div className="selected-columns">
            <label className="field-line">
              Aggregation:
              <select
                className="field-input"
                value={aggregation}
                onChange={(event) => setAggregation(event.target.value)}
              >
                <option value="">None</option>
                <option value="sum">sum</option>
                <option value="mean">mean</option>
                <option value="count">count</option>
                <option value="min">min</option>
                <option value="max">max</option>
                <option value="median">median</option>
              </select>
            </label>
            <label className="field-line">
              Color:
              <select
                className="field-input"
                value={colorColumn}
                onChange={(event) => setColorColumn(event.target.value)}
              >
                <option value="">None</option>
                {columns.map((columnName) => (
                  <option key={columnName} value={columnName}>
                    {columnName}
                  </option>
                ))}
              </select>
            </label>
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
          {plotSpec ? (
            <div ref={plotRef} className="plot-image" />
          ) : (
            <p className="plot-placeholder">
              Your generated chart will appear in this framed area.
            </p>
          )}
        </div>
        {!!plotInsightLines.length && (
          <div className="stats-single">
            <h3>Plot Insights</h3>
            <div className="insights-container">
              {plotInsightLines.map((line, index) => (
                <div key={`${line}-${index}`} className="insight-card">
                  {line}
                </div>
              ))}
            </div>
          </div>
        )}
        {(status || error) && (
          <div className="status-wrap">
            {status && <p className="status success">{status}</p>}
            {error && <p className="status error">{error}</p>}
          </div>
        )}
      </section>

      {columns.length > 0 && (
        <section className="panel">
          <h2>5. Dataset Overview</h2>
          <p className="panel-note">
            Rows: <strong>{rowCount}</strong> | Columns: <strong>{columns.length}</strong>
          </p>
          {stats && (
            <div className="stats-grid">
              
              {/* Data Types */}
              <div>
                <h3>Data Types</h3>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.dtypes).map(([col, type]) => (
                      <tr key={col}>
                        <td>{col}</td>
                        <td>{type}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Null Counts */}
              <div>
                <h3>Null Counts</h3>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Null Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(stats.null_counts).map(([col, count]) => (
                      <tr key={col}>
                        <td>{col}</td>
                        <td>{count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

            </div>
          )}
          {columnStats && (
            <div className="stats-single">
              <h3>Column Stats ({xColumn})</h3>

              <div className="stats-list">
                {Object.entries(columnStats).map(([key, value]) => (
                  <div key={key} className="stat-row">
                    <span className="stat-name">{key.toUpperCase()}</span>
                    <span className="stat-value">
                      {typeof value === "number" ? value.toFixed(3) : value}
                    </span>
                  </div>
                ))}
              </div>

            </div>
          )}
          {!!previewRows.length && (
            <div className="stats-single">
              <h3>Preview (first 5 rows)</h3>
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      {columns.map((col) => (
                        <th key={col}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewRows.map((row, i) => (
                      <tr key={i}>
                        {columns.map((col) => (
                          <td key={col}>{row[col] ?? "—"}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </section>
      )}

      {columns.length > 0 && (
        <section className="panel">
          <h2>6. AI Insights and Query</h2>
          <button className="action-btn" onClick={fetchOverviewInsights}>
            Generate Overview Insights
          </button>
          {!!insightLines.length && (
            <div className="stats-single">
              <h3>Insights</h3>
              <div className="insights-container">
                {insightLines.map((line, index) => (
                  <div key={index} className="insight-card">
                    {line}
                  </div>
                ))}
              </div>
            </div>
          )}
          <div className="query-row">
            <input
              className="field-input"
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question about the CSV..."
            />
            <button className="action-btn" onClick={handleAsk}>
              Ask
            </button>
          </div>
          {queryResult && (
            <div className="stats-single">
              <h3>Query Result</h3>
                
                {/* Structured Query */}
                <div className="query-structured">
                  <h4>Applied Filters</h4>  

                  {queryResult.structured_query?.filters?.length ? (
                    <div className="filter-chips">
                      {queryResult.structured_query.filters.map((f, i) => (
                        <div key={i} className="filter-chip">
                          {f.column} {f.operator} {String(f.value)}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>No filters applied</p>
                  )}

                  <p className="aggregation-line">
                    Aggregation:{" "}
                    <strong>
                      {queryResult.structured_query?.aggregation?.toUpperCase()}
                    </strong>{" "}
                    on column{" "}
                    <strong>{queryResult.structured_query?.column}</strong>
                  </p>
                </div>

                {/* Final Answer */}
                <div className="query-answer">
                  <p>Final Answer</p>
                  <h3>
                    {typeof queryResult.answer === "number"
                      ? queryResult.answer.toFixed(3)
                      : queryResult.answer}
                  </h3>
                </div>
            </div>
          )}
        </section>
      )}

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
