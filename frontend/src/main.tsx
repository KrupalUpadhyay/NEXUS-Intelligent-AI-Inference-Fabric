import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const phases = ["Gateway", "Cache", "Orion", "Backends", "Analytics"];

function App() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">INTELLIGENT AI INFERENCE FABRIC</p>
        <h1>NEXUS</h1>
        <p className="lede">The control plane for every inference decision.</p>
        <span className="status"><i /> Gateway online</span>
      </section>
      <section className="fabric" aria-label="Inference fabric roadmap">
        {phases.map((phase, index) => (
          <div className={index === 0 ? "node active" : "node"} key={phase}>
            <span>0{index + 1}</span>
            {phase}
          </div>
        ))}
      </section>
      <p className="footnote">Phase 1 · API foundation connected · Orion policy training begins in Phase 7</p>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode><App /></StrictMode>,
);
