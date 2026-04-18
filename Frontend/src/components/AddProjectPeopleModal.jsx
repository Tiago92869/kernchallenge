import { useMemo, useState } from 'react'

function getInitials(firstName, lastName) {
  return `${firstName[0] || ''}${lastName[0] || ''}`.toUpperCase()
}

function AddProjectPeopleModal({ isOpen, users, onClose, onDone }) {
  const [searchValue, setSearchValue] = useState('')
  const [selectedIds, setSelectedIds] = useState([])

  const visibleUsers = useMemo(() => {
    const normalized = searchValue.trim().toLowerCase()
    if (!normalized) {
      return users
    }

    return users.filter((user) =>
      [user.firstName, user.lastName, user.email].join(' ').toLowerCase().includes(normalized),
    )
  }, [users, searchValue])

  if (!isOpen) {
    return null
  }

  function toggleSelected(userId) {
    setSelectedIds((current) =>
      current.includes(userId) ? current.filter((id) => id !== userId) : [...current, userId],
    )
  }

  function handleClose() {
    setSearchValue('')
    setSelectedIds([])
    onClose()
  }

  function handleDone() {
    onDone(selectedIds)
    setSearchValue('')
    setSelectedIds([])
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={handleClose}>
      <article
        className="modal-card add-people-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-people-title"
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-head add-people-head">
          <h2 id="add-people-title">Add People</h2>
          <button type="button" className="add-people-close" onClick={handleClose} aria-label="Close add people">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M18.3 5.7 12 12l6.3 6.3-1.4 1.4L10.6 13.4 4.3 19.7 2.9 18.3 9.2 12 2.9 5.7l1.4-1.4 6.3 6.3 6.3-6.3z" />
            </svg>
          </button>
        </header>

        <div className="modal-body add-people-body">
          <label className="field add-people-search" htmlFor="add-people-search-input">
            <span className="sr-only">Search users</span>
            <input
              id="add-people-search-input"
              type="search"
              value={searchValue}
              onChange={(event) => setSearchValue(event.target.value)}
              placeholder="Search users..."
            />
          </label>

          <ul className="add-people-list">
            {visibleUsers.map((user) => {
              const isSelected = selectedIds.includes(user.id)

              return (
                <li key={user.id} className="add-people-row">
                  <div className="add-people-user">
                    <span className="project-member-bubble add-people-avatar">{getInitials(user.firstName, user.lastName)}</span>
                    <div>
                      <strong>{`${user.firstName} ${user.lastName}`}</strong>
                      <p className="muted">{user.email}</p>
                    </div>
                  </div>

                  <button
                    type="button"
                    className={isSelected ? 'btn-secondary' : 'btn-primary'}
                    onClick={() => toggleSelected(user.id)}
                  >
                    {isSelected ? 'Added' : 'Add'}
                  </button>
                </li>
              )
            })}
          </ul>

          <div className="add-people-footer">
            <button type="button" className="btn-secondary" onClick={handleClose}>
              Cancel
            </button>
            <button type="button" className="btn-primary" onClick={handleDone}>
              Done
            </button>
          </div>
        </div>
      </article>
    </div>
  )
}

export default AddProjectPeopleModal
