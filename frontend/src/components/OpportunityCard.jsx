import { ArrowUpRight, ChevronRight } from 'lucide-react';

export default function OpportunityCard({ opportunity, onExplore, mock }) {
  const breakdown = opportunity?.score_breakdown || {};

  const indicators = [
    ['Demand', breakdown.demand?.score],
    ['Supply gap', breakdown.supply_gap?.score],
    ['Momentum', breakdown.momentum?.score],
    ['Technology', breakdown.technology?.score],
    ['Competition', breakdown.competition?.score],
    ['Geographic gap', breakdown.geographic_gap?.score],
  ];

  const supportingCount = Array.isArray(opportunity?.supporting_evidence)
    ? opportunity.supporting_evidence.length
    : 0;

  const counterCount = Array.isArray(opportunity?.counter_evidence)
    ? opportunity.counter_evidence.length
    : 0;

  const score =
    typeof opportunity?.score === 'number'
      ? Math.round(opportunity.score)
      : null;

  return (
    <article className="opportunity-card">
      <div className="opp-card-top">
        <span className="tag">Research hypothesis</span>

        <span className="opp-arrow">
          <ArrowUpRight size={17} />
        </span>
      </div>

      <div className="opportunity-title-row">
        <div>
          <h3>{opportunity?.title || 'Opportunity candidate'}</h3>
          <p>
            {opportunity?.description ||
              'A market pattern identified from the collected evidence.'}
          </p>
        </div>

        {score !== null && (
          <div className="opportunity-score">
            <strong>{score}</strong>
            <span>/100</span>
          </div>
        )}
      </div>

      <div className="indicator-row">
        {indicators.map(([name, value]) => (
          <div className="indicator" key={name}>
            <span>{name}</span>
            <b>{typeof value === 'number' ? Math.round(value) : '—'}</b>
          </div>
        ))}
      </div>

      <div className="evidence-counts">
        <span>
          <i className="support-dot" />
          {supportingCount} supporting points
        </span>

        <span>
          <i className="counter-dot" />
          {counterCount} counterpoints
        </span>
      </div>

      <button className="text-button" onClick={onExplore}>
        Explore opportunity
        <ChevronRight size={16} />
      </button>

      {mock && (
        <div className="micro-note">
          Development example · not a live backend opportunity
        </div>
      )}
    </article>
  );
}