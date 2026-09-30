import {
  ArrowDown,
  BarChart3,
  BriefcaseBusiness,
  CheckCircle2,
  GraduationCap,
  Map,
  Newspaper,
  Search,
  ShieldCheck,
  ShoppingBag,
  Sparkles,
} from 'lucide-react';

import SearchForm from '../components/SearchForm.jsx';

const SOURCE_CARDS = [
  {
    icon: Search,
    label: 'Search',
    description: 'Market demand',
  },
  {
    icon: Newspaper,
    label: 'News',
    description: 'Market momentum',
  },
  {
    icon: BriefcaseBusiness,
    label: 'Jobs',
    description: 'Talent demand',
  },
  {
    icon: Map,
    label: 'Maps',
    description: 'Local supply',
  },
  {
    icon: ShoppingBag,
    label: 'Shopping',
    description: 'Commercial activity',
  },
  {
    icon: GraduationCap,
    label: 'Scholar',
    description: 'Technology activity',
  },
];

export default function Home({
  onSubmit,
  loading,
  error,
  onDemo,
}) {
  return (
    <main className="home-hero">
      <div className="hero-orb orb-one" />
      <div className="hero-orb orb-two" />

      <div className="hero-content">

        {/* Kicker */}
        <div className="hero-kicker">
          <span className="kicker-icon">
            <Sparkles size={14} />
          </span>

          MARKET INTELLIGENCE, GROUNDED IN EVIDENCE
        </div>

        {/* Main heading */}
        <h1>
          Discover where
          <br />
          the market is <em>moving.</em>
        </h1>

        <p className="hero-copy">
          OpportunityOS researches live market signals across search,
          news, jobs, suppliers, products and research to uncover
          evidence-backed opportunities.
        </p>

        {/* Research card */}
        <section className="hero-card">

          <div className="form-heading">
            <div>
              <div className="section-eyebrow">
                <BarChart3 size={13} />
                MARKET RESEARCH
              </div>

              <h2>Start a research run</h2>

              <p>
                Define a market and location. OpportunityOS will
                investigate the available signals and build an
                evidence-backed research result.
              </p>
            </div>

            <span className="secure-label">
              <ShieldCheck size={14} />
              Evidence first
            </span>
          </div>

          <SearchForm
            onSubmit={onSubmit}
            loading={loading}
          />

          {/* Loading state */}
          {loading && (
            <div
              className="progress-state"
              role="status"
              aria-live="polite"
            >
              <span className="spinner" />

              <div>
                <b>Research in progress</b>

                <small>
                  Collecting and analyzing live market data.
                  This may take a few moments.
                </small>
              </div>
            </div>
          )}

          {/* Error state */}
          {error && !loading && (
            <div
              className="error-banner"
              role="alert"
            >
              <div>
                <strong>Research couldn't be completed.</strong>

                <span>{error}</span>
              </div>

              {onDemo && (
                <button
                  type="button"
                  className="demo-link"
                  onClick={onDemo}
                >
                  View development sample
                </button>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="form-foot">
            <span>
              API connection via your OpportunityOS backend
            </span>

            <span className="dot-sep" />

            <span>
              No API key exposed in browser
            </span>
          </div>
        </section>

        {/* Source coverage */}
        <section className="source-section">

          <div className="source-heading">
            <div>
              <span className="source-eyebrow">
                RESEARCH COVERAGE
              </span>

              <h3>
                Six independent market lenses
              </h3>
            </div>

            <span className="source-status">
              <CheckCircle2 size={14} />
              Multi-source research
            </span>
          </div>

          <div className="source-grid">
            {SOURCE_CARDS.map((source) => {
              const Icon = source.icon;

              return (
                <div
                  className="source-card"
                  key={source.label}
                >
                  <span className="source-icon">
                    <Icon size={16} />
                  </span>

                  <div>
                    <strong>{source.label}</strong>
                    <small>{source.description}</small>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Bottom navigation hint */}
        <div className="hero-bottom">
          <span>
            Search · Jobs · News · Maps · Shopping · Scholar
          </span>

          <span>
            <ArrowDown size={14} />
            Built for clearer decisions
          </span>
        </div>

      </div>
    </main>
  );
}