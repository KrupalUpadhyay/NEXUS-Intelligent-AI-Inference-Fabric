import { FormEvent, StrictMode, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Decision = { inference_id: string; cached: boolean; latency_ms: number; estimated_cost_usd: number; routing: { selected_backend: string; confidence: number; reason: string[] } };
type Metrics = { total_requests: number; cache_hits: number; average_latency_ms: number; total_cost_usd: number; recent_decisions: Decision[] };
const emptyMetrics: Metrics = { total_requests: 0, cache_hits: 0, average_latency_ms: 0, total_cost_usd: 0, recent_decisions: [] };

function App() {
  const [metrics, setMetrics] = useState<Metrics>(emptyMetrics);
  const [models, setModels] = useState<{name: string; provider: string; is_local: boolean}[]>([]);
  const [prompt, setPrompt] = useState("Explain why semantic caching makes AI systems faster.");
  const [task, setTask] = useState("reasoning");
  const [result, setResult] = useState<Decision | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    fetch("/api/v1/metrics").then(r => r.json()).then(setMetrics).catch(() => undefined);
    fetch("/api/v1/models").then(r => r.json()).then(setModels).catch(() => undefined);
    const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/api/v1/live`);
    ws.onmessage = ({ data }) => {
      const message = JSON.parse(data);
      if (message.type === "snapshot") setMetrics(message.metrics);
      if (message.type === "inference_completed") setMetrics(current => ({ ...current, total_requests: current.total_requests + 1, recent_decisions: [message.inference, ...current.recent_decisions].slice(0, 8) }));
    };
    return () => ws.close();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true);
    try {
      const response = await fetch("/api/v1/infer", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prompt, task_type: task, max_tokens: 256, metadata: { queue_length: "4" } }) });
      const body = await response.json(); setResult(body);
    } finally { setBusy(false); }
  }

  const cards = [["Requests", metrics.total_requests], ["Cache hit rate", metrics.total_requests ? `${Math.round(metrics.cache_hits / metrics.total_requests * 100)}%` : "0%"], ["Avg latency", `${metrics.average_latency_ms.toFixed(0)}ms`], ["Tracked cost", `$${metrics.total_cost_usd.toFixed(4)}`]];
  return <main className="app-shell">
    <aside><div className="brand"><span>N</span> NEXUS</div><p>Inference fabric</p>{["Overview", "Live requests", "Inference graph", "Backend health", "Orion decisions", "Analytics", "Cache", "Settings"].map((item, index) => <button className={index === 0 ? "nav active" : "nav"} key={item}>{item}</button>)}</aside>
    <section className="content"><header><div><p className="eyebrow">CONTROL PLANE / LIVE</p><h1>Inference Overview</h1></div><span className="online"><i /> System operational</span></header>
      <section className="metrics">{cards.map(([label, value]) => <article className="metric" key={String(label)}><small>{label}</small><strong>{value}</strong><em>Live telemetry</em></article>)}</section>
      <section className="grid"><article className="panel flow"><div className="panel-title"><h2>Live inference path</h2><span>Animated</span></div><div className="path">{["Gateway", "Semantic cache", "Orion", "Adapter", "Response"].map((node, i) => <div className="flow-node" key={node}><b>0{i + 1}</b>{node}{i < 4 && <i className="particle" />}</div>)}</div></article>
        <article className="panel"><div className="panel-title"><h2>Backend health</h2><span>{models.length} configured</span></div>{models.map(model => <div className="backend" key={model.name}><i /><div><b>{model.name}</b><small>{model.provider}{model.is_local ? " · local" : " · simulated"}</small></div><span>Ready</span></div>)}</article></section>
      <section className="grid lower"><article className="panel request"><div className="panel-title"><h2>Submit inference</h2><span>Try Orion</span></div><form onSubmit={submit}><textarea value={prompt} onChange={e => setPrompt(e.target.value)} /><select value={task} onChange={e => setTask(e.target.value)}>{["chat", "summarization", "reasoning", "translation", "code", "ocr", "embeddings"].map(t => <option key={t}>{t}</option>)}</select><button disabled={busy}>{busy ? "Routing…" : "Run inference"}</button></form>{result && <div className="decision"><b>{result.routing.selected_backend}</b><span>{Math.round(result.routing.confidence * 100)}% confidence · {result.latency_ms}ms · ${result.estimated_cost_usd}</span><small>{result.routing.reason[0]}</small></div>}</article>
      <article className="panel"><div className="panel-title"><h2>Recent decisions</h2><span>{metrics.recent_decisions.length} events</span></div>{metrics.recent_decisions.slice(0, 5).map((event, index) => <div className="event" key={`${event.inference_id}-${index}`}><i className={event.cached ? "cached" : ""}/><b>{event.routing.selected_backend}</b><span>{event.cached ? "Cache hit" : `${event.latency_ms}ms`}</span></div>)}</article></section>
    </section>
  </main>;
}
createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
