import { useEffect, useRef } from 'react'

export default function ConfirmDialog({ title, children, confirmLabel, onConfirm, onCancel }) {
  const cancelRef = useRef(null)

  useEffect(() => {
    cancelRef.current?.focus()
    const onKey = (event) => {
      if (event.key === 'Escape') onCancel()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onCancel])

  return (
    <div className="dialog-scrim" onClick={onCancel}>
      <div
        className="dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="dialog-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 id="dialog-title">{title}</h2>
        <p>{children}</p>
        <div className="dialog-actions">
          <button type="button" className="btn btn-secondary" ref={cancelRef} onClick={onCancel}>
            Cancel
          </button>
          <button type="button" className="btn btn-danger" onClick={onConfirm}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
