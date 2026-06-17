const STEPS = [
  { label: 'Fetching PR diff from GitHub…', delay: 0 },
  { label: 'Security agent scanning for vulnerabilities…', delay: 8 },
  { label: 'Style agent reviewing code quality…', delay: 22 },
  { label: 'Test agent checking coverage…', delay: 36 },
  { label: 'Compiling final verdict…', delay: 50 },
]

import { useState, useEffect } from 'react'

export default function LoadingState({ repo, prNumber }) {
  const [stepIndex, setStepIndex] = useState(0)
  const [elapsed, setElapsed] = useState(0)

  useEffect(() => {
    const ticker = setInterval(() => setElapsed(s => s + 1), 1000)
    return () => clearInterval(ticker)
  }, [])

  useEffect(() => {
    const next = STEPS.findLastIndex(s => elapsed >= s.delay)
    if (next >= 0 && next !== stepIndex) setStepIndex(next)
  }, [elapsed])

  return (
    <div className="loading-state">
      <div className="spinner" aria-hidden="true" />
      <p className="loading-title">Agents are reviewing your PR…</p>
      <p className="loading-target">
        <span className="mono">{repo}</span> #{prNumber}
      </p>
      <p className="loading-step">{STEPS[stepIndex].label}</p>
      <p className="loading-elapsed">{elapsed}s elapsed, this usually takes 30-60 seconds</p>
    </div>
  )
}
