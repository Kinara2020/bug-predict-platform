import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import "./App.css";

const API_URL = "http://localhost:8000";

function riskColor(label) {
  if (label === "high") return "#e74c3c";
  if (label === "medium") return "#f39c12";
  return "#2ecc71";
}

function scoreColor(score) {
  if (score >= 75) return "#2ecc71";
  if (score >= 50) return "#f39c12";
  return "#e74c3c";
}

export default function App() {
  const [owner, setOwner] = useState("");
  const [repo, setRepo] = useState("");
  const [branch, setBranch] = useState("main");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [deciding, setDeciding] = useState(false);
  const [error, setError] = useState("");
  const [selectedFiles, setSelectedFiles] = useState({});

  const toggleFile = (path) => {
    setSelectedFiles((prev) => ({ ...prev, [path]: !prev[path] }));
  };

  const runScan = async () => {
    if (!owner || !repo) {
      setError("Enter both owner and repo");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    setSelectedFiles({});
    try {
      const res = await fetch(`${API_URL}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ owner, repo, branch }),
      });
      if (!res.ok) throw new Error("Scan failed — check backend logs");
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchLatest = async () => {
    if (!owner || !repo) return;
    try {
      const res = await fetch(`${API_URL}/latest?owner=${owner}&repo=${repo}`);
      if (res.ok) setResult(await res.json());
    } catch (e) {
      // silent
    }
  };

  const sendDecision = async (decision) => {
    setDeciding(true);
    setError("");
    const filesToFix =
      decision === "suggest_fix"
        ? result.file_metrics
            .filter((f) => f.bug_risk_label !== "low" && selectedFiles[f.file_path])
            .map((f) => ({
              file_path: f.file_path,
              issue: "High predicted bug risk — refactor and add safety checks",
            }))
        : [];
    if (decision === "suggest_fix" && filesToFix.length === 0) {
      setError("Select at least one file to fix before approving.");
      setDeciding(false);
      return;
    }
    try {
      const res = await fetch(`${API_URL}/decision`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ owner, repo, branch, decision, files_to_fix: filesToFix }),
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Decision failed");
      }
      const data = await res.json();
      setResult(data);
    } catch (e) {
      setError(e.message || "Decision failed — check backend logs");
    } finally {
      setDeciding(false);
    }
  };

  const chartData = result?.file_metrics
    ?.slice()
    .sort((a, b) => b.bug_risk_score - a.bug_risk_score)
    .slice(0, 12)
    .map((f) => ({ ...f, short: f.file_path.split("/").pop() }));

  return (
    <div className="app">
      <header className="header">
        <h1>🔍 AI Code Quality Platform</h1>
        <p className="subtitle">Bug prediction · Security scan · Code quality — powered by ML + LLM</p>
      </header>

      <div className="scan-bar">
        <input placeholder="owner (e.g. octocat)" value={owner} onChange={(e) => setOwner(e.target.value)} />
        <input placeholder="repo" value={repo} onChange={(e) => setRepo(e.target.value)} />
        <input placeholder="branch" value={branch} onChange={(e) => setBranch(e.target.value)} />
        <button onClick={runScan} disabled={loading}>
          {loading ? "Scanning..." : "Scan Repo"}
        </button>
        <button onClick={fetchLatest} disabled={loading}>
          Refresh Latest
        </button>
      </div>
      {error && <div className="error">{error}</div>}
      {loading && (
        <div className="loading-bar">
          <div className="loading-fill" />
        </div>
      )}

      {result && (
        <>
          <div className="score-row">
            <div className="score-card" style={{ borderColor: scoreColor(result.overall_quality_score) }}>
              <div className="score-num" style={{ color: scoreColor(result.overall_quality_score) }}>
                {result.overall_quality_score}
              </div>
              <div className="score-label">Overall Quality Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-num">{result.file_metrics.length}</div>
              <div className="stat-label">Files Analyzed</div>
            </div>
            <div className="stat-card">
              <div className="stat-num" style={{ color: "#e74c3c" }}>
                {result.file_metrics.filter((f) => f.bug_risk_label === "high").length}
              </div>
              <div className="stat-label">High-Risk Files</div>
            </div>
            <div className="stat-card">
              <div className="stat-num" style={{ color: "#e74c3c" }}>{result.security_issues.length}</div>
              <div className="stat-label">Security Issues</div>
            </div>
          </div>

          <section className="panel">
            <h2>Decision</h2>
            <p style={{ color: "#9aa0ac", fontSize: 13 }}>
              Status: <b>{result.decision}</b>
            </p>
            {result.fix_branch && (
              <p style={{ fontSize: 13 }}>
                Fix pushed to branch: <code>{result.fix_branch}</code>
              </p>
            )}
            <div style={{ display: "flex", gap: 10, marginTop: 10 }}>
              <button className="btn-reject" onClick={() => sendDecision("reject")} disabled={deciding}>
                Reject
              </button>
              <button className="btn-approve" onClick={() => sendDecision("approve")} disabled={deciding}>
                Approve
              </button>
              <button className="btn-fix" onClick={() => sendDecision("suggest_fix")} disabled={deciding}>
                {deciding ? "Fixing..." : "Suggest Fix & Approve"}
              </button>
            </div>
          </section>

          <section className="panel">
            <h2>Select Files to Fix</h2>
            <p style={{ color: "#9aa0ac", fontSize: 13 }}>
              Choose which flagged files the AI should repair. Unselected files stay untouched.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: 10 }}>
              {result.file_metrics
                .filter((f) => f.bug_risk_label !== "low")
                .map((f, i) => (
                  <label key={i} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
                    <input
                      type="checkbox"
                      checked={!!selectedFiles[f.file_path]}
                      onChange={() => toggleFile(f.file_path)}
                    />
                    <span style={{ fontFamily: "monospace" }}>{f.file_path}</span>
                    <span style={{ color: riskColor(f.bug_risk_label) }}>
                      ({(f.bug_risk_score * 100).toFixed(0)}% risk)
                    </span>
                  </label>
                ))}
              {result.file_metrics.filter((f) => f.bug_risk_label !== "low").length === 0 && (
                <p style={{ color: "#9aa0ac", fontSize: 13 }}>No flagged files to fix.</p>
              )}
            </div>
          </section>

          {result.fix_diffs && result.fix_diffs.length > 0 && (
            <section className="panel">
              <h2>Applied Fixes</h2>
              {result.fix_diffs.map((d, i) => (
                <div key={i} style={{ marginBottom: 12, background: "#14161d", borderRadius: 8, padding: 10 }}>
                  <div style={{ fontFamily: "monospace", fontSize: 12, color: "#9aa0ac" }}>{d.file_path}</div>
                  <pre style={{ fontSize: 11, color: "#6fe0a1", whiteSpace: "pre-wrap", maxHeight: 150, overflow: "auto" }}>
                    {d.fixed}
                  </pre>
                </div>
              ))}
            </section>
          )}

          <section className="panel">
            <h2>Bug Risk by File (top 12)</h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={chartData}>
                <XAxis dataKey="short" angle={-30} textAnchor="end" height={70} tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 1]} />
                <Tooltip formatter={(v) => v.toFixed(2)} />
                <Bar dataKey="bug_risk_score" radius={[6, 6, 0, 0]}>
                  {chartData?.map((f, i) => (
                    <Cell key={i} fill={riskColor(f.bug_risk_label)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </section>

          <section className="panel">
            <h2>🔒 Security Issues ({result.security_issues.length})</h2>
            {result.security_issues.length === 0 ? (
              <p className="empty">No issues found.</p>
            ) : (
              <div className="issue-list">
                {result.security_issues.map((s, i) => (
                  <div key={i} className={`issue-row sev-${s.severity.toLowerCase()}`}>
                    <span className="badge">{s.severity}</span>
                    <span className="issue-path">
                      {s.file_path}:{s.line}
                    </span>
                    <span className="issue-text">{s.issue}</span>
                    <span className="issue-source">{s.source}</span>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="panel">
            <h2>⚠️ High-Risk Files</h2>
            <div className="risk-grid">
              {result.file_metrics
                .filter((f) => f.bug_risk_label !== "low")
                .map((f, i) => (
                  <div key={i} className="risk-card" style={{ borderLeftColor: riskColor(f.bug_risk_label) }}>
                    <div className="risk-path">{f.file_path}</div>
                    <div className="risk-meta">
                      Risk: <b style={{ color: riskColor(f.bug_risk_label) }}>{(f.bug_risk_score * 100).toFixed(0)}%</b>
                      {" · "}Complexity: {f.cyclomatic_complexity.toFixed(1)}
                      {" · "}Maintainability: {f.maintainability_index.toFixed(0)}
                    </div>
                  </div>
                ))}
            </div>
          </section>
        </>
      )}
    </div>
  );
}