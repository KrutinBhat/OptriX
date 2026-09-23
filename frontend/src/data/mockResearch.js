export const mockResearch = {
  topic: 'Drone Components', location: 'India',
  google_search: { source: 'google_search', queries_executed: 2, results: [
    { title: 'Drone component manufacturers in India', link: 'https://example.com/manufacturers', snippet: 'Illustrative development result for supplier discovery.' },
    { title: 'UAV battery systems and components', link: 'https://example.com/batteries', snippet: 'Illustrative development result for market context.' },
  ] },
  google_news: { source: 'google_news', queries_executed: 1, results: [{ title: 'Illustrative UAV sector coverage', link: 'https://example.com/news', snippet: 'Development sample, not live reporting.' }] },
  google_jobs: { source: 'google_jobs', queries_executed: 1, results: [] },
  google_maps: { source: 'google_maps', queries_executed: 1, results: [] },
  google_shopping: { source: 'google_shopping', queries_executed: 1, results: [] },
  google_scholar: { source: 'google_scholar', queries_executed: 1, results: [] },
  research_stats: { total_queries: 7, total_results: 3 },
};

export const exampleOpportunity = {
  title: 'Drone battery thermal management',
  description: 'An illustrative hypothesis about thermal performance and reliability in compact UAV power systems.',
  indicators: [['Demand', 'High'], ['Supply gap', 'Medium'], ['Technology activity', 'High'], ['Competition', 'Medium']],
  supporting: ['Illustrative search and news coverage point to sustained interest.', 'Battery engineering is a relevant adjacent capability.'],
  counter: ['Established battery and electronics suppliers may already serve this segment.', 'Certification, safety and thermal design raise development costs.'],
};
