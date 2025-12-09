import React, { useEffect, useState } from 'react'
import axios from 'axios'
import EditorPanel from './components/EditorPanel'
import QuestionPanel from './components/QuestionPanel'

export default function App() {
  const [question, setQuestion] = useState(null)
  // Get problemId from URL params: ?problemId=1
  const [problemId, setProblemId] = useState(() => {
    const params = new URLSearchParams(window.location.search)
    const id = params.get('problemId')
    console.log('[App] Problem ID from URL:', id)
    return id || '1'  // Default to '1' if not provided
  })
  const [loading, setLoading] = useState(true)

  // Fetch problem whenever problemId changes
  useEffect(() => {
    const fetchProblem = async () => {
      console.log('[App] Fetching problem:', problemId)
      try {
        setLoading(true)
        const response = await axios.get(`/api/problem/${problemId}`)
        console.log('[App] Problem fetched:', response.data)
        setQuestion(response.data)
      } catch (error) {
        console.error('[App] Error fetching problem:', error.message)
        setQuestion(null)
      } finally {
        setLoading(false)
      }
    }

    fetchProblem()
  }, [problemId])

  return (
    <div className="app-grid">
      <div className="left">
        <QuestionPanel 
          question={question} 
          problemId={problemId} 
          loading={loading} 
        />
      </div>
      <div className="right">
        <EditorPanel 
          externalProblemId={problemId}
          question={question}
        />
      </div>
    </div>
  )
}
