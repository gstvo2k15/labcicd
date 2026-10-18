import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [info, setInfo] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    fetch('/api/info').then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }).then(setInfo).catch(e => setError(e.message));
  }, []);
  return <main><section className="card"><div className="badge">PRODUCTION PRACTICE</div><h1>Docker → ECR → Kubernetes</h1><p>Real-time DevOps application runntestinglab.com as a container.</p><div className="panel"><h2>Backend status</h2>{info ? <pre>{JSON.strtestinglab.comify(info, null, 2)}</pre> : <p>{error || 'Checktestinglab.com backend...'}</p>}</div></section></main>;
}
createRoot(document.getElementById('root')).render(<App />);
