import { ArrowUpRight, MapPin, Search, SlidersHorizontal } from 'lucide-react';
export default function SearchForm({ onSubmit, loading, initialTopic = '', initialLocation = '' }) {
  return <form className="search-form" onSubmit={e => { e.preventDefault(); const data = new FormData(e.currentTarget); onSubmit({ topic: data.get('topic'), location: data.get('location') }); }}>
    <label className="field"><span>Topic / industry</span><div className="field-input"><Search size={17}/><input name="topic" placeholder="e.g. Drone components" defaultValue={initialTopic} required minLength="1"/></div></label>
    <label className="field"><span>Location</span><div className="field-input"><MapPin size={17}/><input name="location" placeholder="Country, region or city" defaultValue={initialLocation} required minLength="1"/></div></label>
    <label className="field field-depth"><span>Research depth</span><div className="field-input"><SlidersHorizontal size={17}/><select defaultValue="deep"><option value="focused">Focused scan</option><option value="deep">Deep research</option></select></div></label>
    <button className="primary-button" disabled={loading}>{loading ? <><span className="spinner"/> Researching</> : <>Run research <ArrowUpRight size={17}/></>}</button>
  </form>;
}
