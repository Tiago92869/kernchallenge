import { Route, Routes } from 'react-router-dom'

import AppLayout from '../components/AppLayout'
import ProtectedRoute from '../components/ProtectedRoute'
import PublicOnlyRoute from '../components/PublicOnlyRoute'
import DashboardPage from '../pages/DashboardPage'
import CreateAccountPage from '../pages/CreateAccountPage'
import LandingPage from '../pages/LandingPage'
import LoginPage from '../pages/LoginPage'
import NotFoundPage from '../pages/NotFoundPage'
import NotificationsPage from '../pages/NotificationsPage'
import ProjectsPage from '../pages/ProjectsPage'
import TimeEntriesPage from '../pages/TimeEntriesPage'

function AppRoutes() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <PublicOnlyRoute>
            <LandingPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/login"
        element={
          <PublicOnlyRoute>
            <LoginPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/signup"
        element={
          <PublicOnlyRoute>
            <CreateAccountPage />
          </PublicOnlyRoute>
        }
      />

      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        }
      >
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="projects" element={<ProjectsPage />} />
        <Route path="time-entries" element={<TimeEntriesPage />} />
        <Route path="notifications" element={<NotificationsPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}

export default AppRoutes
