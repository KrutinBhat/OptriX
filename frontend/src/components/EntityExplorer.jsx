import { useMemo, useState } from 'react';

const groups = [
  ['Companies', 'google_search'],
  ['Products', 'google_shopping'],
  ['Research papers', 'google_scholar'],
  ['Job roles', 'google_jobs'],
  ['Locations', 'google_maps'],
];

export default function EntityExplorer({ data }) {
  const [filter, setFilter] = useState('All');

  const list = useMemo(() => {
    return groups.flatMap(([type, key]) => {
      const rows = data?.[key]?.results;

      if (!Array.isArray(rows)) {
        return [];
      }

      return rows.map((row) => {
        const title =
          row?.business_name ||
          row?.company_name ||
          row?.title ||
          row?.name ||
          row?.position ||
          row?.job_title ||
          'Untitled record';

        const detail =
          row?.address ||
          row?.location ||
          row?.snippet ||
          row?.description ||
          row?.category ||
          '';

        return {
          type,
          title: String(title),
          detail: String(detail),
        };
      });
    });
  }, [data]);

  const shown =
    filter === 'All'
      ? list
      : list.filter((entity) => entity.type === filter);

  return (
    <section className="panel entity-panel">
      <div className="section-heading">
        <div>
          <div className="eyebrow">Entities & organizations</div>
          <h2>Entity explorer</h2>
        </div>

        <span className="tag muted">
          {list.length} found
        </span>
      </div>

      <div className="filter-row">
        <button
          className={filter === 'All' ? 'active' : ''}
          onClick={() => setFilter('All')}
        >
          All
        </button>

        {groups.map(([group]) => (
          <button
            className={filter === group ? 'active' : ''}
            key={group}
            onClick={() => setFilter(group)}
          >
            {group}
          </button>
        ))}
      </div>

      <div className="entity-list">
        {shown.length > 0 ? (
          shown.slice(0, 10).map((entity, index) => {
            const initial =
              entity.title.trim().charAt(0).toUpperCase() || '?';

            return (
              <div
                className="entity-row"
                key={`${entity.type}-${entity.title}-${index}`}
              >
                <span className="entity-initial">
                  {initial}
                </span>

                <div>
                  <b>{entity.title}</b>

                  <small>
                    {entity.type}
                    {entity.detail
                      ? ` · ${entity.detail}`
                      : ''}
                  </small>
                </div>

                <span className="tag muted">
                  Observed
                </span>
              </div>
            );
          })
        ) : (
          <div className="empty-evidence">
            No entities in this category yet.
          </div>
        )}
      </div>
    </section>
  );
}