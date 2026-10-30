import { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import "./App.css";

const API_URL = "https://bug-predict-platform.onrender.com/";

function riskColor(label) {
  if (label === "high") return "#f85149";
  if (label === "medium") return "#d29922";
  return "#3fb950";
}

function scoreColor(score) {
  if (score >= 75) return "#3fb950";
  if (score >= 50) return "#d29922";
  return "#f85149";
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
      setResult(await res.json());
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
    } catch (e) {}
  };

  const sendDecision = async (decision) => {
    setDeciding(true);
    setError("");
    const filesToFix =
      decision === "suggest_fix"
        ? result.file_metrics
            .filter((f) => f.bug_risk_label !== "low" && selectedFiles[f.file_path])
            .map((f) => ({ file_path: f.file_path, issue: "High predicted bug risk — refactor and add safety checks" }))
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
      setResult(await res.json());
    } catch (e) {
      setError(e.message || "Decision failed");
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
    <div className="gh-app">
      <nav className="gh-nav">
        <div className="gh-nav-left">
          <svg height="32" viewBox="0 0 16 16" width="32" fill="#f0f6fc">
            <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A8.012 8.012 0 0 1 0 8c0-4.42 3.58-8 8-8Z"/>
          </svg>
          <span className="gh-brand">AI Code Quality</span>
        </div>
        <div className="gh-nav-right">
          <span className="gh-pill">ML + LLM powered</span>
        </div>
      </nav>

      <div className="gh-container">
        <div className="gh-toolbar">
          <input className="gh-input" placeholder="owner" value={owner} onChange={(e) => setOwner(e.target.value)} />
          <span className="gh-slash">/</span>
          <input className="gh-input" placeholder="repository" value={repo} onChange={(e) => setRepo(e.target.value)} />
          <span className="gh-at">@</span>
          <input className="gh-input gh-input-branch" placeholder="main" value={branch} onChange={(e) => setBranch(e.target.value)} />
          <button className="gh-btn gh-btn-primary" onClick={runScan} disabled={loading}>
            {loading ? "Scanning…" : "Scan repository"}
          </button>
          <button className="gh-btn" onClick={fetchLatest} disabled={loading}>↻ Refresh</button>
        </div>

        {error && <div className="gh-flash gh-flash-error">⚠ {error}</div>}
        {loading && <div className="gh-progress"><div className="gh-progress-bar" /></div>}
        
{!result && !loading && (
  <section className="gh-welcome">
    <div className="gh-welcome-icon">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3 4.5 7v5c0 4.5 3.2 7.5 7.5 9 4.3-1.5 7.5-4.5 7.5-9V7L12 3Z" />
        <path d="m9 12 2 2 4-4" />
      </svg>
    </div>

    <h1>Know your code a little better.</h1>

    <p className="gh-welcome-description">
      Review repository quality, spot files with higher predicted bug risk,
      and check security findings — all in one place.
    </p>

    <div className="gh-welcome-steps">
      <div className="gh-welcome-step">
        <span className="gh-step-number">1</span>
        <div>
          <strong>Choose a repository</strong>
          <p>Enter the GitHub owner, repository name, and branch above.</p>
        </div>
      </div>

      <div className="gh-welcome-step">
        <span className="gh-step-number">2</span>
        <div>
          <strong>Run the scan</strong>
          <p>Let the existing analysis process inspect the code.</p>
        </div>
      </div>

      <div className="gh-welcome-step">
        <span className="gh-step-number">3</span>
        <div>
          <strong>Review the findings</strong>
          <p>Explore risk scores, affected files, and security findings.</p>
        </div>
      </div>
    </div>

    <p className="gh-welcome-note">
      Start with a repository you have permission to analyze.
    </p>
  </section>
)}


        {result && (
          <>
            <div className="gh-summary-bar">
              <div className="gh-summary-item">
                <span className="gh-summary-num" style={{ color: scoreColor(result.overall_quality_score) }}>
                  {result.overall_quality_score}
                </span>
                <span className="gh-summary-label">quality score</span>
              </div>
              <div className="gh-summary-divider" />
              <div className="gh-summary-item">
                <span className="gh-summary-num">{result.file_metrics.length}</span>
                <span className="gh-summary-label">files analyzed</span>
              </div>
              <div className="gh-summary-divider" />
              <div className="gh-summary-item">
                <span className="gh-summary-num" style={{ color: result.file_metrics.filter(f => f.bug_risk_label === "high").length ? "#f85149" : "#3fb950" }}>
                  {result.file_metrics.filter((f) => f.bug_risk_label === "high").length}
                </span>
                <span className="gh-summary-label">high risk</span>
              </div>
              <div className="gh-summary-divider" />
              <div className="gh-summary-item">
                <span className="gh-summary-num" style={{ color: result.security_issues.length ? "#f85149" : "#3fb950" }}>
                  {result.security_issues.length}
                </span>
                <span className="gh-summary-label">security findings</span>
              </div>
            </div>

            <div className="gh-card">
              <div className="gh-card-header">
                <span>Review decision</span>
                <span className={`gh-status-badge gh-status-${result.decision}`}>{result.decision}</span>
              </div>
              <div className="gh-card-body">
                {result.fix_branch && (
                  <div className="gh-branch-pill">
                    <svg height="14" viewBox="0 0 16 16" fill="#8b949e"><path d="M11.75 2.5a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm-2.25.75a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V7.231c-.483.657-1.034 1.158-1.615 1.52-.7.436-1.44.633-2.025.732v2.117a2.25 2.25 0 1 1-1.5 0V4.372a2.25 2.25 0 1 1 1.5 0v2.097c.372-.09.898-.25 1.408-.566.564-.351 1.145-.954 1.405-1.955A2.25 2.25 0 0 1 9.5 3.25Zm-6 .122a.75.75 0 1 0 1.5 0 .75.75 0 0 0-1.5 0ZM4.25 12a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Zm8.25.75a.75.75 0 1 0 0 1.5.75.75 0 0 0 0-1.5Z"/></svg>
                    <code>{result.fix_branch}</code>
                  </div>
                )}
                <div className="gh-btn-row">
                  <button className="gh-btn gh-btn-danger" onClick={() => sendDecision("reject")} disabled={deciding}>Reject</button>
                  <button className="gh-btn gh-btn-success" onClick={() => sendDecision("approve")} disabled={deciding}>Approve</button>
                  <button className="gh-btn gh-btn-warning" onClick={() => sendDecision("suggest_fix")} disabled={deciding}>
                    {deciding ? "Generating fix…" : "Suggest fix & approve"}
                  </button>
                </div>
              </div>
            </div>

            <div className="gh-card">
              <div className="gh-card-header">Select files for AI repair</div>
              <div className="gh-file-list">
                {result.file_metrics.filter((f) => f.bug_risk_label !== "low").map((f, i) => (
                  <label key={i} className="gh-file-row">
                    <input type="checkbox" checked={!!selectedFiles[f.file_path]} onChange={() => toggleFile(f.file_path)} />
                    <svg height="16" viewBox="0 0 16 16" fill="#8b949e"><path d="M2 1.75C2 .784 2.784 0 3.75 0h6.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v9.586A1.75 1.75 0 0 1 13.25 16h-9.5A1.75 1.75 0 0 1 2 14.25Z"/></svg>
                    <span className="gh-file-path">{f.file_path}</span>
                    <span className="gh-risk-tag" style={{ color: riskColor(f.bug_risk_label), borderColor: riskColor(f.bug_risk_label) }}>
                      {(f.bug_risk_score * 100).toFixed(0)}% risk
                    </span>
                  </label>
                ))}
                {result.file_metrics.filter((f) => f.bug_risk_label !== "low").length === 0 && (
                  <div className="gh-empty">No flagged files — nothing to fix here.</div>
                )}
              </div>
            </div>

            {result.fix_diffs && result.fix_diffs.length > 0 && (
              <div className="gh-card">
                <div className="gh-card-header">AI-generated patches</div>
                {result.fix_diffs.map((d, i) => (
                  <div key={i} className="gh-diff-block">
                    <div className="gh-diff-header">{d.file_path}</div>
                    <pre className="gh-diff-code">{d.fixed}</pre>
                  </div>
                ))}
              </div>
            )}

            <div className="gh-card">
              <div className="gh-card-header">Bug risk by file</div>
              <div className="gh-card-body">
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={chartData}>
                    <XAxis dataKey="short" angle={-30} textAnchor="end" height={70} tick={{ fontSize: 11, fill: "#8b949e" }} />
                    <YAxis domain={[0, 1]} tick={{ fill: "#8b949e" }} />
                    <Tooltip contentStyle={{ background: "#161b22", border: "1px solid #30363d", borderRadius: 6 }} formatter={(v) => v.toFixed(2)} />
                    <Bar dataKey="bug_risk_score" radius={[4, 4, 0, 0]}>
                      {chartData?.map((f, i) => <Cell key={i} fill={riskColor(f.bug_risk_label)} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="gh-card">
              <div className="gh-card-header">Security findings ({result.security_issues.length})</div>
              <div className="gh-file-list">
                {result.security_issues.length === 0 ? (
                  <div className="gh-empty">✓ No security issues found</div>
                ) : (
                  result.security_issues.map((s, i) => (
                    <div key={i} className="gh-issue-row">
                      <span className={`gh-sev-badge gh-sev-${s.severity.toLowerCase()}`}>{s.severity}</span>
                      <span className="gh-issue-path">{s.file_path}:{s.line}</span>
                      <span className="gh-issue-text">{s.issue}</span>
                      <span className="gh-issue-source">{s.source}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
