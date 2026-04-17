export const MOCK_PROJECTS = [
  {
    id: 'project-website-redesign',
    name: 'Website Redesign',
    visibility: 'PUBLIC',
    accent: 'blue',
  },
  {
    id: 'project-marketing-campaign',
    name: 'Marketing Campaign',
    visibility: 'PRIVATE',
    accent: 'amber',
  },
  {
    id: 'project-client-meeting',
    name: 'Client Meeting',
    visibility: 'PRIVATE',
    accent: 'slate',
  },
  {
    id: 'project-mobile-mvp',
    name: 'Mobile App Development',
    visibility: 'PUBLIC',
    accent: 'green',
  },
  {
    id: 'project-internal-research',
    name: 'Internal Research',
    visibility: 'PRIVATE',
    accent: 'violet',
  },
  {
    id: 'project-product-planning',
    name: 'Product Planning',
    visibility: 'PUBLIC',
    accent: 'rose',
  },
]

export const MOCK_TIME_RANGE_OPTIONS = [
  { value: 'all', label: 'All time' },
  { value: 'last-7', label: 'Last 7 days' },
  { value: 'last-30', label: 'Last 30 days' },
  { value: 'april-2026', label: 'April 2026' },
  { value: 'march-2026', label: 'March 2026' },
]

export const MOCK_TIME_ENTRIES = [
  {
    id: 'entry-1001',
    projectId: 'project-website-redesign',
    date: '2026-04-16',
    durationMinutes: 210,
    description: 'Designing new homepage layout and updating graphics.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-04-16T08:45:00',
    updatedAt: '2026-04-16T12:18:00',
    focus: 'Design system refresh',
    tags: ['Design', 'Homepage', 'UI'],
  },
  {
    id: 'entry-1002',
    projectId: 'project-marketing-campaign',
    date: '2026-04-15',
    durationMinutes: 150,
    description: 'Drafted content calendar and aligned next-week launch assets.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-04-15T09:00:00',
    updatedAt: '2026-04-15T11:55:00',
    focus: 'Campaign planning',
    tags: ['Content', 'Planning'],
  },
  {
    id: 'entry-1003',
    projectId: 'project-client-meeting',
    date: '2026-04-14',
    durationMinutes: 75,
    description: 'Reviewed sprint goals and clarified deliverables with the client.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-04-14T14:10:00',
    updatedAt: '2026-04-14T15:22:00',
    focus: 'Stakeholder sync',
    tags: ['Meeting', 'Client'],
  },
  {
    id: 'entry-1004',
    projectId: 'project-mobile-mvp',
    date: '2026-04-12',
    durationMinutes: 240,
    description: 'Fixed navigation state bugs and validated edge cases on tablet viewports.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-04-12T10:05:00',
    updatedAt: '2026-04-12T14:20:00',
    focus: 'Bug fixing',
    tags: ['QA', 'Mobile'],
  },
  {
    id: 'entry-1005',
    projectId: 'project-internal-research',
    date: '2026-04-10',
    durationMinutes: 165,
    description: 'Benchmarked competitor time-tracking flows and documented useful patterns.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-04-10T08:30:00',
    updatedAt: '2026-04-10T11:17:00',
    focus: 'Discovery research',
    tags: ['Research', 'Analysis'],
  },
  {
    id: 'entry-1006',
    projectId: 'project-product-planning',
    date: '2026-04-08',
    durationMinutes: 195,
    description: 'Mapped feature priorities and refined acceptance notes for the next sprint.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-04-08T13:05:00',
    updatedAt: '2026-04-08T16:41:00',
    focus: 'Sprint planning',
    tags: ['Planning', 'Backlog'],
  },
  {
    id: 'entry-1007',
    projectId: 'project-website-redesign',
    date: '2026-03-28',
    durationMinutes: 120,
    description: 'Updated section hierarchy after review feedback and reworked hero copy spacing.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-03-28T09:20:00',
    updatedAt: '2026-03-28T11:28:00',
    focus: 'Iteration pass',
    tags: ['Design', 'Review'],
  },
  {
    id: 'entry-1008',
    projectId: 'project-mobile-mvp',
    date: '2026-03-22',
    durationMinutes: 90,
    description: 'Verified onboarding states and documented device-specific rendering issues.',
    loggedBy: 'Alex Johnson',
    createdAt: '2026-03-22T10:15:00',
    updatedAt: '2026-03-22T12:00:00',
    focus: 'Regression review',
    tags: ['Testing', 'Mobile'],
  },
]

export function getMockProjectById(projectId) {
  return MOCK_PROJECTS.find((project) => project.id === projectId) || null
}

export function getMockTimeEntryById(entryId) {
  const entry = MOCK_TIME_ENTRIES.find((item) => item.id === entryId)
  if (!entry) {
    return null
  }

  const project = getMockProjectById(entry.projectId)
  return {
    ...entry,
    project,
  }
}