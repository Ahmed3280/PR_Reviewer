import { useState } from 'react'
import InputForm from './components/InputForm'
import LoadingState from './components/LoadingState'
import FindingsCard from './components/FindingsCard'
import VerdictBadge from './components/VerdictBadge'

const API_BASE = 'http://localhost:8000'

export default function App() {
  const [state, setState] = useState('idle') // idle | loading | done | error
  const [request, setRequest] = useState(null)
  const [result, setResult] = useState(null)
  const [errorMsg, setErrorMsg] = useState('')

  async function handleSubmit({ repo, pr_number }) {
    setRequest({ repo, pr_number })
    setState('loading')
    setErrorMsg('')

    try {
      const res = await fetch(`${API_BASE}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo, pr_number }),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || `Server error ${res.status}`)
      }

      setResult(data)
      setState('done')
    } catch (err) {
      setErrorMsg(err.message || 'Something went wrong. Is the backend running?')
      setState('error')
    }
  }

  function handleReset() {
    setState('idle')
    setRequest(null)
    setResult(null)
    setErrorMsg('')
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__inner">
          <span className="app-logo">◈</span>
          <h1 className="app-title">PR Reviewer</h1>
          <span className="app-subtitle">Multi-agent code review</span>
        </div>
      </header>

      <main className="app-main">
        {/* Input is always visible unless we are showing results */}
        {state !== 'done' && (
          <section className="section section--input">
            <InputForm onSubmit={handleSubmit} loading={state === 'loading'} />
          </section>
        )}

        {state === 'loading' && (
          <section className="section">
            <LoadingState repo={request.repo} prNumber={request.pr_number} />
          </section>
        )}

        {state === 'error' && (
          <section className="section">
            <div className="error-banner">
              <span className="error-banner__icon">⚠</span>
              <span>{errorMsg}</span>
            </div>
          </section>
        )}

        {state === 'done' && result && (
          <>
            <section className="section section--meta">
              <p className="result-meta">
                Results for{' '}
                <a
                  className="result-link"
                  href={`https://github.com/${result.repo}/pull/${result.pr_number}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  {result.repo} #{result.pr_number}
                </a>
              </p>
            </section>

            <section className="section section--findings">
              <div className="findings-grid">
                <FindingsCard
                  title="Security"
                  findings={result.security_findings}
                  accent="red"
                />
                <FindingsCard
                  title="Style"
                  findings={result.style_findings}
                  accent="blue"
                />
                <FindingsCard
                  title="Tests"
                  findings={result.test_findings}
                  accent="green"
                />
              </div>
            </section>

            <section className="section section--verdict">
              <VerdictBadge verdict={result.final_verdict} onReset={handleReset} />
            </section>
          </>
        )}
      </main>
    </div>
  )
}
