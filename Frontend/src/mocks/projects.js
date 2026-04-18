export const MOCK_PROJECTS = [
  {
    id: 'project-beta-website-update',
    name: 'Beta Website Update',
    description: 'Revamp landing pages and optimize conversion funnels for the spring launch.',
    visibility: 'PUBLIC',
    isArchived: false,
    userRole: 'OWNER',
    isMine: true,
    members: [
      { id: 'u-alex', firstName: 'Alex', lastName: 'Johnson' },
      { id: 'u-emma', firstName: 'Emma', lastName: 'Clark' },
      { id: 'u-luca', firstName: 'Luca', lastName: 'Silva' },
    ],
    canAccess: true,
    createdAt: '2026-04-03T10:30:00',
    lastEntryAt: '2026-04-16T09:20:00',
  },
  {
    id: 'project-marketing-campaign',
    name: 'Marketing Campaign',
    description: 'Cross-channel campaign planning with social and email rollout.',
    visibility: 'PRIVATE',
    isArchived: false,
    userRole: 'MEMBER',
    isMine: false,
    members: [
      { id: 'u-alex', firstName: 'Alex', lastName: 'Johnson' },
      { id: 'u-john', firstName: 'John', lastName: 'Reed' },
      { id: 'u-maria', firstName: 'Maria', lastName: 'Silva' },
    ],
    canAccess: false,
    createdAt: '2026-03-12T09:00:00',
    lastEntryAt: '2026-04-13T17:40:00',
  },
  {
    id: 'project-website-redesign',
    name: 'Website Redesign',
    description: 'Modernize the product website and migrate to new design tokens.',
    visibility: 'PUBLIC',
    isArchived: true,
    userRole: 'OWNER',
    isMine: true,
    members: [
      { id: 'u-alex', firstName: 'Alex', lastName: 'Johnson' },
      { id: 'u-noah', firstName: 'Noah', lastName: 'Walker' },
      { id: 'u-lia', firstName: 'Lia', lastName: 'Costa' },
      { id: 'u-zoe', firstName: 'Zoe', lastName: 'Meyer' },
    ],
    canAccess: true,
    createdAt: '2026-02-05T12:15:00',
    lastEntryAt: '2026-04-04T11:00:00',
  },
  {
    id: 'project-mobile-app-development',
    name: 'Mobile App Development',
    description: 'Build core timesheet flows for iOS and Android.',
    visibility: 'PRIVATE',
    isArchived: false,
    userRole: 'MEMBER',
    isMine: false,
    members: [
      { id: 'u-alex', firstName: 'Alex', lastName: 'Johnson' },
      { id: 'u-sam', firstName: 'Sam', lastName: 'Nunes' },
      { id: 'u-rita', firstName: 'Rita', lastName: 'Pires' },
    ],
    canAccess: true,
    createdAt: '2025-12-10T08:50:00',
    lastEntryAt: '2026-04-17T10:10:00',
  },
  {
    id: 'project-alpha',
    name: 'Project Alpha',
    description: 'Core platform updates and sprint execution for milestone A.',
    visibility: 'PUBLIC',
    isArchived: false,
    userRole: 'OWNER',
    isMine: true,
    members: [
      { id: 'u-alex', firstName: 'Alex', lastName: 'Johnson' },
      { id: 'u-ian', firstName: 'Ian', lastName: 'Parker' },
      { id: 'u-lina', firstName: 'Lina', lastName: 'Rocha' },
    ],
    canAccess: true,
    createdAt: '2026-01-20T13:20:00',
    lastEntryAt: '2026-04-18T07:10:00',
  },
]

export const MOCK_PROJECT_ENTRIES = [
  {
    id: 'pentry-1001',
    projectId: 'project-alpha',
    user: { firstName: 'Alex', lastName: 'Johnson' },
    date: '2026-04-18',
    durationMinutes: 150,
    description: 'Wrote new landing page copy and refined CTA placement.',
  },
  {
    id: 'pentry-1002',
    projectId: 'project-alpha',
    user: { firstName: 'Alex', lastName: 'Johnson' },
    date: '2026-04-17',
    durationMinutes: 90,
    description: 'Team meeting and follow-ups for sprint planning.',
  },
  {
    id: 'pentry-1003',
    projectId: 'project-alpha',
    user: { firstName: 'Alex', lastName: 'Johnson' },
    date: '2026-04-16',
    durationMinutes: 120,
    description: 'Fixed dashboard bugs and reviewed QA regressions.',
  },
  {
    id: 'pentry-1004',
    projectId: 'project-beta-website-update',
    user: { firstName: 'Emma', lastName: 'Clark' },
    date: '2026-04-16',
    durationMinutes: 135,
    description: 'Updated feature highlights section for campaign launch.',
  },
  {
    id: 'pentry-1005',
    projectId: 'project-beta-website-update',
    user: { firstName: 'Luca', lastName: 'Silva' },
    date: '2026-04-15',
    durationMinutes: 105,
    description: 'Implemented responsive header fixes and accessibility polish.',
  },
  {
    id: 'pentry-1006',
    projectId: 'project-marketing-campaign',
    user: { firstName: 'John', lastName: 'Reed' },
    date: '2026-04-14',
    durationMinutes: 180,
    description: 'Prepared Q2 campaign creatives and channel plan.',
  },
  {
    id: 'pentry-1007',
    projectId: 'project-mobile-app-development',
    user: { firstName: 'Sam', lastName: 'Nunes' },
    date: '2026-04-17',
    durationMinutes: 120,
    description: 'Integrated auth flow and fixed onboarding screen issues.',
  },
]

export function getMockProjectById(projectId) {
  return MOCK_PROJECTS.find((project) => project.id === projectId) || null
}

export function getMockEntriesByProjectId(projectId) {
  return MOCK_PROJECT_ENTRIES.filter((entry) => entry.projectId === projectId)
}

export const MOCK_PROJECT_MEMBERS = {
  'project-alpha': [
    {
      id: 'u-alex',
      firstName: 'Alex',
      lastName: 'Parker',
      email: 'alex.parker@example.com',
      role: 'OWNER',
      joinedAt: '2024-04-05',
    },
    {
      id: 'u-sarah',
      firstName: 'Sarah',
      lastName: 'Thompson',
      email: 's.thompson@example.com',
      role: 'MEMBER',
      joinedAt: '2024-04-08',
    },
    {
      id: 'u-dave',
      firstName: 'Dave',
      lastName: 'Johnson',
      email: 'd.johnson@example.com',
      role: 'MEMBER',
      joinedAt: '2024-04-09',
    },
    {
      id: 'u-emma',
      firstName: 'Emma',
      lastName: 'Davis',
      email: 'emma.davis@example.com',
      role: 'MEMBER',
      joinedAt: '2024-04-10',
    },
  ],
  'project-beta-website-update': [
    {
      id: 'u-alex',
      firstName: 'Alex',
      lastName: 'Parker',
      email: 'alex.parker@example.com',
      role: 'OWNER',
      joinedAt: '2024-04-03',
    },
    {
      id: 'u-luca',
      firstName: 'Luca',
      lastName: 'Silva',
      email: 'l.silva@example.com',
      role: 'MEMBER',
      joinedAt: '2024-04-06',
    },
  ],
}

export const MOCK_ADDABLE_USERS = [
  { id: 'u-ryan', firstName: 'Ryan', lastName: 'Carter', email: 'ryan.carter@example.com' },
  { id: 'u-sarah-w', firstName: 'Sarah', lastName: 'Williams', email: 'sarah.williams@example.com' },
  { id: 'u-michael', firstName: 'Michael', lastName: 'Brown', email: 'm.brown@example.com' },
  { id: 'u-lisa', firstName: 'Lisa', lastName: 'Robinson', email: 'lisa.robinson@example.com' },
  { id: 'u-elena', firstName: 'Elena', lastName: 'Mora', email: 'elena.mora@example.com' },
]

export function getMockMembersByProjectId(projectId) {
  const fallbackMembers = getMockProjectById(projectId)?.members || []
  const seeded = MOCK_PROJECT_MEMBERS[projectId]

  if (seeded?.length) {
    return seeded.map((member) => ({ ...member }))
  }

  return fallbackMembers.map((member, index) => ({
    id: member.id,
    firstName: member.firstName,
    lastName: member.lastName,
    email: `${member.firstName.toLowerCase()}.${member.lastName.toLowerCase()}@example.com`,
    role: index === 0 ? 'OWNER' : 'MEMBER',
    joinedAt: '2024-04-01',
  }))
}
