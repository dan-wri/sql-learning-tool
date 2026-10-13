import { useEffect, useRef } from 'react'
import { Loader2, Table2 } from 'lucide-react'
import ChangePreview from './ChangePreview.jsx'
import FeedbackPanel from './FeedbackPanel.jsx'
import ResultTable from './ResultTable.jsx'

export default function OutputWorkspace({ submission, submitting, onNext, nextLabel }) {
  const ref = useRef(null)

  // Bring fresh feedback into view inside the workspace's own scroll region.
  useEffect(() => {
    if (submission) ref.current?.scrollIntoView?.({ block: 'nearest', behavior: 'smooth' })
  }, [submission])

  if (submitting) {
    return (
      <section className="output card" aria-label="Output" aria-busy="true">
        <p className="output-empty">
          <Loader2 size={18} className="spin" aria-hidden="true" /> Running your query…
        </p>
      </section>
    )
  }
  if (!submission) {
    return (
      <section className="output card" aria-label="Output">
        <p className="output-empty">
          <Table2 size={18} aria-hidden="true" /> Run your query to see the result here.
        </p>
      </section>
    )
  }
  return (
    <section className="output card" aria-label="Output" ref={ref}>
      <FeedbackPanel submission={submission} onNext={onNext} nextLabel={nextLabel} />
      <ChangePreview changes={submission.changes} persisted={submission.persisted} reviewMode={submission.review_mode} />
      <ResultTable result={submission.result} />
    </section>
  )
}
