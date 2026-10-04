import { useState } from 'react';
import {
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Database,
  FileSearch,
  MapPin,
  Network,
  RefreshCw,
  Search,
  Users,
} from 'lucide-react';

import MarketPulse from '../components/MarketPulse.jsx';
import OpportunityCard from '../components/OpportunityCard.jsx';
import EvidenceGraph from '../components/EvidenceGraph.jsx';
import EvidencePanel from '../components/EvidencePanel.jsx';
import CounterEvidence from '../components/CounterEvidence.jsx';
import EntityExplorer from '../components/EntityExplorer.jsx';
import ResearchReplay from '../components/ResearchReplay.jsx';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview' },
  { id: 'signals', label: 'Signals' },
  { id: 'opportunities', label: 'Opportunities' },
  { id: 'evidence', label: 'Evidence' },
  { id: 'entities', label: 'Entities' },
  { id: 'replay', label: 'Research replay' },
];

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

  const sourceCount = Object.keys(data || {}).filter((key) =>
    [
      'search',
      'news',
      'jobs',
      'maps',
      'shopping',
      'scholar',
      'google_search',
      'google_news',
      'google_jobs',
      'google_maps',
      'google_shopping',
      'google_scholar',
    ].includes(key),
  ).length;

  const signalScores = Object.values(signals)
    .map((signal) => (
      signal && typeof signal.score === 'number'
        ? signal.score
        : null
    ))
    .filter((score) => score !== null);

  const overallSignal =
    signalScores.length > 0
      ? Math.round(
          signalScores.reduce((sum, score) => sum + score, 0) /
            signalScores.length,
        )
      : null;

  const primaryOpportunity = opportunities[0] || null;

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    });
  };

  return (
    <main className="results-page">

      {/* -------------------------------------------------
          RESULTS HEADER
      ------------------------------------------------- */}

      <header className="results-header" id="overview">

        <button
          type="button"
          className="back-link"
          onClick={onBack}
        >
          <ArrowLeft size={15} />
          New research
        </button>

        <div className="results-header-main">

          <div className="results-title-group">

            <div className="eyebrow">
              <BarChart3 size={13} />
              Research workspace
            </div>

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

              {!mock && (
                <span className="live-meta">
                  <CheckCircle2 size={14} />
                  Live research
                </span>
              )}

            </div>

          </div>

          <div className={`status-pill ${mock ? 'sample' : ''}`}>
            <i />
            {mock ? 'Development sample' : 'Collection complete'}
          </div>

        </div>

      </header>


      {/* -------------------------------------------------
          CONTEXTUAL NAVIGATION
      ------------------------------------------------- */}

      <nav className="results-nav" aria-label="Research sections">

        <div className="results-nav-inner">

          {NAV_ITEMS.map((item) => (
            <button
              type="button"
              key={item.id}
              onClick={() => scrollTo(item.id)}
            >
              {item.label}
            </button>
          ))}

        </div>

      </nav>


      {/* -------------------------------------------------
          DEVELOPMENT / API STATE
      ------------------------------------------------- */}

      {mock && (
        <div className="sample-banner">

          <Database size={15} />

          <div>
            <strong>Development data</strong>

            <span>
              This workspace is displaying a development sample.
              Live source results are not being shown in this run.
            </span>
          </div>

        </div>
      )}


      {/* -------------------------------------------------
          EXECUTIVE OVERVIEW
      ------------------------------------------------- */}

      <section className="overview-grid">

        <div className="overview-main">

          <div className="section-label">
            <span className="section-number">01</span>
            Executive overview
          </div>

          <h2>
            What did the research uncover?
          </h2>

          <p className="overview-description">
            OpportunityOS combines independent market signals to
            identify patterns worth investigating. The results below
            separate source evidence, derived signals and opportunity
            hypotheses so that conclusions remain traceable.
          </p>

          <div className="overview-metrics">

            <OverviewMetric
              label="Signal strength"
              value={
                overallSignal === null
                  ? '—'
                  : `${overallSignal}/100`
              }
              detail={
                overallSignal === null
                  ? 'Not available'
                  : getSignalLabel(overallSignal)
              }
            />

            <OverviewMetric
              label="Opportunities"
              value={opportunities.length}
              detail="Hypotheses identified"
            />

            <OverviewMetric
              label="Evidence collected"
              value={totalResults}
              detail="Source records"
            />

            <OverviewMetric
              label="Queries executed"
              value={totalQueries}
              detail="Research queries"
            />

          </div>

        </div>


        <aside className="overview-snapshot">

          <div className="snapshot-label">
            <FileSearch size={14} />
            Research snapshot
          </div>

          <div className="snapshot-row">
            <span>Market</span>
            <strong>{topic}</strong>
          </div>

          <div className="snapshot-row">
            <span>Location</span>
            <strong>{location}</strong>
          </div>

          <div className="snapshot-row">
            <span>Sources analyzed</span>
            <strong>
              {sourceCount || '—'}
            </strong>
          </div>

          <div className="snapshot-row">
            <span>Signals generated</span>
            <strong>
              {Object.keys(signals).length}
            </strong>
          </div>

          <div className="snapshot-divider" />

          <p>
            Scores describe observed market signals. They are not
            predictions or guarantees of commercial success.
          </p>

        </aside>

      </section>


      {/* -------------------------------------------------
          MARKET SIGNALS
      ------------------------------------------------- */}

      <section
        className="results-section"
        id="signals"
      >

        <SectionHeader
          number="02"
          eyebrow="Market intelligence"
          title="Market signals"
          description="Six analytical dimensions derived from the collected research."
        />

        <div className="pulse-shell">
          <MarketPulse
            data={data}
            mock={mock}
          />
        </div>

      </section>


      {/* -------------------------------------------------
          OPPORTUNITY DISCOVERY
      ------------------------------------------------- */}

      <section
        className="results-section"
        id="opportunities"
      >

        <SectionHeader
          number="03"
          eyebrow="Evidence-led hypotheses"
          title="Opportunity discovery"
          description="Potential market patterns identified from the available signals."
          action={
            opportunities.length > 0
              ? `${opportunities.length} hypotheses`
              : 'No hypotheses'
          }
        />

        {primaryOpportunity && (
          <div className="opportunity-feature">

            <div className="opportunity-feature-copy">

              <span className="feature-kicker">
                Primary hypothesis
              </span>

              <h3>
                {primaryOpportunity.title ||
                  'Opportunity identified'}
              </h3>

              <p>
                {primaryOpportunity.description ||
                  'The research engine identified a market pattern worth further investigation.'}
              </p>

              <button
                type="button"
                className="feature-action"
                onClick={onExplore}
              >
                Explore opportunity
                <ChevronRight size={16} />
              </button>

            </div>

            <div className="opportunity-feature-score">

              <span>Opportunity score</span>

              <strong>
                {typeof primaryOpportunity.score === 'number'
                  ? primaryOpportunity.score
                  : '—'}
              </strong>

              <small>
                Signal-based hypothesis
              </small>

            </div>

          </div>
        )}


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

            <Search size={18} />

            <div>
              <h3>
                No strong opportunity candidate detected
              </h3>

              <p>
                The collected evidence did not produce a
                sufficiently supported opportunity pattern.
                The underlying source data remains available
                for investigation.
              </p>
            </div>

          </div>

        )}

      </section>


      {/* -------------------------------------------------
          EVIDENCE
      ------------------------------------------------- */}

      <section
        className="results-section"
        id="evidence"
      >

        <SectionHeader
          number="04"
          eyebrow="Traceability"
          title="Evidence intelligence"
          description="Move from source relationships to the records behind each signal."
        />

        <div className="evidence-layout">

          <div className="panel evidence-graph-panel">

            <div className="panel-heading">

              <div>
                <span className="panel-kicker">
                  Source relationships
                </span>

                <h3>
                  Evidence graph
                </h3>
              </div>

              <Network size={17} />

            </div>

            <EvidenceGraph
              data={data}
              selected={selected}
              onSelect={setSelected}
            />

          </div>


          <div className="panel evidence-detail-panel">

            <div className="panel-heading">

              <div>
                <span className="panel-kicker">
                  Selected source
                </span>

                <h3>
                  Evidence records
                </h3>
              </div>

            </div>

            <EvidencePanel
              data={data}
              selected={selected}
            />

          </div>

        </div>

      </section>


      {/* -------------------------------------------------
          SUPPORTING / COUNTER EVIDENCE
      ------------------------------------------------- */}

      <section className="results-section">

        <SectionHeader
          eyebrow="Balanced assessment"
          title="Supporting & counter-evidence"
          description="Evidence should be examined from both sides before interpreting a market hypothesis."
        />

        <CounterEvidence
          opportunity={opportunity}
        />

      </section>


      {/* -------------------------------------------------
          ENTITIES
      ------------------------------------------------- */}

      <section
        className="results-section"
        id="entities"
      >

        <SectionHeader
          number="05"
          eyebrow="Market landscape"
          title="Entity explorer"
          description="Explore the organizations, products and entities surfaced during research."
        />

        <div className="panel intelligence-panel">

          <div className="panel-heading">

            <div>
              <span className="panel-kicker">
                Discovered entities
              </span>

              <h3>
                Entity landscape
              </h3>
            </div>

            <Users size={17} />

          </div>

          <EntityExplorer
            data={data}
          />

        </div>

      </section>


      {/* -------------------------------------------------
          RESEARCH REPLAY
      ------------------------------------------------- */}

      <section
        className="results-section"
        id="replay"
      >

        <SectionHeader
          number="06"
          eyebrow="Audit & provenance"
          title="Research replay"
          description="Trace how OpportunityOS moved from queries and source collection to signals and hypotheses."
        />

        <div className="panel intelligence-panel">

          <div className="panel-heading">

            <div>
              <span className="panel-kicker">
                Research provenance
              </span>

              <h3>
                Research pipeline
              </h3>
            </div>

            <RefreshCw size={17} />

          </div>

          <ResearchReplay
            data={data}
          />

        </div>

      </section>


      {/* -------------------------------------------------
          FINAL NOTE
      ------------------------------------------------- */}

      <section className="results-closing">

        <div>
          <span className="closing-icon">
            <CheckCircle2 size={17} />
          </span>

          <div>
            <strong>
              Evidence informs decisions.
            </strong>

            <span>
              OpportunityOS surfaces signals and hypotheses for
              investigation; it does not guarantee outcomes.
            </span>
          </div>
        </div>

      </section>

    </main>
  );
}


/* -------------------------------------------------
   Section header
------------------------------------------------- */

function SectionHeader({
  number,
  eyebrow,
  title,
  description,
  action,
}) {
  return (
    <div className="section-heading">

      <div className="section-heading-main">

        {number && (
          <span className="section-number">
            {number}
          </span>
        )}

        <div>

          <div className="eyebrow">
            {eyebrow}
          </div>

          <h2>
            {title}
          </h2>

          {description && (
            <p>
              {description}
            </p>
          )}

        </div>

      </div>

      {action && (
        <span className="section-action">
          {action}
        </span>
      )}

    </div>
  );
}


/* -------------------------------------------------
   Overview metric
------------------------------------------------- */

function OverviewMetric({
  label,
  value,
  detail,
}) {
  return (
    <div className="overview-metric">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

      <small>
        {detail}
      </small>

    </div>
  );
}


/* -------------------------------------------------
   Helpers
------------------------------------------------- */

function getSignalLabel(score) {
  if (score >= 75) return 'Strong observed signal';
  if (score >= 55) return 'Moderate observed signal';
  if (score >= 35) return 'Limited observed signal';

  return 'Weak observed signal';
}