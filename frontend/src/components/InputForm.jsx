import { useState } from 'react'

const PR_URL_RE = /github\.com\/([^/]+\/[^/]+)\/pull\/(\d+)/

export default function InputForm({ onSubmit, loading }) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    setError('')

    const match = url.trim().match(PR_URL_RE)
    if (!match) {
      setError('Invalid GitHub PR URL. Expected: https://github.com/owner/repo/pull/123')
      return
    }

    const [, repo, prStr] = match
    onSubmit({ repo, pr_number: parseInt(prStr, 10) })
  }

  return (
    <form className="input-form" onSubmit={handleSubmit}>
      <div className="input-row">
        <input
          className={`url-input${error ? ' url-input--error' : ''}`}
          type="text"
          placeholder="https://github.com/owner/repo/pull/123"
          value={url}
          onChange={e => { setUrl(e.target.value); setError('') }}
          disabled={loading}
          spellCheck={false}
        />
        <button className="submit-btn" type="submit" disabled={loading || !url.trim()}>
          Review PR
        </button>
      </div>
      {error && <p className="inline-error">{error}</p>}
    </form>
  )
}
