const NO_ISSUES_PHRASES = [
  'no issues',
  'no problems',
  'no concerns',
  'no vulnerabilities',
  'looks good',
  'nothing to report',
  'no significant',
]

function hasNoIssues(text) {
  const lower = text.toLowerCase()
  return NO_ISSUES_PHRASES.some(p => lower.includes(p))
}

export default function FindingsCard({ title, findings, accent }) {
  const clean = hasNoIssues(findings)

  return (
    <div className={`findings-card findings-card--${accent}`}>
      <div className="findings-card__header">
        <span className={`findings-card__dot findings-card__dot--${accent}`} />
        <h2 className="findings-card__title">{title}</h2>
        {clean && (
          <span className="findings-card__badge findings-card__badge--ok" title="No issues found">
            ✓
          </span>
        )}
      </div>
      <pre className="findings-card__body">{findings}</pre>
    </div>
  )
}
