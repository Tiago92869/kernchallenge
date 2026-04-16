# TimeSync Frontend

Frontend application for the TimeSync project built with React and Vite.

## Prerequisites

- Node.js 20+
- npm 10+

## How To Run (Local Development)

1. Open a terminal in the Frontend folder.
2. Install dependencies:

```bash
npm install
```

3. Start development server:

```bash
npm run dev
```

4. Open the URL shown in terminal (usually http://localhost:5173).

## Useful Commands

Run lint:

```bash
npm run lint
```

Build production bundle:

```bash
npm run build
```

Preview production build locally:

```bash
npm run preview
```

## Environment Notes

- API base URL is consumed in code through VITE_API_URL.
- If not set, the frontend defaults to http://localhost:5000.

You can create a .env file in this folder when needed, for example:

```env
VITE_API_URL=http://localhost:5000
```

## Folder Organization

```text
Frontend/
  index.html                # Vite HTML entry template
  package.json              # Scripts and dependencies
  vite.config.js            # Vite configuration
  eslint.config.js          # ESLint configuration
  public/                   # Static files served as-is
  src/
    main.jsx                # App bootstrap (Router and providers)
    App.jsx                 # Root app component
    index.css               # Global styles
    App.css                 # Additional app-level styles
    assets/                 # Images and static assets used by components
      hero.png
      react.svg
      vite.svg
    components/             # Reusable route/feature components
      ProtectedRoute.jsx
      PublicOnlyRoute.jsx
    context/                # Global React context/state
      AuthContext.jsx
      AuthContextValue.js
    hooks/                  # Reusable custom hooks
      useAuth.js
    pages/                  # Route-level pages/screens
      LandingPage.jsx
      LoginPage.jsx
      SignupPage.jsx
      DashboardPage.jsx
    routes/                 # Route definitions and composition
      AppRoutes.jsx
```

## Current Routing Summary

Public routes:
- / -> Landing page
- /login -> Login page
- /signup -> Signup page

Protected route:
- /dashboard -> Dashboard page

Public routes are guarded by a public-only wrapper, and dashboard is guarded by an auth-protected wrapper.
