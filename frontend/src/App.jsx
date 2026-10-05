import { useEffect, useState } from 'react';
import {
  Activity,
  Bell,
  ChevronDown,
  CircleHelp,
  Menu,
} from 'lucide-react';

import Home from './pages/Home.jsx';
import Results from './pages/Results.jsx';
import OpportunityDetails from './pages/OpportunityDetails.jsx';
import { runResearch } from './services/api.js';
import { mockResearch, exampleOpportunity } from './data/mockResearch.js';

function normalizeOpportunity(candidate, input) {
  if (!candidate) {
    return {
      title: `${input.topic} — areas to investigate`,
      description:
        'The backend returned source material but no structured opportunity hypotheses. Review the records to develop and validate an assessment.',
      score_breakdown: {},
      supporting_evidence: [],
      counter_evidence: [],
    };
  }

  return {
    ...exampleOpportunity,
    ...candidate,
    indicators:
      candidate.indicators || exampleOpportunity.indicators,
    supporting_evidence:
      candidate.supporting_evidence ||
      candidate.supporting ||
      [],
    counter_evidence:
      candidate.counter_evidence ||
      candidate.counter ||
      [],
  };
}

export default function App() {
  const [showIntro, setShowIntro] = useState(true);

useEffect(() => {
  const timer = setTimeout(() => {
    setShowIntro(false);
  }, 10000);

  return () => clearTimeout(timer);
}, []);
  const [view, setView] = useState('home');
  const [data, setData] = useState(null);
  const [mock, setMock] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [opportunity, setOpportunity] =
    useState(exampleOpportunity);

  async function research(input) {
    setError('');
    setLoading(true);

    try {
      const response = await runResearch(input);

      if (
        response &&
        typeof response === 'object' &&
        Object.keys(response).length
      ) {
        setData(response);
        setMock(false);

        const candidate = Array.isArray(response.opportunities)
          ? response.opportunities[0]
          : null;

        setOpportunity(
          normalizeOpportunity(candidate, input),
        );
      } else {
        setData({
          ...mockResearch,
          ...input,
        });

        setMock(true);
        setOpportunity(exampleOpportunity);
      }

      setView('results');
    } catch (e) {
      setError(
        e.message ||
          'Unable to connect to the research engine. Please make sure the backend is running.',
      );
    } finally {
      setLoading(false);
    }
  }

  const back = () => setView('results');

  const showDemo = () => {
    setData(mockResearch);
    setMock(true);
    setOpportunity(exampleOpportunity);
    setView('results');
  };

  return (
  <>
    {showIntro && (
      <div className="intro-screen">
        <video
          src="/optrix-intro.mp4"
          autoPlay
          muted
          playsInline
          onEnded={() => setShowIntro(false)}
        />
      </div>
    )}

    <div className="app-shell">
      <header className="topbar">
        <a
          className="brand"
          href="#"
          onClick={(event) => {
            event.preventDefault();
            setView('home');
          }}
          aria-label="OptriX home"
        >
          <span className="brand-mark">
            <Activity size={19} aria-hidden="true" />
          </span>

          <span>
            OptriX
            <small>MARKET INTELLIGENCE</small>
          </span>
        </a>

        <nav aria-label="Primary navigation">
          <button
            type="button"
            className={`nav-item ${
              view === 'home' ? 'current' : ''
            }`}
            onClick={() => setView('home')}
          >
            Research
          </button>

          <button
            type="button"
            className={`nav-item ${
              view !== 'home' ? 'current' : ''
            }`}
            onClick={() => data && setView('results')}
          >
            Workspace
          </button>
        </nav>

        <div className="top-actions">
          <span className="connection">
            <i />
            Research engine
          </span>

          {/* Showcase-only control */}
          <button
            type="button"
            className="icon-button"
            aria-label="Help"
            title="Help — showcase"
          >
            <CircleHelp size={17} aria-hidden="true" />
          </button>

          {/* Showcase-only control */}
          <button
            type="button"
            className="icon-button"
            aria-label="Notifications"
            title="Notifications — showcase"
          >
            <Bell size={17} aria-hidden="true" />
          </button>

          {/* Showcase-only profile control */}
          <button
            type="button"
            className="profile-button"
            aria-label="Profile — showcase"
            title="Profile — showcase"
          >
            <span>OS</span>
            <ChevronDown size={13} aria-hidden="true" />
          </button>

          <button
            type="button"
            className="mobile-menu"
            aria-label="Menu"
          >
            <Menu size={20} aria-hidden="true" />
          </button>
        </div>
      </header>

      {view === 'home' ? (
        <Home
          onSubmit={research}
          loading={loading}
          error={error}
          onDemo={showDemo}
        />
      ) : view === 'detail' ? (
        <OpportunityDetails
          opportunity={opportunity}
          data={data}
          mock={mock}
          onBack={back}
        />
      ) : (
        <Results
          data={data}
          mock={mock}
          opportunity={opportunity}
          onBack={() => setView('home')}
          onExplore={() => setView('detail')}
        />
      )}

      <footer className="footer">
        <span>
          OPTRIX <b>·</b> MARKET SIGNALS, WITH SOURCES
        </span>

        <span>
          Evidence informs decisions. It does not guarantee
          outcomes.
        </span>
      </footer>
    </div>
  </>
  );
}