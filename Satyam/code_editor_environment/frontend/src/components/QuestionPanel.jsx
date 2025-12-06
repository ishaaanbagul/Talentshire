import React from 'react'

export default function QuestionPanel({ question }) {
  if (!question) return <div className="question-panel">Loading question...</div>

  return (
    <div className="question-panel">
      <h2>{question.title}</h2>
      <p>{question.body}</p>
      <div className="meta">
        <strong>Difficulty:</strong> {question.difficulty}
      </div>
      <div className="samples">
        <h4>Sample Input</h4>
        <pre>{question.sample_input}</pre>
        <h4>Sample Output</h4>
        <pre>{question.sample_output}</pre>
        <h4>Constraints</h4>
        <pre>{question.constraints}</pre>
      </div>
    </div>
  )
}
