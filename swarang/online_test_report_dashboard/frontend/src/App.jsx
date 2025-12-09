
import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import axios from "axios";
import "./App.css";

ChartJS.register(ArcElement, Tooltip, Legend);

const twoColors = (mainColor) => {
  return [mainColor, "rgba(220,220,220,0.4)"];
}

export default function App(){
  const [data, setData] = useState(null);
  const [includeProctoring, setIncludeProctoring] = useState(true);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);

  useEffect(()=>{
    axios.get("http://localhost:8000/api/sample").then(r=> setData(r.data)).catch(e=>{
      setData({
        candidate: {name:"John Doe", email:"john@example.com", id:"CAND123", exam:"Full Stack Test", date:"2025-12-06", duration:"120 minutes"},
        mcq: {
          max_marks:50, 
          marks_obtained:38, 
          correct:19, 
          wrong:6, 
          questions:[
            {id:1, question:"What is the correct way to declare a variable in JavaScript?", is_correct:true, marks:2, options:["var x = 5;", "variable x = 5;", "x = 5;", "int x = 5;"], correct:"var x = 5;", given_answer:"var x = 5;"},
            {id:2, question:"Which of the following is NOT a valid CSS selector?", is_correct:false, marks:2, options:[".classname", "#idname", "::before", "&element"], correct:"&element", given_answer:"::before"},
            {id:3, question:"What does REST stand for?", is_correct:true, marks:2, options:["Representational State Transfer", "Remote Server Transfer", "Request State Transfer", "Response State Transfer"], correct:"Representational State Transfer", given_answer:"Representational State Transfer"},
            {id:4, question:"Which HTTP method is used to update a resource?", is_correct:true, marks:2, options:["GET", "PUT", "DELETE", "POST"], correct:"PUT", given_answer:"PUT"},
            {id:5, question:"What is the time complexity of binary search?", is_correct:false, marks:2, options:["O(n)", "O(log n)", "O(n²)", "O(1)"], correct:"O(log n)", given_answer:"O(n)"}
          ]
        },
        coding: {
          max_marks:50, 
          marks_obtained:42, 
          output_ok:true, 
          questions:[
            {id:1, title:"Reverse a String", description:"Write a function to reverse a string without using built-in methods", difficulty:"Easy", marks:10, output_correct:true, given_answer:"function reverseString(s) {\\n  let result = '';\\n  for(let i = s.length - 1; i >= 0; i--) {\\n    result += s[i];\\n  }\\n  return result;\\n}"},
            {id:2, title:"Find Missing Number", description:"Given an array of n-1 integers from 1 to n, find the missing number", difficulty:"Medium", marks:15, output_correct:true, given_answer:"function findMissing(arr) {\\n  const n = arr.length + 1;\\n  const sum = (n * (n + 1)) / 2;\\n  const arrSum = arr.reduce((a, b) => a + b, 0);\\n  return sum - arrSum;\\n}"},
            {id:3, title:"Longest Palindrome", description:"Find the length of the longest palindromic substring in a string", difficulty:"Hard", marks:25, output_correct:true, given_answer:"function longestPalindrome(s) {\\n  if(s.length < 2) return s;\\n  let longest = s[0];\\n  for(let i = 0; i < s.length; i++) {\\n    for(let j = i + 1; j <= s.length; j++) {\\n      const sub = s.slice(i, j);\\n      if(sub === sub.split('').reverse().join('') && sub.length > longest.length) {\\n        longest = sub;\\n      }\\n    }\\n  }\\n  return longest;\\n}"}
          ]
        },
        proctoring: {flagged_faces:0, focus_deviation_percent:4.5, cheating_events:0, unusual_activity:"Normal"}
      });
    })
  },[]);

  if(!data) return (
    <div className="loader">
      <div className="spinner"></div>
      <p>Loading Report...</p>
    </div>
  );

  // Safe percentage calculations with division by zero protection
  const mcqMax = data.mcq?.max_marks || 0;
  const mcqObtained = data.mcq?.marks_obtained || 0;
  const mcqPct = mcqMax > 0 ? (mcqObtained / mcqMax) * 100 : 0;
  
  const codingMax = data.coding?.max_marks || 0;
  const codingObtained = data.coding?.marks_obtained || 0;
  
  // For coding: if max_marks is 0, calculate attempt percentage instead
  let codingPct = 0;
  let codingAttempted = 0;
  let codingTotal = 0;
  if (codingMax > 0) {
    codingPct = (codingObtained / codingMax) * 100;
  } else {
    // Calculate attempt percentage based on questions
    const codingQuestions = data.coding?.questions || [];
    codingTotal = codingQuestions.length;
    codingAttempted = codingQuestions.filter(q => q.given_answer || q.output_correct !== undefined).length;
    codingPct = codingTotal > 0 ? (codingAttempted / codingTotal) * 100 : 0;
  }
  
  const totalMarks = mcqMax + codingMax;
  const totalObtained = mcqObtained + codingObtained;
  const totalPct = totalMarks > 0 ? (totalObtained / totalMarks) * 100 : 0;

  const mcqChart = {
    labels: ["Obtained","Remaining"],
    datasets: [{
      data: [
        data.mcq?.marks_obtained || 0, 
        Math.max(0, (data.mcq?.max_marks || 0) - (data.mcq?.marks_obtained || 0))
      ],
      backgroundColor: ["#3B82F6", "rgba(59, 130, 246, 0.15)"],
      borderColor: ["#3B82F6", "#E5E7EB"],
      borderWidth: 2,
      hoverOffset: 6
    }]
  };

  const codingChart = {
    labels: codingMax > 0 ? ["Obtained","Remaining"] : ["Attempted","Remaining"],
    datasets: [{
      data: codingMax > 0 
        ? [
            data.coding?.marks_obtained || 0, 
            Math.max(0, (data.coding?.max_marks || 0) - (data.coding?.marks_obtained || 0))
          ]
        : [
            codingAttempted,
            Math.max(0, codingTotal - codingAttempted)
          ],
      backgroundColor: ["#10B981", "rgba(16, 185, 129, 0.15)"],
      borderColor: ["#10B981", "#E5E7EB"],
      borderWidth: 2,
      hoverOffset: 6
    }]
  };

  // Calculate proctoring compliance score (100 - focus deviation = compliance)
  const focusDeviation = data.proctoring?.focus_deviation_percent || 0;
  const proctoringCompliance = Math.max(0, Math.min(100, 100 - focusDeviation));
  const proctoringChart = {
    labels: ["Compliant","Non-Compliant"],
    datasets: [{
      data: [
        proctoringCompliance,
        Math.max(0, 100 - proctoringCompliance)
      ],
      backgroundColor: ["#f59e0b", "rgba(245, 158, 11, 0.15)"],
      borderColor: ["#f59e0b", "#E5E7EB"],
      borderWidth: 2,
      hoverOffset: 6
    }]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: "bottom",
        labels: { font: { size: 11, family: "'Inter', sans-serif" }, padding: 15, usePointStyle: true }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return context.label + ": " + context.parsed;
          }
        }
      }
    }
  };

  const downloadDashboardPdf = async () => {
    if (!data) {
      alert("No data available to generate PDF");
      return;
    }

    setIsGeneratingPdf(true);
    try {
      // Prepare payload with current data and proctoring preference
      const payload = {
        candidate: data.candidate || {},
        mcq: data.mcq || {},
        coding: data.coding || {},
        proctoring: includeProctoring ? (data.proctoring || {}) : null,
        include_proctoring: includeProctoring
      };

      // Generate new PDF with current data
      const resp = await axios.post(
        "http://localhost:8000/api/report",
        payload,
        { responseType: "blob" }
      );
      
      const blob = new Blob([resp.data], {type: "application/pdf"});
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${data.candidate?.name || 'report'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error("PDF generation error:", e);
      const errorMsg = e.response?.data 
        ? `Failed to generate PDF: ${e.response.data.detail || e.response.statusText}`
        : `Failed to generate PDF: ${e.message}`;
      alert(errorMsg);
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const getScoreColor = (pct) => {
    if (pct >= 80) return "#10B981";
    if (pct >= 60) return "#F59E0B";
    return "#EF4444";
  };

  return (
    <div className="app-container">
      <style>{`
        @import url('https://rsms.me/inter/inter.css');
        
        * {
          font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
      `}</style>
      
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div>
            <h1>EXAMINATION REPORT</h1>
            <p>Comprehensive Exam Performance Analysis</p>
          </div>
          <div style={{display: "flex", gap: "12px", alignItems: "center"}}>
            <label className="checkbox-label" style={{color: "white", marginRight: "8px"}}>
              <input 
                type="checkbox" 
                checked={includeProctoring} 
                onChange={(e)=> setIncludeProctoring(e.target.checked)} 
                style={{width: "16px", height: "16px", cursor: "pointer"}}
              />
              <span style={{fontSize: "13px", fontWeight: 500}}>Include Proctoring</span>
            </label>
            <button 
              onClick={downloadDashboardPdf} 
              className="download-btn"
              disabled={isGeneratingPdf}
            >
              {isGeneratingPdf ? "Generating PDF..." : "Download PDF Report"}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container">
        {/* Candidate Card */}
        <section className="card candidate-card">
          <div className="candidate-header">
            <div>
              <h2>{data.candidate.name}</h2>
              <p className="exam-title">{data.candidate.exam}</p>
            </div>
          </div>
          
          <div className="candidate-details">
            <div className="detail-item">
              <span className="label">Email</span>
              <span className="value">{data.candidate.email}</span>
            </div>
            <div className="detail-item">
              <span className="label">Candidate ID</span>
              <span className="value">{data.candidate.id}</span>
            </div>
            <div className="detail-item">
              <span className="label">Date</span>
              <span className="value">{data.candidate.date || "N/A"}</span>
            </div>
            <div className="detail-item">
              <span className="label">Duration</span>
              <span className="value">{data.candidate.duration || "120 minutes"}</span>
            </div>
          </div>
        </section>

        {/* Score Overview */}
        <section className="score-overview">
          {(data.mcq?.max_marks || data.mcq?.questions?.length) ? (
            <div className="score-card mcq-card">
              <div className="score-chart">
                <Doughnut data={mcqChart} options={chartOptions} height={160} />
              </div>
              <div className="score-info">
                <h3>MCQ Section</h3>
                <p className="score-pct" style={{color: getScoreColor(mcqPct)}}>{mcqPct.toFixed(1)}%</p>
                <p className="score-detail">{data.mcq?.marks_obtained || 0}/{data.mcq?.max_marks || 0} marks</p>
                <div className="score-breakdown">
                  <span className="correct">✓ {data.mcq?.correct || 0} Correct</span>
                  <span className="wrong">✗ {data.mcq?.wrong || 0} Wrong</span>
                </div>
              </div>
            </div>
          ) : null}
          {(data.coding?.max_marks || data.coding?.questions?.length) ? (
            <div className="score-card coding-card">
              <div className="score-chart">
                <Doughnut data={codingChart} options={chartOptions} height={160} />
              </div>
              <div className="score-info">
                <h3>Coding Section</h3>
                <p className="score-pct" style={{color: getScoreColor(codingPct)}}>{codingPct.toFixed(1)}%</p>
                {codingMax > 0 ? (
                  <>
                    <p className="score-detail">{data.coding?.marks_obtained || 0}/{data.coding?.max_marks || 0} marks</p>
                    <div className="score-breakdown">
                      <span className={data.coding?.output_ok ? "correct" : "wrong"}>
                        {data.coding?.output_ok ? "✓ Output Correct" : "✗ Output Failed"}
                      </span>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="score-detail">{codingAttempted}/{codingTotal} questions attempted</p>
                    <div className="score-breakdown">
                      <span style={{color: "#6B7280"}}>Questions Completed</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          ) : null}
          {includeProctoring && data.proctoring ? (
            <div className="score-card proctoring-card">
              <div className="score-chart">
                <Doughnut data={proctoringChart} options={chartOptions} height={160} />
              </div>
              <div className="score-info">
                <h3>Proctoring Compliance</h3>
                <p className="score-pct" style={{color: getScoreColor(proctoringCompliance)}}>{proctoringCompliance.toFixed(1)}%</p>
                <p className="score-detail">Deviation: {focusDeviation.toFixed(1)}%</p>
                <div className="score-breakdown">
                  <span className={proctoringCompliance >= 80 ? "correct" : proctoringCompliance >= 60 ? "wrong" : "wrong"}>
                    {proctoringCompliance >= 80 ? "✓ Good Compliance" : proctoringCompliance >= 60 ? "⚠ Moderate Compliance" : "✗ Low Compliance"}
                  </span>
                </div>
              </div>
            </div>
          ) : null}
        </section>

        {/* MCQ Questions Section */}
        {(data.mcq?.questions || []).length > 0 && (
          <section className="card questions-section">
            <h3>MCQ QUESTIONS REVIEW ({(data.mcq?.questions || []).length})</h3>
            <div className="questions-list">
              {(data.mcq?.questions || []).map((q, idx) => (
                <div key={idx} className={`question-card ${q.is_correct ? "correct" : "incorrect"}`}>
                  <div className="question-header">
                    <h4>Q{q.id}: {q.question}</h4>
                    <span className={`status-badge ${q.is_correct ? "success" : "error"}`}>
                      {q.is_correct ? "✓ Correct" : "✗ Incorrect"}
                    </span>
                  </div>
                  
                  <div className="options-container">
                    {q.options?.map((opt, i) => (
                      <div 
                        key={i} 
                        className={`option ${opt === q.correct ? "correct-ans" : ""} ${opt === q.given_answer && !q.is_correct ? "wrong-ans" : ""}`}
                      >
                        <span className="option-letter">{String.fromCharCode(65 + i)}</span>
                        <span>{opt}</span>
                        {opt === q.correct && <span className="marker">✓ Correct</span>}
                        {opt === q.given_answer && !q.is_correct && <span className="marker error">✗ Your answer</span>}
                      </div>
                    ))}
                  </div>
                  
                  <div className="question-footer">
                    <span className="marks-earned">Marks: {q.marks}</span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Coding Questions Section */}
        {(data.coding?.questions || []).length > 0 && (
          <section className="card questions-section">
            <h3>CODING QUESTIONS REVIEW ({(data.coding?.questions || []).length})</h3>
            <div className="questions-list">
              {(data.coding?.questions || []).map((q, idx) => (
                <div key={idx} className={`question-card ${q.output_correct ? "correct" : "incorrect"}`}>
                  <div className="question-header">
                    <div>
                      <h4>Q{q.id}: {q.title}</h4>
                      <p className="question-desc">{q.description}</p>
                    </div>
                    <span className={`difficulty-badge ${q.difficulty.toLowerCase()}`}>
                      {q.difficulty}
                    </span>
                  </div>

                  <div className="code-section">
                    <p className="code-label">Your Solution:</p>
                    <pre className="code-block"><code>{q.given_answer}</code></pre>
                  </div>

                  <div className="question-footer">
                    {q.marks ? (
                      <span className="marks-earned">Marks: {q.marks}</span>
                    ) : (
                      <span className="marks-earned">Attempt: Completed</span>
                    )}
                    <span className={`output-status ${q.output_correct ? "success" : "error"}`}>
                      {q.output_correct ? "✓ Output Correct" : "✗ Output Incorrect"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Proctoring Section */}
        {includeProctoring && data.proctoring && (
          <section className="card proctoring-section">
            <div className="section-header">
              <h3>PROCTORING REPORT</h3>
            </div>

            <div className="proctoring-grid">
              <div className="proctoring-item">
                <span className="proctoring-label">Flagged Faces</span>
                <span className="proctoring-value">{data.proctoring.flagged_faces}</span>
              </div>
              <div className="proctoring-item">
                <span className="proctoring-label">Focus Deviation</span>
                <span className="proctoring-value">{data.proctoring.focus_deviation_percent}%</span>
              </div>
              <div className="proctoring-item">
                <span className="proctoring-label">Cheating Events</span>
                <span className="proctoring-value">{data.proctoring.cheating_events}</span>
              </div>
              <div className="proctoring-item">
                <span className="proctoring-label">Activity Status</span>
                <span className="proctoring-value">{data.proctoring.unusual_activity || "Normal"}</span>
              </div>
            </div>
          </section>
        )}
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>© 2025 Online Test Platform. All rights reserved.</p>
      </footer>
    </div>
  )
}
