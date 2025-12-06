import React, { useEffect, useState } from 'react'
import axios from 'axios'
import EditorPanel from './components/EditorPanel'
import QuestionPanel from './components/QuestionPanel'

export default function App() {
  const [question, setQuestion] = useState(null)

  useEffect(() => {
    axios.get('http://localhost:8000/question').then((res) => setQuestion(res.data)).catch(console.error)
  }, [])

  return (
    <div className="app-grid">
      <div className="left">
        <QuestionPanel question={question} />
      </div>
      <div className="right">
        <EditorPanel />
      </div>
    </div>
  )
}
