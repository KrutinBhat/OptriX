import { useState } from 'react';
import { ArrowLeft, Clock3, Database, MapPin } from 'lucide-react';
import MarketPulse from '../components/MarketPulse.jsx';
import MarketTrend from '../components/MarketTrend.jsx';
import OpportunityCard from '../components/OpportunityCard.jsx';
import EvidenceGraph from '../components/EvidenceGraph.jsx';
import EvidencePanel from '../components/EvidencePanel.jsx';
import CounterEvidence from '../components/CounterEvidence.jsx';
import EntityExplorer from '../components/EntityExplorer.jsx';
import ResearchReplay from '../components/ResearchReplay.jsx';
export default function Results({data,mock,opportunity,onBack,onExplore}) {
  const [selected,setSelected]=useState('google_news');
  const topic=data.topic||'Research topic', location=data.location||'Location';
  return <main className="results-page"><button className="back-link" onClick={onBack}><ArrowLeft size={15}/> New research</button><div className="results-head"><div><div className="eyebrow">Research results</div><h1>{topic}</h1><div className="meta-row"><span><MapPin size={14}/>{location}</span><span><Clock3 size={14}/>{new Date().toLocaleString(undefined,{dateStyle:'medium',timeStyle:'short'})}</span></div></div><span className={`status-pill ${mock?'sample':''}`}><i/>{mock?'Development sample':'Collection complete'}</span></div>
  {mock&&<div className="sample-banner"><Database size={15}/><span><b>Development data shown.</b> The API response did not contain structured opportunity or scoring data. Source counts below reflect the sample payload.</span></div>}
  <MarketPulse data={data} mock={mock}/><div className="two-column"><MarketTrend mock={mock}/><section className="panel signal-summary"><div className="eyebrow">Signal interpretation</div><h2>Evidence before scores</h2><p>The current backend collects source records. It does not yet return validated demand, supply gap, momentum or competition scores.</p><div className="summary-note"><span className="note-bar"/>No market score is inferred from result counts.</div></section></div>
  <section className="section opportunity-section"><div className="section-heading"><div><div className="eyebrow">Evidence-led hypotheses</div><h2>Opportunity discovery</h2></div><span className="source-caption">Potential opportunities · review both sides</span></div><OpportunityCard opportunity={opportunity} onExplore={onExplore} mock={mock}/></section>
  <section className="section"><div className="section-heading"><div><div className="eyebrow">Source relationships</div><h2>Evidence graph</h2></div></div><div className="panel evidence-layout"><EvidenceGraph data={data} selected={selected} onSelect={setSelected}/><EvidencePanel data={data} selected={selected}/></div></section>
  <section className="section"><div className="section-heading"><div><div className="eyebrow">Balanced assessment</div><h2>Supporting & counter-evidence</h2></div></div><CounterEvidence opportunity={opportunity}/></section><div className="lower-grid"><EntityExplorer data={data}/><ResearchReplay data={data}/></div></main>;
}
