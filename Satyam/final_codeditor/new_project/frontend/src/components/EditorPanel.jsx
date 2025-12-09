import React, { useState, useEffect } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'

const LANGUAGES = [
  { name: 'Python', value: 'python' },
  { name: 'Java', value: 'java' },
  { name: 'SQL', value: 'sql' },
  { name: 'PySpark', value: 'pyspark' },
]

// Service URLs - Use relative URLs so nginx proxy handles routing
const EXECUTION_SERVICE_URL = '/api'
const PROBLEM_SERVICE_URL = '/api'
const SUBMISSION_SERVICE_URL = '/api'

// Parse input() calls from code
function parseInputPrompts(code) {
  const prompts = []
  
  // Match input() calls with or without prompts
  // Matches: input(), input("prompt"), input('prompt')
  const inputRegex = /input\s*\(\s*["']?([^"']*?)["']?\s*\)/g
  let match
  
  while ((match = inputRegex.exec(code)) !== null) {
    const prompt = match[1] || `Enter value ${prompts.length + 1}:`
    prompts.push(prompt)
  }
  
  return prompts
}

export default function EditorPanel({ externalProblemId, setExternalProblemId, question }) {
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('x = 5\ny = 3\nprint(x + y)')
  const [stdin, setStdin] = useState('')
  const [output, setOutput] = useState('')
  const [running, setRunning] = useState(false)
  const [inputPrompts, setInputPrompts] = useState([])
  // NOTE: problemId and problemData are ONLY internal use, NEVER rendered
  const [problemId] = useState(externalProblemId || '')
  const [problemData] = useState(null) // NEVER used in render
  const [userId, setUserId] = useState('user_' + Math.random().toString(36).substr(2, 9))
  const [lastSaved, setLastSaved] = useState(null)
  const [draftLoaded, setDraftLoaded] = useState(false)

  // Auto-populate stdin from problem's sample_input when problem changes
  useEffect(() => {
    if (question && question.sample_input) {
      console.log('EditorPanel: Auto-populating stdin from sample_input')
      setStdin(question.sample_input)
      setOutput('') // Clear previous output when new problem loads
      console.log('✓ Input field auto-populated with sample input')
    }
  }, [question])

  // Load draft on component mount
  useEffect(() => {
    const loadDraft = async () => {
      if (!problemId || draftLoaded) return
      
      try {
        const res = await axios.get(`${SUBMISSION_SERVICE_URL}/draft/${userId}/${problemId}`)
        if (res.data.status !== 'no_draft') {
          setCode(res.data.code || '')
          setLanguage(res.data.language || 'python')
          setOutput(`📝 Draft recovered from ${new Date(res.data.last_saved).toLocaleTimeString()}`)
          setDraftLoaded(true)
        }
      } catch (err) {
        console.log('No draft found or error loading draft')
      }
    }
    
    loadDraft()
  }, [problemId])

  // Auto-save draft every 5 seconds
  useEffect(() => {
    const autoSaveInterval = setInterval(async () => {
      if (code.trim() && problemId) {
        try {
          await axios.post(`${SUBMISSION_SERVICE_URL}/draft`, {
            user_id: userId,
            problem_id: problemId,
            language: language,
            code: code,
            cursor_position: 0,
            status: 'draft'
          })
          setLastSaved(new Date())
          console.log('✓ Draft auto-saved')
        } catch (err) {
          console.log('Draft auto-save failed:', err.message)
        }
      }
    }, 5000) // Save every 5 seconds
    
    return () => clearInterval(autoSaveInterval)
  }, [code, language, problemId, userId])

  // Update input prompts when code changes
  useEffect(() => {
    const prompts = parseInputPrompts(code)
    setInputPrompts(prompts)
  }, [code])

  // Fetch problem when problem ID changes
  async function fetchProblem(id) {
    if (!id) {
      setProblemData(null)
      return
    }
    
    try {
      const res = await axios.get(`${PROBLEM_SERVICE_URL}/problem/${id}`)
      setProblemData(res.data)
      setOutput(`✓ Problem loaded: ${res.data.title}`)
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message
      setOutput(`[Error] Failed to load problem: ${errMsg}`)
    }
  }

  async function run() {
    if (!code.trim()) {
      setOutput('[Error]\nPlease write some code first!')
      return
    }

    setRunning(true)
    setOutput('')
    try {
      const payload = {
        language: language,
        version: null,
        files: [{ name: 'main', content: code }],
        stdin: stdin,
        problem_id: problemId || null,
        user_id: userId
      }

      console.log('Calling Execution Service:', EXECUTION_SERVICE_URL)
      console.log('Sending payload:', payload)

      // Call Execution Service (Port 8001)
      const res = await axios.post(`${EXECUTION_SERVICE_URL}/run`, payload)
      const data = res.data
      
      console.log('Response:', data)
      
      // Extract output
      let output = ''
      if (data.run && data.run.stdout) {
        output = data.run.stdout
      } else if (data.run && data.run.output) {
        output = data.run.output
      } else {
        output = JSON.stringify(data, null, 2)
      }
      
      // If there's stderr, append it
      if (data.run && data.run.stderr && data.run.stderr.trim()) {
        output += '\n[Error]\n' + data.run.stderr
      }
      
      // Check if output matches expected output
      let testMessage = ''
      if (question && question.expected_output) {
        const expectedOutput = question.expected_output.trim()
        const actualOutput = output.trim()
        
        if (actualOutput === expectedOutput) {
          testMessage = '\n\n✅ Test Case PASSED\nExpected: ' + expectedOutput + ' | Got: ' + actualOutput
        } else {
          testMessage = '\n\n❌ Test Case FAILED\nExpected: ' + expectedOutput + ' | Got: ' + actualOutput
        }
      }
      
      setOutput((output || '(No output)') + testMessage)
    } catch (err) {
      console.error('Error:', err)
      const errMsg = err.response?.data?.detail || err.response?.data?.message || err.message
      setOutput('[Error]\n' + errMsg)
    } finally {
      setRunning(false)
    }
  }

  async function submitCode() {
    if (!code.trim()) {
      setOutput('[Error]\nPlease write some code first!')
      return
    }

    try {
      const payload = {
        user_id: userId,
        problem_id: problemId || 'unknown',
        language: language,
        code: code,
        stdin: stdin
      }

      console.log('Calling Submission Service:', SUBMISSION_SERVICE_URL)
      
      // Call Submission Service (Port 8003)
      const res = await axios.post(`${SUBMISSION_SERVICE_URL}/submission`, payload)
      setOutput(`✓ Code submitted successfully!\nSubmission ID: ${res.data.submission_id}`)
      
      // Delete draft after successful submission
      if (problemId) {
        try {
          await axios.delete(`${SUBMISSION_SERVICE_URL}/draft/${userId}/${problemId}`)
          console.log('✓ Draft cleared after submission')
        } catch (err) {
          console.log('Could not delete draft:', err.message)
        }
      }
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.message
      setOutput('[Error]\nFailed to submit: ' + errMsg)
    }
  }

  return (
    <div className="editor-container" style={{ backgroundColor: '#1e1e1e', color: '#e0e0e0' }}>
      {/* HEADER SECTION - Language, Run, Submit, Autosave only */}
      <div className="editor-header">
        <div className="header-controls">
          {/* Language Selector */}
          <div className="control-group">
            <label>Language:</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)} className="language-select">
              {LANGUAGES.map(lang => (
                <option key={lang.value} value={lang.value}>{lang.name}</option>
              ))}
            </select>
          </div>

          {/* Run & Submit Buttons */}
          <button onClick={run} disabled={running} className="run-btn">
            {running ? 'Running...' : '▶ Run Code'}
          </button>
          <button onClick={submitCode} disabled={running} className="submit-btn">
            📤 Submit
          </button>

          {/* Auto-save Status */}
          {lastSaved && (
            <div className="auto-save-status">
              💾 Saved: {lastSaved.toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>

      {/* CODE EDITOR SECTION - ONLY CODE, NO PROBLEM INFO */}
      <div className="code-section">
        <h4>Code</h4>
        <div className="editor-wrapper">
          <Editor 
            height="40vh" 
            language={language} 
            value={code}
            onChange={(v) => setCode(v || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
            }}
          />
        </div>
      </div>

      <div className="io-section">
        <div className="input-area">
          <h4>
            Input (stdin) 
            {question && question.sample_input ? (
              <span style={{fontSize: '0.85em', color: '#88dd88', marginLeft: '10px'}}>
                ✓ Auto-filled from sample input
              </span>
            ) : null}
          </h4>
          {inputPrompts.length > 0 && (
            <div className="input-prompts">
              <small style={{color: '#88dd88'}}>📝 Code expects input:</small>
              {inputPrompts.map((prompt, idx) => (
                <small key={idx} style={{display: 'block', color: '#88dd88'}}>
                  → {prompt}
                </small>
              ))}
            </div>
          )}
          <textarea 
            value={stdin} 
            onChange={(e) => setStdin(e.target.value)}
            placeholder="Enter input values here&#10;Each value on a new line&#10;(for input() prompts)"
            className="input-textarea"
          />
          <small className="input-hint">💡 Sample input auto-filled. Edit if needed for custom testing</small>
        </div>

        <div className="output-area">
          <h4>Output</h4>
          <pre className="output-console">{output || '(No output yet)'}</pre>
          {output && output.includes('✅ Test Case PASSED') && (
            <div style={{color: '#4ade80', fontWeight: 'bold', marginTop: '10px', fontSize: '14px'}}>
              ✅ Test Case PASSED
            </div>
          )}
          {output && output.includes('❌ Test Case FAILED') && (
            <div style={{color: '#f87171', fontWeight: 'bold', marginTop: '10px', fontSize: '14px'}}>
              ❌ Test Case FAILED
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
