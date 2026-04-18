import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import AddProjectPeopleModal from '../components/AddProjectPeopleModal'
import {
  MOCK_ADDABLE_USERS,
  getMockMembersByProjectId,
  getMockProjectById,
} from '../mocks/projects'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function getInitials(firstName, lastName) {
  return `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()
}

function ProjectMembersPage() {
  const navigate = useNavigate()
  const { id } = useParams()

  const project = getMockProjectById(id)
  const [members, setMembers] = useState(() => getMockMembersByProjectId(id))
  const [isAddOpen, setIsAddOpen] = useState(false)

  const addableUsers = useMemo(() => {
    const currentIds = new Set(members.map((member) => member.id))
    return MOCK_ADDABLE_USERS.filter((user) => !currentIds.has(user.id))
  }, [members])

  if (!project) {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Project not found.</p>
          <button type="button" className="btn-primary entry-missing-link" onClick={() => navigate('/projects')}>
            Back to Projects
          </button>
        </div>
      </section>
    )
  }

  if (project.userRole !== 'OWNER') {
    return (
      <section className="dashboard-stack">
        <div className="dashboard-card">
          <p className="muted">Only project owners can manage members.</p>
          <button type="button" className="btn-primary entry-missing-link" onClick={() => navigate(`/projects/${project.id}`)}>
            Back to Project
          </button>
        </div>
      </section>
    )
  }

  return (
    <>
    <section className={`stack-lg project-members-page ${isAddOpen ? 'blurred' : ''}`}>
      <div className="dashboard-card project-members-header-card">
        <div>
          <p className="project-members-breadcrumb">{project.name} · Project Members</p>
          <h2>Project Members</h2>
        </div>

        <button type="button" className="btn-primary" onClick={() => setIsAddOpen(true)}>
          Add People
        </button>
      </div>

      <div className="dashboard-card entries-table-card">
        <div className="entries-table-wrap">
          <table className="entries-table project-members-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Joined At</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {members.map((member) => (
                <tr key={member.id}>
                  <td>
                    <div className="project-member-name-cell">
                      <span className="project-member-bubble">{getInitials(member.firstName, member.lastName)}</span>
                      <strong>{`${member.firstName} ${member.lastName}`}</strong>
                    </div>
                  </td>
                  <td>{member.email}</td>
                  <td>
                    <span className={`project-role-badge ${member.role === 'OWNER' ? 'owner' : 'member'}`}>
                      {member.role === 'OWNER' ? 'Owner' : 'Member'}
                    </span>
                  </td>
                  <td>{formatDate(member.joinedAt)}</td>
                  <td>
                    {member.role === 'OWNER' ? (
                      <span className="muted">-</span>
                    ) : (
                      <button
                        type="button"
                        className="member-remove-btn"
                        onClick={() => setMembers((current) => current.filter((item) => item.id !== member.id))}
                      >
                        Remove
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </section>

      <AddProjectPeopleModal
        key={isAddOpen ? 'add-open' : 'add-closed'}
        isOpen={isAddOpen}
        users={addableUsers}
        onClose={() => setIsAddOpen(false)}
        onDone={(selectedIds) => {
          if (!selectedIds.length) {
            setIsAddOpen(false)
            return
          }

          const joinedAt = new Date().toISOString().slice(0, 10)
          const selectedUsers = addableUsers
            .filter((user) => selectedIds.includes(user.id))
            .map((user) => ({
              id: user.id,
              firstName: user.firstName,
              lastName: user.lastName,
              email: user.email,
              role: 'MEMBER',
              joinedAt,
            }))

          setMembers((current) => [...current, ...selectedUsers])
          setIsAddOpen(false)
        }}
      />
    </>
  )
}

export default ProjectMembersPage
