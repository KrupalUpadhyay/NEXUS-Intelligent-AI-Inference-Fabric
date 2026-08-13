import { FormEvent, StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Decision = { inference_id: string; output: string; cached: boolean; latency_ms: number; estimated_cost_usd: number; quality_score: number; routing: { selected_backend: string; confidence: number; reason: string[] } };
type Metrics = { total_requests: number; cache_hits: number; average_latency_ms: number; total_cost_usd: number; recent_decisions: Decision[] };
type Model = { name: string; provider: string; is_local: boolean };
type Page = "Overview" | "Live Requests" | "Inference Graph" | "Backend Health" | "Orion Decisions" | "Analytics" | "Cache" | "Settings";
const pages: Page[] = ["Overview", "Live Requests", "Inference Graph", "Backend Health", "Orion Decisions", "Analytics", "Cache", "Settings"];
const blankMetrics: Metrics = { total_requests: 0, cache_hits: 0, average_latency_ms: 0, total_cost_usd: 0, recent_decisions: [] };

function DecisionRows({ decisions }: { decisions: Decision[] }) {
  return <>{decisions.length === 0 ? <p className="empty">No completed requests yet. Run an inference from Orion Decisions.</p> : decisions.slice(0, 10).map((event, index) => <div className="event" key={`${event.inference_id}-${index}`}><i className={event.cached ? "cached" : ""}/><b>{event.routing.selected_backend}</b><span>{event.cached ? "Cache hit" : `${event.latency_ms}ms`}</span></div>)}</>;
}

function App() {
  const [activePage, setActivePage] = useState<Page>("Overview");
  const [metrics, setMetrics] = useState<Metrics>(blankMetrics);
  const [models, setModels] = useState<Model[]>([]);
  const [prompt, setPrompt] = useState("Explain why semantic caching makes AI systems faster.");
  const [task, setTask] = useState("reasoning");
  const [backend, setBackend] = useState("auto");
  const [priority, setPriority] = useState(7);
  const [queueLength, setQueueLength] = useState(4);
  const [result, setResult] = useState<Decision | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const refreshMetrics = () => fetch("/api/v1/metrics").then(r => r.json()).then(setMetrics).catch(() => undefined);

  useEffect(() => {
    refreshMetrics();
    fetch("/api/v1/models").then(r => r.json()).then(setModels).catch(() => setError("API is unavailable. Start NEXUS using: python run.py"));
    const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/v1/live`);
    ws.onmessage = ({ data }) => { const message = JSON.parse(data); if (message.type === "snapshot") setMetrics(message.metrics); if (message.type === "inference_completed") refreshMetrics(); };
    return () => ws.close();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      const payload: Record<string, unknown> = { prompt, task_type: task, max_tokens: 256, user_priority: priority, metadata: { queue_length: String(queueLength) } };
      if (backend !== "auto") payload.preferred_backend = backend;
      const response = await fetch("/api/v1/infer", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const body = await response.json(); if (!response.ok) throw new Error(body.detail ?? "Inference failed");
      setResult(body); refreshMetrics();
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Inference failed"); }
    finally { setBusy(false); }
  }

  const cards = [["Requests", metrics.total_requests], ["Cache hit rate", metrics.total_requests ? `${Math.round(metrics.cache_hits / metrics.total_requests * 100)}%` : "0%"], ["Avg latency", `${metrics.average_latency_ms.toFixed(0)}ms`], ["Tracked cost", `$${metrics.total_cost_usd.toFixed(4)}`]];
  const metricsCards = <section className="metrics">{cards.map(([label, value]) => <article className="metric" key={String(label)}><small>{label}</small><strong>{value}</strong><em>Live telemetry</em></article>)}</section>;
  const graph = <article className="panel flow"><div className="panel-title"><h2>Request lifecycle</h2><span>Live architecture</span></div><div className="path">{["Gateway", "Semantic cache", "Orion", "Adapter", "Response"].map((node, i) => <div className="flow-node" key={node}><b>0{i + 1}</b>{node}{i < 4 && <i className="particle" />}</div>)}</div></article>;
  const catalog = <article className="panel"><div className="panel-title"><h2>Backend catalog</h2><span>{models.length} configured</span></div>{models.map(model => <div className="backend" key={model.name}><i /><div><b>{model.name}</b><small>{model.provider}{model.is_local ? " · optional local" : " · simulated"}</small></div><span>{model.is_local ? "Optional" : "Ready"}</span></div>)}</article>;
  const inferenceForm = <article className="panel request"><div className="panel-title"><h2>Submit inference</h2><span>Interactive control</span></div><form onSubmit={submit}><label>Prompt<textarea value={prompt} onChange={e => setPrompt(e.target.value)} /></label><div className="form-row"><label>Task<select value={task} onChange={e => setTask(e.target.value)}>{["chat", "summarization", "reasoning", "translation", "code", "ocr", "embeddings"].map(t => <option key={t}>{t}</option>)}</select></label><label>Route via<select value={backend} onChange={e => setBackend(e.target.value)}><option value="auto">Orion auto-route</option>{models.filter(model => !model.is_local).map(model => <option value={model.name} key={model.name}>{model.name}</option>)}</select></label><label>Priority: {priority}<input type="range" min="0" max="10" value={priority} onChange={e => setPriority(Number(e.target.value))} /></label><label>Queue length: {queueLength}<input type="range" min="0" max="80" value={queueLength} onChange={e => setQueueLength(Number(e.target.value))} /></label></div><button disabled={busy}>{busy ? "Routing…" : "Run inference"}</button></form>{error && <p className="error">{error}</p>}{result && <div className="decision"><b>{result.cached ? "Semantic cache hit" : result.routing.selected_backend}</b><span>{Math.round(result.routing.confidence * 100)}% confidence · {result.latency_ms}ms · ${result.estimated_cost_usd} · quality {result.quality_score}</span><small>{result.routing.reason[0]}</small><pre>{result.output}</pre></div>}</article>;

  let pageContent: JSX.Element;
  if (activePage === "Overview") pageContent = <><p className="page-caption">NEXUS routes each inference using cache state, Orion, and backend availability.</p>{metricsCards}<section className="grid">{graph}{catalog}</section><section className="overview-inference">{inferenceForm}</section></>;
  else if (activePage === "Live Requests") pageContent = <article className="panel wide"><div className="panel-title"><h2>Live request stream</h2><span>{metrics.recent_decisions.length} events</span></div><DecisionRows decisions={metrics.recent_decisions}/></article>;
  else if (activePage === "Inference Graph") pageContent = <><p className="page-caption">Every request follows this path; a cache hit exits early before model execution.</p>{graph}</>;
  else if (activePage === "Backend Health") pageContent = <><p className="page-caption">Configured providers and their current demo readiness.</p>{catalog}</>;
  else if (activePage === "Orion Decisions") pageContent = <><p className="page-caption">Leave Route via on Orion auto-route to use the learned policy.</p>{inferenceForm}</>;
  else if (activePage === "Analytics") pageContent = <><p className="page-caption">Aggregate telemetry accumulated in this running session.</p>{metricsCards}<article className="panel wide"><h2>Recent routing activity</h2><DecisionRows decisions={metrics.recent_decisions}/></article></>;
  else if (activePage === "Cache") pageContent = <article className="panel wide"><div className="panel-title"><h2>Semantic cache</h2><span>{metrics.cache_hits} hits</span></div><p className="page-caption">Repeat the same prompt from Orion Decisions to demonstrate a cache hit. Cached requests return immediately and do not incur simulated cost.</p>{result ? <div className="decision"><b>{result.cached ? "Latest request was a cache hit" : "Latest request was a cache miss"}</b><span>{result.cached ? "Reuse saved output on the next matching request." : "Run the same request again to populate and hit cache."}</span></div> : <p className="empty">No request has been made in this session.</p>}</article>;
  else pageContent = <article className="panel wide"><h2>Routing settings</h2><p className="page-caption">The active demo policy is Orion with simulated backends. Use the Route via selector on Orion Decisions to override it for a request.</p><div className="backend"><i/><div><b>Default policy</b><small>Orion learned routing policy</small></div><span>Enabled</span></div><div className="backend"><i/><div><b>Semantic cache</b><small>In-memory local cache for this no-Docker demo</small></div><span>Enabled</span></div></article>;

  return <main className="app-shell"><aside><div className="brand"><span>N</span> NEXUS</div><p>Inference fabric</p><small>Dashboard v2 · multi-page</small>{pages.map(page => <button className={activePage === page ? "nav active" : "nav"} key={page} onClick={() => { setActivePage(page); window.scrollTo({ top: 0, behavior: "smooth" }); }}>{page}</button>)}</aside><section className="content"><header><div><p className="eyebrow">NEXUS CONTROL PLANE</p><h1>{activePage}</h1></div><span className="online"><i /> System operational</span></header>{pageContent}</section></main>;
}
createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
