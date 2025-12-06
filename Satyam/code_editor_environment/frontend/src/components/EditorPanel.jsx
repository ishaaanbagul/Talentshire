import React, { useState } from 'react'
import Editor from '@monaco-editor/react'
import axios from 'axios'

const LANGUAGES = [
  { name: 'Python', value: 'python' },
  { name: 'Java', value: 'java' },
  { name: 'SQL', value: 'sql' },
]

export default function EditorPanel() {
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState('x = 5\ny = 3\nprint(x + y)')
  const [stdin, setStdin] = useState('')
  const [output, setOutput] = useState('')
  const [running, setRunning] = useState(false)

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
      }

      console.log('Sending payload:', payload)

      const res = await axios.post('http://localhost:8000/run', payload)
      const data = res.data
      
      console.log('Response:', data)
      
      // Extract just the output
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
      
      setOutput(output || '(No output)')
    } catch (err) {
      const errMsg = err.response?.data?.detail || err.response?.data?.message || err.message
      setOutput('[Error]\n' + errMsg)
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="editor-container">
      <div className="editor-header">
        <div className="header-controls">
          <div className="control-group">
            <label>Language:</label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)} className="language-select">
              {LANGUAGES.map(lang => (
                <option key={lang.value} value={lang.value}>{lang.name}</option>
              ))}
            </select>
          </div>
          <button onClick={run} disabled={running} className="run-btn">
            {running ? 'Running...' : '▶ Run Code'}
          </button>
        </div>
      </div>

      <div className="code-section">
        <h4>Code</h4>
        <div className="editor-wrapper">
          <Editor 
            height="45vh" 
            language={language} 
            defaultValue={code} 
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
          <h4>Input (stdin)</h4>
          <textarea 
            value={stdin} 
            onChange={(e) => setStdin(e.target.value)}
            placeholder="Enter input values here&#10;Each value on a new line&#10;(for input() prompts)"
            className="input-textarea"
          />
          <small className="input-hint">💡 Tip: If code has input('enter num:'), just type the number here</small>
        </div>

        <div className="output-area">
          <h4>Output</h4>
          <pre className="output-console">{output || '(No output yet)'}</pre>
        </div>
      </div>
    </div>
  )
}
