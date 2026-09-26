import { Activity, Check } from 'lucide-react';

export default function ResearchReplay({ data }) {
  const names = [
    ['google_search', 'Google Search'],
    ['google_news', 'Google News'],
    ['google_jobs', 'Google Jobs'],
    ['google_maps', 'Google Maps'],
    ['google_shopping', 'Google Shopping'],
    ['google_scholar', 'Google Scholar'],
  ];

  const stats = data?.research_stats || {};

  const count = Object.values(data || {})
    .filter(
      (value) =>
        value &&
        typeof value === 'object' &&
        Array.isArray(value.results)
    )
    .reduce((total, value) => total + value.results.length, 0);

  const signalCount =
    data?.signals && typeof data.signals === 'object'
      ? Object.keys(data.signals).length
      : 0;

  const opportunityCount = Array.isArray(data?.opportunities)
    ? data.opportunities.length
    : 0;

  return (
    <section className="panel replay-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">Collection trace</div>
          <h2>Research replay</h2>
        </div>

        <Activity size={17} className="subtle-icon" />
      </div>

      <div className="replay-stats">
        <div>
          <small>Queries executed</small>
          <b>{stats.total_queries ?? '—'}</b>
        </div>

        <div>
          <small>Records returned</small>
          <b>{stats.total_results ?? count}</b>
        </div>

        <div>
          <small>Signals generated</small>
          <b>{signalCount}</b>
        </div>

        <div>
          <small>Opportunities found</small>
          <b>{opportunityCount}</b>
        </div>
      </div>

      <div className="query-list">
        {names.map(([key, label]) => {
          const queryCount =
            data?.[key]?.queries_executed ?? 0;

          return (
            <div key={key}>
              <span>
                <Check size={13} />
                {label}
              </span>

              <b>{queryCount} queries</b>
            </div>
          );
        })}
      </div>

      <p className="disclaimer">
        This replay reflects the research run returned by the backend:
        source queries → collected records → market signals →
        opportunity candidates.
      </p>
    </section>
  );
}