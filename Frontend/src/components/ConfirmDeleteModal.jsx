function ConfirmDeleteModal({ isOpen, description, onCancel, onConfirm }) {
  if (!isOpen) {
    return null
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={onCancel}>
      <div
        className="modal-card confirm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-delete-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-head">
          <h2 id="confirm-delete-title">Delete Time Entry</h2>
        </div>

        <div className="modal-body stack-sm">
          <p className="confirm-copy">Are you sure that you want to delete this entry?</p>
          {description ? <p className="muted confirm-detail">{description}</p> : null}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              No
            </button>
            <button type="button" className="btn-danger" onClick={onConfirm}>
              Yes
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConfirmDeleteModal