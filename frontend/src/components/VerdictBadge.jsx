function detectVerdict(text) {
  const upper = text.toUpperCase()
  if (upper.includes('APPROVE')) return 'APPROVE'
  if (upper.includes('REQUEST CHANGES')) return 'REQUEST CHANGES'
  if (upper.includes('COMMENT')) return 'COMMENT'
  return 'COMMENT'
}

const VERDICT_META = {
  'APPROVE': { color: 'green', icon: '✓' },
  'REQUEST CHANGES': { color: 'red', icon: '✗' },
  'COMMENT': { color: 'yellow', icon: '◉' },
}

export default function VerdictBadge({ verdict, onReset }) {
  const label = detectVerdict(verdict)
  const { color, icon } = VERDICT_META[label]

  return (
    <div className="verdict-section">
      <div className={`verdict-badge verdict-badge--${color}`}>
        <span className="verdict-badge__icon">{icon}</span>
        <span className="verdict-badge__label">{label}</span>
      </div>
      <pre className="verdict-text">{verdict}</pre>
      <button className="reset-btn" onClick={onReset}>
        Review Another PR
      </button>
    </div>
  )
}
