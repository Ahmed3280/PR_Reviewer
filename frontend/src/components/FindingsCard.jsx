function stripMarkdown(text) {
  return text
    .replace(/^#{1,3}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
}

const NO_ISSUES_PREFIXES = [
  'no security issues found',
  'no style issues found',
  'no test coverage issues found',
]

function firstSentenceHasNoIssues(text) {
  const firstSentence = text.split(/[.\n]/)[0].toLowerCase()
  return NO_ISSUES_PREFIXES.some(p => firstSentence.includes(p))
}

function parsePoints(text) {
  const chunks = text.split(/\n\n+/)
  const points = []
  for (const chunk of chunks) {
    if (chunk.includes('\n')) {
      points.push(...chunk.split('\n'))
    } else {
      points.push(chunk)
    }
  }
  return points.map(p => p.trim().replace(/^\d+[\.\)]\s*/, '')).filter(Boolean)
}

export default function FindingsCard({ title, findings, accent }) {
  const clean = firstSentenceHasNoIssues(findings)

  if (clean) {
    return (
      <div className={`findings-card findings-card--${accent}`}>
        <div className="findings-card__header">
          <span className={`findings-card__dot findings-card__dot--${accent}`} />
          <h2 className="findings-card__title">{title}</h2>
          <span className="findings-card__badge findings-card__badge--ok" title="No issues found">
            ✓
          </span>
        </div>
      </div>
    )
  }

  const points = parsePoints(stripMarkdown(findings))

  return (
    <div className={`findings-card findings-card--${accent}`}>
      <div className="findings-card__header">
        <span className={`findings-card__dot findings-card__dot--${accent}`} />
        <h2 className="findings-card__title">{title}</h2>
      </div>
      <div className="findings-card__body">
        {points.length === 1 ? (
          <p className="findings-point">{points[0]}</p>
        ) : (
          points.map((point, i) => (
            <div key={i}>
              <p className="findings-point">
                <span className="findings-point__num">{i + 1}.</span> {point}
              </p>
              {i < points.length - 1 && <hr className="findings-separator" />}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
