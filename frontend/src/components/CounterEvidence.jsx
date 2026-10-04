function evidenceText(item, fallback) {
  if (typeof item === 'string') {
    return item;
  }

  return (
    item?.title ||
    item?.snippet ||
    item?.description ||
    item?.text ||
    fallback
  );
}

export default function CounterEvidence({ opportunity }) {
  const supporting = Array.isArray(opportunity?.supporting_evidence)
    ? opportunity.supporting_evidence
    : Array.isArray(opportunity?.supporting)
      ? opportunity.supporting
      : [];

  const counter = Array.isArray(opportunity?.counter_evidence)
    ? opportunity.counter_evidence
    : Array.isArray(opportunity?.counter)
      ? opportunity.counter
      : [];

  const renderColumn = (items, type, title, emptyText) => (
    <div className={`evidence-column ${type}`}>
      <h4>
        <i />
        {title}
      </h4>

      {items.length > 0 ? (
        items.map((item, index) => (
          <div className="evidence-item" key={index}>
            <p>
              {evidenceText(
                item,
                type === 'support'
                  ? 'Supporting evidence identified by the research engine.'
                  : 'Counter-evidence identified by the research engine.',
              )}
            </p>

            {item &&
              typeof item === 'object' &&
              item.signal && (
                <small>
                  Signal:{' '}
                  {String(item.signal).replaceAll('_', ' ')}
                </small>
              )}
          </div>
        ))
      ) : (
        <p className="empty-evidence">{emptyText}</p>
      )}
    </div>
  );

  return (
    <div className="evidence-columns">
      {renderColumn(
        supporting,
        'support',
        'Supporting evidence',
        'No supporting evidence was attached to this opportunity.',
      )}

      {renderColumn(
        counter,
        'counter',
        'Counter-evidence',
        'No counter-evidence was generated for this research run yet.',
      )}
    </div>
  );
}