import { useState } from 'react';
import { ArrowLeft, Clock3, Database, MapPin } from 'lucide-react';

import MarketPulse from '../components/MarketPulse.jsx';
import MarketTrend from '../components/MarketTrend.jsx';
import OpportunityCard from '../components/OpportunityCard.jsx';
import EvidenceGraph from '../components/EvidenceGraph.jsx';
import EvidencePanel from '../components/EvidencePanel.jsx';
import CounterEvidence from '../components/CounterEvidence.jsx';
import EntityExplorer from '../components/EntityExplorer.jsx';
import ResearchReplay from '../components/ResearchReplay.jsx';


export default function Results({
  data,
  mock,
  opportunity,
  onBack,
  onExplore,
}) {
  const [selected, setSelected] = useState('google_news');

  const topic = data?.topic || 'Research topic';
  const location = data?.location || 'Location';

  const signals = data?.signals || {};
  const opportunities = Array.isArray(data?.opportunities)
    ? data.opportunities
    : [];

  const researchStats = data?.research_stats || {};

  const totalResults = Number(researchStats.total_results || 0);
  const totalQueries = Number(researchStats.total_queries || 0);

  return (
    <main className="results-page">

      {/* Back */}
      <button className="back-link" onClick={onBack}>
        <ArrowLeft size={15} />
        New research
      </button>


      {/* Header */}
      <div className="results-head">

        <div>
          <div className="eyebrow">Research results</div>

          <h1>{topic}</h1>

          <div className="meta-row">
            <span>
              <MapPin size={14} />
              {location}
            </span>

            <span>
              <Clock3 size={14} />
              {new Date().toLocaleString(undefined, {
                dateStyle: 'medium',
                timeStyle: 'short',
              })}
            </span>
          </div>
        </div>


        <span className={`status-pill ${mock ? 'sample' : ''}`}>
          <i />
          {mock ? 'Development sample' : 'Collection complete'}
        </span>

      </div>


      {/* Sample warning */}
      {mock && (
        <div className="sample-banner">
          <Database size={15} />

          <span>
            <b>Development data shown.</b>{' '}
            The live research engine could not be displayed, so this page
            is showing the development sample.
          </span>
        </div>
      )}


      {/* Market pulse */}
      <MarketPulse
        data={data}
        mock={mock}
      />


      {/* Market intelligence */}
      <div className="two-column">

        <MarketTrend
          mock={mock}
        />


        <section className="panel signal-summary">

          <div className="eyebrow">
            Signal interpretation
          </div>

          <h2>
            Evidence before decisions
          </h2>

          <p>
            OpportunityOS combines live signals from jobs, search,
            news, maps, shopping and research to identify patterns
            worth investigating.
          </p>


          <div className="signal-mini-grid">

            <SignalMini
              label="Demand"
              signal={signals.demand}
            />

            <SignalMini
              label="Supply gap"
              signal={signals.supply_gap}
            />

            <SignalMini
              label="Momentum"
              signal={signals.momentum}
            />

            <SignalMini
              label="Technology"
              signal={signals.technology}
            />

            <SignalMini
              label="Competition"
              signal={signals.competition}
            />

            <SignalMini
              label="Geographic gap"
              signal={signals.geographic_gap}
            />

          </div>


          <div className="summary-note">
            <span className="note-bar" />

            Scores are calculated from the collected evidence and
            are intended to support investigation, not guarantee
            an outcome.
          </div>

        </section>

      </div>


      {/* Research statistics */}
      <section className="section research-stats-section">

        <div className="section-heading">

          <div>
            <div className="eyebrow">
              Research run
            </div>

            <h2>
              Collection statistics
            </h2>
          </div>

        </div>


        <div className="stats-grid">

          <Stat
            label="Queries executed"
            value={totalQueries}
          />

          <Stat
            label="Results collected"
            value={totalResults}
          />

          <Stat
            label="Signals generated"
            value={Object.keys(signals).length}
          />

          <Stat
            label="Opportunities found"
            value={opportunities.length}
          />

        </div>

      </section>


      {/* Opportunities */}
      <section className="section opportunity-section">

        <div className="section-heading">

          <div>
            <div className="eyebrow">
              Evidence-led hypotheses
            </div>

            <h2>
              Opportunity discovery
            </h2>
          </div>

          <span className="source-caption">
            Potential opportunities · review both sides
          </span>

        </div>


        {opportunities.length > 0 ? (

          <div className="opportunity-list">

            {opportunities.map((item, index) => (

              <OpportunityCard
                key={`${item.title || 'opportunity'}-${index}`}
                opportunity={item}
                onExplore={onExplore}
                mock={mock}
              />

            ))}

          </div>

        ) : (

          <div className="panel empty-opportunities">

            <h3>
              No strong opportunity candidate detected
            </h3>

            <p>
              The collected evidence did not produce a sufficiently
              supported opportunity pattern for this research run.
              The underlying source data remains available below
              for investigation.
            </p>

          </div>

        )}

      </section>


      {/* Evidence graph */}
      <section className="section">

        <div className="section-heading">

          <div>
            <div className="eyebrow">
              Source relationships
            </div>

            <h2>
              Evidence graph
            </h2>
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


      {/* Supporting / counter evidence */}
      <section className="section">

        <div className="section-heading">

          <div>
            <div className="eyebrow">
              Balanced assessment
            </div>

            <h2>
              Supporting & counter-evidence
            </h2>
          </div>

        </div>


        <CounterEvidence
          opportunity={opportunity}
        />

      </section>


      {/* Lower intelligence tools */}
      <div className="lower-grid">

        <EntityExplorer
          data={data}
        />

        <ResearchReplay
          data={data}
        />

      </div>

    </main>
  );
}


/* --------------------------------
   Signal mini card
-------------------------------- */

function SignalMini({
  label,
  signal,
}) {
  const score =
    signal && typeof signal.score === 'number'
      ? Math.round(signal.score)
      : null;

  return (
    <div className="signal-mini">

      <span>
        {label}
      </span>

      <strong>
        {score === null ? '—' : score}
      </strong>

    </div>
  );
}


/* --------------------------------
   Research statistic
-------------------------------- */

function Stat({
  label,
  value,
}) {
  return (
    <div className="stat-card">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}