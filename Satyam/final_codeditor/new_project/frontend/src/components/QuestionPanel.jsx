import React, { useEffect } from 'react'

export default function QuestionPanel({ question, problemId, loading }) {
  useEffect(() => {
    console.log('QuestionPanel received:', { question, problemId, loading })
  }, [question, loading, problemId])

  return (
    <div className="question-panel">
      {/* Problem ID Display (Read-only, from URL) */}
      <div style={{
        display: 'flex',
        gap: '10px',
        alignItems: 'center',
        padding: '10px',
        background: '#0f1724',
        borderRadius: '4px',
        marginBottom: '12px'
      }}>
        <label style={{ fontWeight: 'bold', minWidth: '80px' }}>Problem ID:</label>
        <span style={{
          padding: '6px 10px',
          background: '#1e293b',
          border: '1px solid #3e3e42',
          color: '#e6eef6',
          borderRadius: '4px',
          fontSize: '13px',
          flex: '1'
        }}>
          {problemId}
        </span>
      </div>

      {/* Loading State */}
      {loading && (
        <div style={{
          textAlign: 'center',
          color: '#9aa4b2',
          padding: '40px 20px',
          fontSize: '14px'
        }}>
          ⏳ Loading problem...
        </div>
      )}

      {/* Problem Data */}
      {!loading && question && (
        <>
          <h2 style={{ color: '#10b981', margin: '0 0 10px 0', fontSize: '1.3rem' }}>
            {question.title}
          </h2>
          <p style={{ color: '#cbd5e1', lineHeight: '1.6', margin: '8px 0' }}>
            <strong>Description:</strong> {question.description}
          </p>
          <div style={{ background: '#0f1724', padding: '10px', borderRadius: '4px', color: '#cbd5e1' }}>
            <strong>Difficulty:</strong> {question.difficulty}
          </div>
          <div style={{ background: '#0f1724', padding: '10px', borderRadius: '4px', color: '#cbd5e1' }}>
            <strong>Labels:</strong> {(question.labels || []).join(', ')}
          </div>
          <div style={{ background: '#0f1724', padding: '10px', borderRadius: '4px', color: '#cbd5e1' }}>
            <strong>Constraints:</strong> {question.constraints}
          </div>
          <div style={{ marginTop: '12px' }}>
            <h4 style={{ color: '#10b981', margin: '0 0 8px 0' }}>Sample Input:</h4>
            <pre style={{
              background: '#0f1724',
              padding: '10px',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#cbd5e1',
              border: '1px solid #3e3e42',
              margin: '0 0 12px 0',
              overflow: 'auto'
            }}>{question.sample_input}</pre>
          </div>
          <div>
            <h4 style={{ color: '#10b981', margin: '0 0 8px 0' }}>Expected Output:</h4>
            <pre style={{
              background: '#0f1724',
              padding: '10px',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#cbd5e1',
              border: '1px solid #3e3e42',
              margin: '0',
              overflow: 'auto'
            }}>{question.sample_output}</pre>
          </div>
        </>
      )}

      {/* No Data State */}
      {!loading && !question && (
        <div style={{
          textAlign: 'center',
          color: '#9aa4b2',
          padding: '40px 20px',
          fontSize: '14px'
        }}>
          ❌ No problem found
        </div>
      )}
    </div>
  )
}
