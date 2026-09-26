import { useState } from 'react';
import { ArrowLeft, MapPin } from 'lucide-react';
import EvidenceGraph from '../components/EvidenceGraph.jsx';
import EvidencePanel from '../components/EvidencePanel.jsx';
import CounterEvidence from '../components/CounterEvidence.jsx';

export default function OpportunityDetails({
  opportunity,
  data,
  mock,
  onBack,
}) {
  const [selected, setSelected] = useState('google_search');

  const breakdown = opportunity?.score_breakdown || {};

  const indicators = [
    ['Demand', breakdown.demand?.score],
    ['Supply gap', breakdown.supply_gap?.score],
    ['Momentum', breakdown.momentum?.score],
    ['Technology', breakdown.technology?.score],
    ['Competition', breakdown.competition?.score],
    ['Geographic gap', breakdown.geographic_gap?.score],
  ];

  const supportingEvidence = Array.isArray(opportunity?.supporting_evidence)
    ? opportunity.supporting_evidence
    : [];

  const counterEvidence = Array.isArray(opportunity?.counter_evidence)
    ? opportunity.counter_evidence
    : [];

  const score =
    typeof opportunity?.score === 'number'
      ? Math.round(opportunity.score)
      : null;

  return (
    <main className="results-page details-page">
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={15} />
        Back to research
      </button>

      <div className="detail-hero">
        <span className="tag">Potential opportunity</span>

        <div className="detail-title-row">
          <div>
            <h1>{opportunity?.title || 'Opportunity candidate'}</h1>

            <p>
              {opportunity?.description ||
                'A market pattern identified from the collected evidence.'}
            </p>
          </div>

          {score !== null && (
            <div className="detail-score">
              <strong>{score}</strong>
              <span>/100</span>
            </div>
          )}
        </div>

        <span className="detail-location">
          <MapPin size={14} />
          {data?.location || 'Location not specified'}
        </span>

        {mock && (
          <div className="micro-note">
            Development example · not a validated market finding
          </div>
        )}
      </div>

      <div className="detail-grid">
        <section className="panel detail-section">
          <div className="eyebrow">Why it appeared</div>

          <h2>Signals worth examining</h2>

          <p>
            This hypothesis is generated from the market signals returned by
            the research engine. Each signal contributes evidence to the
            assessment rather than acting as a standalone decision.
          </p>

          <div className="indicator-row">
            {indicators.map(([label, value]) => (
              <div className="indicator" key={label}>
                <span>{label}</span>
                <b>
                  {typeof value === 'number'
                    ? Math.round(value)
                    : '—'}
                </b>
              </div>
            ))}
          </div>

          <div className="detail-evidence-summary">
            <div>
              <strong>{supportingEvidence.length}</strong>
              <span>Supporting evidence</span>
            </div>

            <div>
              <strong>{counterEvidence.length}</strong>
              <span>Counter-evidence</span>
            </div>
          </div>
        </section>

        <section className="panel detail-section">
          <div className="eyebrow">Geographic context</div>

          <h2>{data?.location || 'Location'}</h2>

          <p>
            Geographic scope comes directly from the research request.
            Location-related evidence can be explored through the Maps source
            in the evidence explorer.
          </p>

          <div className="detail-source-list">
            <span>Search</span>
            <span>News</span>
            <span>Jobs</span>
            <span>Maps</span>
            <span>Shopping</span>
            <span>Scholar</span>
          </div>
        </section>
      </div>

      <section className="section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">Balanced assessment</div>
            <h2>Supporting & counter-evidence</h2>
          </div>
        </div>

        <CounterEvidence opportunity={opportunity} />
      </section>

      <section className="section">
        <div className="section-heading">
          <div>
            <div className="eyebrow">Source records</div>
            <h2>Evidence behind this hypothesis</h2>
          </div>
        </div>

        <div className="panel evidence-layout">
          <EvidenceGraph
            data={data}
            selected={selected}
            onSelect={setSelected}
          />

          <EvidencePanel
            data={data}
            selected={selected}
          />
        </div>
      </section>

      <section className="panel detail-section">
        <div className="eyebrow">Scoring transparency</div>

        <h2>How the score was calculated</h2>

        {score !== null ? (
          <>
            <p>
              The opportunity score is calculated from the signal values
              returned by the backend. Positive market signals increase the
              score, while competition and counter-evidence reduce it.
            </p>

            <div className="score-breakdown">
              {Object.entries(breakdown).map(([name, item]) => {
                if (!item || typeof item !== 'object') {
                  return null;
                }

                const label = name
                  .replaceAll('_', ' ')
                  .replace(/\b\w/g, (char) => char.toUpperCase());

                const itemScore =
                  typeof item.score === 'number'
                    ? Math.round(item.score)
                    : null;

                return (
                  <div className="score-row" key={name}>
                    <div>
                      <span>{label}</span>
                      <small>
                        Weight: {item.weight ?? '—'}
                        {item.effect ? ` · ${item.effect}` : ''}
                      </small>
                    </div>

                    <strong>
                      {itemScore !== null ? itemScore : '—'}
                    </strong>
                  </div>
                );
              })}
            </div>
          </>
        ) : (
          <p>
            No score was returned for this opportunity. The detail page will
            show the calculation once the backend provides scoring data.
          </p>
        )}
      </section>
    </main>
  );
}