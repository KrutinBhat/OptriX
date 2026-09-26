export default function CounterEvidence({ opportunity }) {
  const supporting = Array.isArray(opportunity?.supporting_evidence)
    ? opportunity.supporting_evidence
    : [];

  const counter = Array.isArray(opportunity?.counter_evidence)
    ? opportunity.counter_evidence
    : [];

  return (
    <div className="evidence-columns">
      <div className="evidence-column support">
        <h4>
          <i />
          Supporting evidence
        </h4>

        {supporting.length > 0 ? (
          supporting.map((item, index) => (
            <div className="evidence-item" key={index}>
              <p>
                {typeof item === 'string'
                  ? item
                  : item.title ||
                    item.snippet ||
                    item.description ||
                    item.text ||
                    'Supporting evidence identified by the research engine.'}
              </p>

              {item.signal && (
                <small>
                  Signal: {item.signal.replaceAll('_', ' ')}
                </small>
              )}
            </div>
          ))
        ) : (
          <p className="empty-evidence">
            No supporting evidence was attached to this opportunity.
          </p>
        )}
      </div>

      <div className="evidence-column counter">
        <h4>
          <i />
          Counter-evidence
        </h4>

        {counter.length > 0 ? (
          counter.map((item, index) => (
            <div className="evidence-item" key={index}>
              <p>
                {typeof item === 'string'
                  ? item
                  : item.title ||
                    item.snippet ||
                    item.description ||
                    item.text ||
                    'Counter-evidence identified by the research engine.'}
              </p>

              {item.signal && (
                <small>
                  Signal: {item.signal.replaceAll('_', ' ')}
                </small>
              )}
            </div>
          ))
        ) : (
          <p className="empty-evidence">
            No counter-evidence was generated for this research run yet.
          </p>
        )}
      </div>
    </div>
  );
}