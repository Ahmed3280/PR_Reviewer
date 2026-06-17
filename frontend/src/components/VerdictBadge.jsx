function stripMarkdown(text) {
  return text
    .replace(/^#{1,3}\s+/gm, '')
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
}

function parseVerdictSummary(raw) {
  const stripped = stripMarkdown(raw)
  return stripped
    .split('\n')
    .map(l => l.trim())
    .filter(l => {
      if (!l) return false
      if (/^verdict:/i.test(l)) return false
      if (/^summary of (critical )?issues:?$/i.test(l)) return false
      return true
    })
    .join('\n')
    .trim()
}

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
  const summary = parseVerdictSummary(verdict)

  return (
    <div className="verdict-section">
      <div className={`verdict-badge verdict-badge--${color}`}>
        <span className="verdict-badge__icon">{icon}</span>
        <span className="verdict-badge__label">{label}</span>
      </div>
      {summary && (
        <div className="verdict-summary">
          <p className="verdict-summary__label">Summary</p>
          <p className="verdict-summary__text">{summary}</p>
        </div>
      )}
      <button className="reset-btn" onClick={onReset}>
        Review Another PR
      </button>
    </div>
  )
}
