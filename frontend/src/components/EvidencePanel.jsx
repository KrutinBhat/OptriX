import { ExternalLink, FileText } from 'lucide-react';

function getSource(data, selected) {
  if (!selected) {
    return null;
  }

  const aliases = {
    google_search: 'search',
    google_jobs: 'jobs',
    google_news: 'news',
    google_maps: 'maps',
    google_shopping: 'shopping',
    google_scholar: 'scholar',
  };

  return data?.[selected] || data?.[aliases[selected]];
}

function getTitle(record) {
  return (
    record?.title ||
    record?.name ||
    record?.business_name ||
    record?.company_name ||
    record?.position ||
    record?.job_title ||
    'Untitled result'
  );
}

export default function EvidencePanel({ data, selected }) {
  const source = getSource(data, selected);

  const results = Array.isArray(source?.results)
    ? source.results
    : [];

  const label = selected
    ?.replace('google_', '')
    ?.replaceAll('_', ' ');

  return (
    <div className="evidence-panel">
      <div className="evidence-panel-head">
        <div>
          <div className="eyebrow">Selected evidence</div>

          <h3>
            {label
              ? label.charAt(0).toUpperCase() + label.slice(1)
              : 'Choose a source'}
          </h3>
        </div>

        <span className="tag muted">
          {results.length} records
        </span>
      </div>

      {results.length === 0 ? (
        <div className="empty-evidence">
          <FileText size={20} />

          <p>
            No records were returned for this source.
          </p>
        </div>
      ) : (
        <div className="evidence-list">
          {results.slice(0, 6).map((record, index) => {
            const href = record?.link || record?.url;

            return (
              <article
                className="evidence-item"
                key={href || getTitle(record) || index}
              >
                <strong>{getTitle(record)}</strong>

                <p>
                  {record?.snippet ||
                    record?.description ||
                    record?.location ||
                    record?.address ||
                    'Record returned by the research API.'}
                </p>

                {href && (
                  <a
                    href={href}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View source
                    <ExternalLink size={12} />
                  </a>
                )}
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}