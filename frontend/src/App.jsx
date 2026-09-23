import { useState } from 'react';
import { Activity, Bell, ChevronDown, CircleHelp, Menu } from 'lucide-react';
import Home from './pages/Home.jsx';
import Results from './pages/Results.jsx';
import OpportunityDetails from './pages/OpportunityDetails.jsx';
import { runResearch } from './services/api.js';
import { mockResearch, exampleOpportunity } from './data/mockResearch.js';

export default function App() {
  const [view,setView]=useState('home'); const [data,setData]=useState(null); const [mock,setMock]=useState(false);
  const [loading,setLoading]=useState(false); const [error,setError]=useState('');
  const [opportunity,setOpportunity]=useState(exampleOpportunity);
  async function research(input) {
    setError(''); setLoading(true);
    try {
      const response=await runResearch(input);
      if (response && typeof response==='object' && Object.keys(response).length) {
        setData(response); setMock(false);
        const candidate=Array.isArray(response.opportunities)?response.opportunities[0]:null;
        if(candidate) setOpportunity({...exampleOpportunity,...candidate,indicators:candidate.indicators||exampleOpportunity.indicators,supporting:candidate.supporting||[],counter:candidate.counter||[]});
        else setOpportunity({title:`${input.topic} — areas to investigate`,description:'The backend returned source material but no structured opportunity hypotheses. Review the records to develop and validate an assessment.',indicators:[['Demand','Not scored'],['Supply gap','Not scored'],['Tech activity','Not scored'],['Competition','Not scored']],supporting:['No structured opportunity assessment was returned by the backend.'],counter:['Counter-evidence was not returned as structured data by the backend.']});
      } else { setData({...mockResearch,...input}); setMock(true); setOpportunity(exampleOpportunity); }
      setView('results');
    } catch (e) {
      setError(e.message || 'Unable to connect to the research engine. Please make sure the backend is running.');
    } finally { setLoading(false); }
  }
  const back=()=>setView('results');
  const showDemo=()=>{setData(mockResearch);setMock(true);setOpportunity(exampleOpportunity);setView('results');};
  return <div className="app-shell"><header className="topbar"><a className="brand" href="#" onClick={e=>{e.preventDefault();setView('home')}}><span className="brand-mark"><Activity size={19}/></span><span>Opportunity<span className="brand-light">OS</span><small>MARKET INTELLIGENCE</small></span></a><nav><button className={`nav-item ${view==='home'?'current':''}`} onClick={()=>setView('home')}>Research</button><button className={`nav-item ${view!=='home'?'current':''}`} onClick={()=>data&&setView('results')}>Workspace</button></nav><div className="top-actions"><span className="connection"><i/> Research engine</span><button className="icon-button" aria-label="Help"><CircleHelp size={17}/></button><button className="icon-button" aria-label="Notifications"><Bell size={17}/></button><button className="profile-button"><span>OS</span><ChevronDown size={13}/></button><button className="mobile-menu" aria-label="Menu"><Menu/></button></div></header>{view==='home'?<Home onSubmit={research} loading={loading} error={error} onDemo={showDemo}/>:view==='detail'?<OpportunityDetails opportunity={opportunity} data={data} mock={mock} onBack={back}/>:<Results data={data} mock={mock} opportunity={opportunity} onBack={()=>setView('home')} onExplore={()=>setView('detail')}/>}<footer className="footer"><span>OPPORTUNITYOS <b>·</b> MARKET SIGNALS, WITH SOURCES</span><span>Evidence informs decisions. It does not guarantee outcomes.</span></footer></div>;
}
