import {
  Search,
  BriefcaseBusiness,
  Newspaper,
  MapPinned,
  ShoppingBag,
  GraduationCap,
} from 'lucide-react';

const nodes = [
  ['google_search', 'Search', Search],
  ['google_jobs', 'Jobs', BriefcaseBusiness],
  ['google_news', 'News', Newspaper],
  ['google_maps', 'Maps', MapPinned],
  ['google_shopping', 'Shopping', ShoppingBag],
  ['google_scholar', 'Scholar', GraduationCap],
];

export default function EvidenceGraph({ data, selected, onSelect }) {
  return (
    <div className="evidence-graph">
      <div className="graph-core">
        <span className="core-mark">O</span>
        <b>{data?.topic || 'Research topic'}</b>
        <small>evidence links</small>
      </div>

      <div className="graph-nodes">
        {nodes.map(([key, label, Icon]) => {
          const results = Array.isArray(data?.[key]?.results)
            ? data[key].results
            : [];

          return (
            <button
              className={`graph-node ${
                selected === key ? 'selected' : ''
              }`}
              key={key}
              onClick={() => onSelect(key)}
            >
              <span className="node-icon">
                <Icon size={16} />
              </span>

              <b>{label}</b>

              <small>
                {results.length} records
              </small>
            </button>
          );
        })}
      </div>
    </div>
  );
}