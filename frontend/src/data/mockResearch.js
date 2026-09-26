export const mockResearch = {
  topic: 'Drone Components',
  location: 'India',

  google_search: {
    source: 'google_search',
    queries_executed: 2,
    results: [
      {
        title: 'Drone component manufacturers in India',
        link: 'https://example.com/manufacturers',
        snippet: 'Illustrative development result for supplier discovery.',
      },
      {
        title: 'UAV battery systems and components',
        link: 'https://example.com/batteries',
        snippet: 'Illustrative development result for market context.',
      },
    ],
  },

  google_news: {
    source: 'google_news',
    queries_executed: 1,
    results: [
      {
        title: 'Illustrative UAV sector coverage',
        link: 'https://example.com/news',
        snippet: 'Development sample, not live reporting.',
      },
    ],
  },

  google_jobs: {
    source: 'google_jobs',
    queries_executed: 1,
    results: [],
  },

  google_maps: {
    source: 'google_maps',
    queries_executed: 1,
    results: [],
  },

  google_shopping: {
    source: 'google_shopping',
    queries_executed: 1,
    results: [],
  },

  google_scholar: {
    source: 'google_scholar',
    queries_executed: 1,
    results: [],
  },

  signals: {
    demand: {
      score: 72,
      evidence: [
        {
          title: 'Illustrative demand signal',
          snippet: 'Development sample indicating interest in drone components.',
        },
      ],
    },

    supply_gap: {
      score: 64,
      evidence: [
        {
          title: 'Illustrative supply signal',
          snippet: 'Development sample indicating limited specialization.',
        },
      ],
    },

    momentum: {
      score: 78,
      evidence: [
        {
          title: 'Illustrative momentum signal',
          snippet: 'Development sample indicating growing market activity.',
        },
      ],
    },

    technology: {
      score: 81,
      evidence: [
        {
          title: 'Illustrative technology signal',
          snippet: 'Development sample indicating relevant technical activity.',
        },
      ],
    },

    competition: {
      score: 45,
      evidence: [
        {
          title: 'Illustrative competition signal',
          snippet: 'Development sample indicating existing market participants.',
        },
      ],
    },

    geographic_gap: {
      score: 68,
      evidence: [
        {
          title: 'Illustrative geographic signal',
          snippet: 'Development sample indicating regional differences.',
        },
      ],
    },
  },

  opportunities: [
    {
      title: 'Drone battery thermal management',
      description:
        'An illustrative hypothesis about thermal performance and reliability in compact UAV power systems.',

      score: 71,

      score_breakdown: {
        demand: {
          score: 72,
          weight: 0.25,
          effect: 'positive',
        },
        supply_gap: {
          score: 64,
          weight: 0.25,
          effect: 'positive',
        },
        momentum: {
          score: 78,
          weight: 0.15,
          effect: 'positive',
        },
        technology: {
          score: 81,
          weight: 0.15,
          effect: 'positive',
        },
        geographic_gap: {
          score: 68,
          weight: 0.10,
          effect: 'positive',
        },
        competition: {
          score: 45,
          weight: 0.10,
          effect: 'negative',
        },
        counter_evidence: {
          count: 2,
          penalty: 6,
          effect: 'negative',
        },
      },

      supporting_signals: [
        'demand',
        'supply_gap',
        'momentum',
        'technology',
      ],

      supporting_evidence: [
        {
          title: 'Illustrative search evidence',
          snippet:
            'Search activity suggests sustained interest in UAV battery systems.',
          signal: 'demand',
        },
        {
          title: 'Illustrative technology evidence',
          snippet:
            'Battery thermal performance is relevant to compact UAV power systems.',
          signal: 'technology',
        },
        {
          title: 'Illustrative momentum evidence',
          snippet:
            'Recent sector coverage indicates continuing UAV technology activity.',
          signal: 'momentum',
        },
      ],

      counter_evidence: [
        {
          title: 'Existing suppliers',
          snippet:
            'Established battery and electronics suppliers may already serve parts of this segment.',
        },
        {
          title: 'Engineering barriers',
          snippet:
            'Certification, safety and thermal-design requirements can increase development complexity.',
        },
      ],
    },
  ],

  research_stats: {
    total_queries: 7,
    total_results: 3,
  },
};

export const exampleOpportunity = mockResearch.opportunities[0];