function ConfirmDeleteModal({
  isOpen,
  description,
  onCancel,
  onConfirm,
  title = 'Delete Time Entry',
  message = 'Are you sure that you want to delete this entry?',
  confirmText = 'Yes',
  cancelText = 'No',
  confirmClassName = 'btn-danger',
}) {
  if (!isOpen) {
    return null
  }

  return (
    <div className="modal-overlay" role="presentation" onClick={onCancel}>
      <div
        className="modal-card confirm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="modal-head">
          <h2 id="confirm-modal-title">{title}</h2>
        </div>

        <div className="modal-body stack-sm">
          <p className="confirm-copy">{message}</p>
          {description ? <p className="muted confirm-detail">{description}</p> : null}

          <div className="modal-actions">
            <button type="button" className="btn-secondary" onClick={onCancel}>
              {cancelText}
            </button>
            <button type="button" className={confirmClassName} onClick={onConfirm}>
              {confirmText}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConfirmDeleteModal