import {
  Activity,
  BriefcaseBusiness,
  Cpu,
  Factory,
  MapPinned,
  Search,
} from 'lucide-react';

const ITEMS = [
  ['google_search', 'Search activity', Search],
  ['google_jobs', 'Hiring signals', BriefcaseBusiness],
  ['google_news', 'News activity', Activity],
  ['google_scholar', 'Research activity', Cpu],
  ['google_shopping', 'Product activity', Factory],
  ['google_maps', 'Supplier discovery', MapPinned],
];

const ALIASES = {
  google_search: 'search',
  google_jobs: 'jobs',
  google_news: 'news',
  google_scholar: 'scholar',
  google_shopping: 'shopping',
  google_maps: 'maps',
};

export default function MarketPulse({ data, mock }) {
  return (
    <section className="section market-pulse-section">
      <div className="section-heading">
        <div>
          <div className="eyebrow">Signal coverage</div>
          <h2>Market pulse</h2>
        </div>

        <span className="source-caption">
          {mock ? 'Development sample' : 'Observed results by source'}
        </span>
      </div>

      <div className="pulse-grid">
        {ITEMS.map(([key, name, Icon]) => {
          const source = data?.[key] || data?.[ALIASES[key]];
          const results = Array.isArray(source?.results)
            ? source.results
            : [];

          return (
            <article className="pulse-card" key={key}>
              <div className="pulse-top">
                <span className="icon-box">
                  <Icon size={17} />
                </span>
                <span className="live-dot" />
              </div>

              <div className="pulse-count">{results.length}</div>
              <div className="pulse-label">{name}</div>

              <div className="pulse-foot">
                {results.length
                  ? 'results collected'
                  : 'No results returned'}
              </div>
            </article>
          );
        })}
      </div>

      <p className="disclaimer">
        Counts reflect returned records. These are coverage measures, not
        market scores or validated demand estimates.
      </p>
    </section>
  );
}