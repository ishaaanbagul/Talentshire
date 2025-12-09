import React, { useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";
import axios from "axios";
import "./App.css";

ChartJS.register(ArcElement, Tooltip, Legend);

const TestCases = () => {
  const [activeCase, setActiveCase] = useState("both");
  const [isGeneratingPdf, setIsGeneratingPdf] = useState(false);
  const [includeProctoring, setIncludeProctoring] = useState(true);

  // Test Case Data
  const testCases = {
    mcqOnly: {
      name: "Test Case 1: MCQ Questions Only",
      description: "Report containing only MCQ questions",
      data: {
        candidate: {
          name: "Alice Johnson",
          email: "alice@example.com",
          id: "CAND001",
          exam: "Full Stack Development",
          date: "2025-12-09",
          duration: "120 minutes"
        },
        mcq: {
          max_marks: 50,
          marks_obtained: 42,
          correct: 21,
          wrong: 4,
          questions: [
            {
              id: 1,
              question: "What is the correct way to declare a variable in JavaScript?",
              is_correct: true,
              marks: 2,
              options: ["var x = 5;", "variable x = 5;", "x = 5;", "int x = 5;"],
              correct: "var x = 5;",
              given_answer: "var x = 5;"
            },
            {
              id: 2,
              question: "Which of the following is NOT a valid CSS selector?",
              is_correct: false,
              marks: 2,
              options: [".classname", "#idname", "::before", "&element"],
              correct: "&element",
              given_answer: "::before"
            },
            {
              id: 3,
              question: "What does REST stand for?",
              is_correct: true,
              marks: 2,
              options: [
                "Representational State Transfer",
                "Remote Server Transfer",
                "Request State Transfer",
                "Response State Transfer"
              ],
              correct: "Representational State Transfer",
              given_answer: "Representational State Transfer"
            },
            {
              id: 4,
              question: "Which HTTP method is used to update a resource?",
              is_correct: true,
              marks: 2,
              options: ["GET", "PUT", "DELETE", "POST"],
              correct: "PUT",
              given_answer: "PUT"
            },
            {
              id: 5,
              question: "What is the time complexity of binary search?",
              is_correct: false,
              marks: 2,
              options: ["O(n)", "O(log n)", "O(n²)", "O(1)"],
              correct: "O(log n)",
              given_answer: "O(n)"
            }
          ]
        },
        coding: { max_marks: 0, marks_obtained: 0, output_ok: false, questions: [] },
        proctoring: {
          flagged_faces: 0,
          focus_deviation_percent: 2.5,
          cheating_events: 0,
          unusual_activity: "Normal"
        }
      }
    },
    codingOnly: {
      name: "Test Case 2: Coding Questions Only (No Marks - Attempt %)",
      description: "Report containing only coding questions without marks",
      data: {
        candidate: {
          name: "Bob Smith",
          email: "bob@example.com",
          id: "CAND002",
          exam: "Algorithm Challenge",
          date: "2025-12-09",
          duration: "120 minutes"
        },
        mcq: { max_marks: 0, marks_obtained: 0, correct: 0, wrong: 0, questions: [] },
        coding: {
          max_marks: 0,
          marks_obtained: 0,
          output_ok: false,
          questions: [
            {
              id: 1,
              title: "Reverse a String",
              description: "Write a function to reverse a string without using built-in methods",
              difficulty: "Easy",
              marks: 0,
              output_correct: true,
              given_answer: "function reverseString(s) {\n  let result = '';\n  for(let i = s.length - 1; i >= 0; i--) {\n    result += s[i];\n  }\n  return result;\n}",
              test_cases_passed: 5,
              test_cases_total: 5
            },
            {
              id: 2,
              title: "Find Missing Number",
              description: "Given an array of n-1 integers from 1 to n, find the missing number",
              difficulty: "Medium",
              marks: 0,
              output_correct: true,
              given_answer: "function findMissing(arr) {\n  const n = arr.length + 1;\n  const sum = (n * (n + 1)) / 2;\n  const arrSum = arr.reduce((a, b) => a + b, 0);\n  return sum - arrSum;\n}",
              test_cases_passed: 8,
              test_cases_total: 10
            },
            {
              id: 3,
              title: "Two Sum Problem",
              description: "Find two numbers in array that add up to target",
              difficulty: "Medium",
              marks: 0,
              output_correct: false,
              given_answer: "function twoSum(arr, target) {\n  for(let i = 0; i < arr.length; i++) {\n    for(let j = i + 1; j < arr.length; j++) {\n      if(arr[i] + arr[j] === target) return [i, j];\n    }\n  }\n}",
              test_cases_passed: 3,
              test_cases_total: 8
            }
          ]
        },
        proctoring: {
          flagged_faces: 1,
          focus_deviation_percent: 8.2,
          cheating_events: 0,
          unusual_activity: "Minor deviation detected"
        }
      }
    },
    both: {
      name: "Test Case 3: Both MCQ and Coding Questions",
      description: "Full report with both MCQ and coding sections",
      data: {
        candidate: {
          name: "Charlie Davis",
          email: "charlie@example.com",
          id: "CAND003",
          exam: "Full Stack Developer Certification",
          date: "2025-12-09",
          duration: "180 minutes"
        },
        mcq: {
          max_marks: 50,
          marks_obtained: 38,
          correct: 19,
          wrong: 6,
          questions: [
            {
              id: 1,
              question: "What is the correct way to declare a variable in JavaScript?",
              is_correct: true,
              marks: 2,
              options: ["var x = 5;", "variable x = 5;", "x = 5;", "int x = 5;"],
              correct: "var x = 5;",
              given_answer: "var x = 5;"
            },
            {
              id: 2,
              question: "Which of the following is NOT a valid CSS selector?",
              is_correct: false,
              marks: 2,
              options: [".classname", "#idname", "::before", "&element"],
              correct: "&element",
              given_answer: "::before"
            },
            {
              id: 3,
              question: "What does REST stand for?",
              is_correct: true,
              marks: 2,
              options: [
                "Representational State Transfer",
                "Remote Server Transfer",
                "Request State Transfer",
                "Response State Transfer"
              ],
              correct: "Representational State Transfer",
              given_answer: "Representational State Transfer"
            },
            {
              id: 4,
              question: "Which HTTP method is used to update a resource?",
              is_correct: true,
              marks: 2,
              options: ["GET", "PUT", "DELETE", "POST"],
              correct: "PUT",
              given_answer: "PUT"
            },
            {
              id: 5,
              question: "What is the time complexity of binary search?",
              is_correct: false,
              marks: 2,
              options: ["O(n)", "O(log n)", "O(n²)", "O(1)"],
              correct: "O(log n)",
              given_answer: "O(n)"
            }
          ]
        },
        coding: {
          max_marks: 50,
          marks_obtained: 42,
          output_ok: true,
          questions: [
            {
              id: 1,
              title: "Reverse a String",
              description: "Write a function to reverse a string without using built-in methods",
              difficulty: "Easy",
              marks: 10,
              output_correct: true,
              given_answer: "function reverseString(s) {\n  let result = '';\n  for(let i = s.length - 1; i >= 0; i--) {\n    result += s[i];\n  }\n  return result;\n}",
              test_cases_passed: 5,
              test_cases_total: 5
            },
            {
              id: 2,
              title: "Find Missing Number",
              description: "Given an array of n-1 integers from 1 to n, find the missing number",
              difficulty: "Medium",
              marks: 15,
              output_correct: true,
              given_answer: "function findMissing(arr) {\n  const n = arr.length + 1;\n  const sum = (n * (n + 1)) / 2;\n  const arrSum = arr.reduce((a, b) => a + b, 0);\n  return sum - arrSum;\n}",
              test_cases_passed: 15,
              test_cases_total: 15
            },
            {
              id: 3,
              title: "Longest Palindrome",
              description: "Find the length of the longest palindromic substring in a string",
              difficulty: "Hard",
              marks: 25,
              output_correct: true,
              given_answer: "function longestPalindrome(s) {\n  if(s.length < 2) return s;\n  let longest = s[0];\n  for(let i = 0; i < s.length; i++) {\n    for(let j = i + 1; j <= s.length; j++) {\n      const sub = s.slice(i, j);\n      if(sub === sub.split('').reverse().join('') && sub.length > longest.length) {\n        longest = sub;\n      }\n    }\n  }\n  return longest;\n}",
              test_cases_passed: 22,
              test_cases_total: 25
            }
          ]
        },
        proctoring: {
          flagged_faces: 0,
          focus_deviation_percent: 4.5,
          cheating_events: 0,
          unusual_activity: "Normal"
        }
      }
    }
  };

  const currentCase = testCases[activeCase];
  const data = currentCase.data;

  // Safe percentage calculations
  const mcqMax = data.mcq?.max_marks || 0;
  const mcqObtained = data.mcq?.marks_obtained || 0;
  const mcqPct = mcqMax > 0 ? (mcqObtained / mcqMax) * 100 : 0;

  const codingMax = data.coding?.max_marks || 0;
  const codingObtained = data.coding?.marks_obtained || 0;

  let codingPct = 0;
  let codingAttempted = 0;
  let codingTotal = 0;
  if (codingMax > 0) {
    codingPct = (codingObtained / codingMax) * 100;
  } else {
    const codingQuestions = data.coding?.questions || [];
    codingTotal = codingQuestions.length;
    codingAttempted = codingQuestions.filter(
      (q) => q.given_answer || q.output_correct !== undefined
    ).length;
    codingPct = codingTotal > 0 ? (codingAttempted / codingTotal) * 100 : 0;
  }

  const totalMarks = mcqMax + codingMax;
  const totalObtained = mcqObtained + codingObtained;
  const totalPct = totalMarks > 0 ? (totalObtained / totalMarks) * 100 : 0;

  const mcqChart = {
    labels: ["Obtained", "Remaining"],
    datasets: [
      {
        data: [
          data.mcq?.marks_obtained || 0,
          Math.max(0, (data.mcq?.max_marks || 0) - (data.mcq?.marks_obtained || 0))
        ],
        backgroundColor: ["#2d5a87", "rgba(45, 90, 135, 0.15)"],
        borderColor: ["#2d5a87", "#E5E7EB"],
        borderWidth: 2,
        hoverOffset: 6
      }
    ]
  };

  const codingChart = {
    labels:
      codingMax > 0 ? ["Obtained", "Remaining"] : ["Attempted", "Remaining"],
    datasets: [
      {
        data:
          codingMax > 0
            ? [
                data.coding?.marks_obtained || 0,
                Math.max(0, (data.coding?.max_marks || 0) - (data.coding?.marks_obtained || 0))
              ]
            : [
                codingAttempted,
                Math.max(0, codingTotal - codingAttempted)
              ],
        backgroundColor: ["#0ea5e9", "rgba(14, 165, 233, 0.15)"],
        borderColor: ["#0ea5e9", "#E5E7EB"],
        borderWidth: 2,
        hoverOffset: 6
      }
    ]
  };

  const focusDeviation = data.proctoring?.focus_deviation_percent || 0;
  const proctoringCompliance = Math.max(0, Math.min(100, 100 - focusDeviation));
  const proctoringChart = {
    labels: ["Compliant", "Non-Compliant"],
    datasets: [
      {
        data: [proctoringCompliance, Math.max(0, 100 - proctoringCompliance)],
        backgroundColor: ["#f59e0b", "rgba(245, 158, 11, 0.15)"],
        borderColor: ["#f59e0b", "#E5E7EB"],
        borderWidth: 2,
        hoverOffset: 6
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          font: { size: 11, family: "'Inter', sans-serif" },
          padding: 15,
          usePointStyle: true
        }
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return context.label + ": " + context.parsed;
          }
        }
      }
    }
  };

  const downloadPdf = async () => {
    if (!data) {
      alert("No data available to generate PDF");
      return;
    }

    setIsGeneratingPdf(true);
    try {
      const payload = {
        candidate: data.candidate || {},
        mcq: data.mcq || {},
        coding: data.coding || {},
        proctoring: includeProctoring ? (data.proctoring || {}) : null,
        include_proctoring: includeProctoring
      };

      const resp = await axios.post("http://localhost:8000/api/report", payload, {
        responseType: "blob"
      });

      const blob = new Blob([resp.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${currentCase.name.replace(/[^a-zA-Z0-9]/g, "_")}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error("PDF generation error:", e);
      alert("Failed to generate PDF: " + (e.message || "Unknown error"));
    } finally {
      setIsGeneratingPdf(false);
    }
  };

  const getScoreColor = (pct) => {
    if (pct >= 80) return "#059669";
    if (pct >= 60) return "#f59e0b";
    return "#dc2626";
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div>
            <h1>EXAMINATION REPORT - TEST CASES</h1>
            <p>Interactive Test Case Demonstration</p>
          </div>
          <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
            <label className="checkbox-label" style={{ color: "white", marginRight: "8px" }}>
              <input
                type="checkbox"
                checked={includeProctoring}
                onChange={(e) => setIncludeProctoring(e.target.checked)}
                style={{ width: "16px", height: "16px", cursor: "pointer" }}
              />
              <span style={{ fontSize: "13px", fontWeight: 500 }}>
                Include Proctoring
              </span>
            </label>
            <button
              onClick={downloadPdf}
              className="download-btn"
              disabled={isGeneratingPdf}
            >
              {isGeneratingPdf ? "Generating PDF..." : "Download PDF Report"}
            </button>
          </div>
        </div>
      </header>

      {/* Test Case Selection */}
      <div className="container">
        <div className="card" style={{ marginBottom: "24px" }}>
          <h3 style={{ marginBottom: "16px", color: "#1e3a5f", fontWeight: 600 }}>
            Select Test Case
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "12px" }}>
            {Object.keys(testCases).map((key) => (
              <button
                key={key}
                onClick={() => setActiveCase(key)}
                style={{
                  padding: "16px",
                  border: activeCase === key ? "2px solid #1e3a5f" : "1px solid #cbd5e1",
                  borderRadius: "4px",
                  background: activeCase === key ? "#f8fafc" : "white",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 0.2s ease"
                }}
              >
                <div style={{ fontWeight: 600, color: "#1e3a5f", marginBottom: "4px" }}>
                  {testCases[key].name}
                </div>
                <div style={{ fontSize: "12px", color: "#6b7280" }}>
                  {testCases[key].description}
                </div>
              </button>
            ))}
          </div>
        </div>

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
                <p
                  className="score-pct"
                  style={{ color: getScoreColor(mcqPct) }}
                >
                  {mcqPct.toFixed(1)}%
                </p>
                <p className="score-detail">
                  {data.mcq?.marks_obtained || 0}/{data.mcq?.max_marks || 0} marks
                </p>
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
                <p
                  className="score-pct"
                  style={{ color: getScoreColor(codingPct) }}
                >
                  {codingPct.toFixed(1)}%
                </p>
                {codingMax > 0 ? (
                  <>
                    <p className="score-detail">
                      {data.coding?.marks_obtained || 0}/
                      {data.coding?.max_marks || 0} marks
                    </p>
                    <div className="score-breakdown">
                      <span
                        className={data.coding?.output_ok ? "correct" : "wrong"}
                      >
                        {data.coding?.output_ok
                          ? "✓ Output Correct"
                          : "✗ Output Failed"}
                      </span>
                    </div>
                  </>
                ) : (
                  <>
                    <p className="score-detail">
                      {codingAttempted}/{codingTotal} questions attempted
                    </p>
                    <div className="score-breakdown">
                      <span style={{ color: "#6b7280" }}>
                        Questions Completed
                      </span>
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
                <p
                  className="score-pct"
                  style={{ color: getScoreColor(proctoringCompliance) }}
                >
                  {proctoringCompliance.toFixed(1)}%
                </p>
                <p className="score-detail">
                  Deviation: {focusDeviation.toFixed(1)}%
                </p>
                <div className="score-breakdown">
                  <span
                    className={
                      proctoringCompliance >= 80
                        ? "correct"
                        : proctoringCompliance >= 60
                        ? "wrong"
                        : "wrong"
                    }
                  >
                    {proctoringCompliance >= 80
                      ? "✓ Good Compliance"
                      : proctoringCompliance >= 60
                      ? "⚠ Moderate Compliance"
                      : "✗ Low Compliance"}
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
                <div
                  key={idx}
                  className={`question-card ${
                    q.is_correct ? "correct" : "incorrect"
                  }`}
                >
                  <div className="question-header">
                    <h4>
                      Q{q.id}: {q.question}
                    </h4>
                    <span
                      className={`status-badge ${
                        q.is_correct ? "success" : "error"
                      }`}
                    >
                      {q.is_correct ? "✓ Correct" : "✗ Incorrect"}
                    </span>
                  </div>

                  <div className="options-container">
                    {q.options?.map((opt, i) => (
                      <div
                        key={i}
                        className={`option ${
                          opt === q.correct ? "correct-ans" : ""
                        } ${
                          opt === q.given_answer && !q.is_correct
                            ? "wrong-ans"
                            : ""
                        }`}
                      >
                        <span className="option-letter">
                          {String.fromCharCode(65 + i)}
                        </span>
                        <span>{opt}</span>
                        {opt === q.correct && (
                          <span className="marker">✓ Correct</span>
                        )}
                        {opt === q.given_answer && !q.is_correct && (
                          <span className="marker error">
                            ✗ Your answer
                          </span>
                        )}
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
                <div
                  key={idx}
                  className={`question-card ${
                    q.output_correct ? "correct" : "incorrect"
                  }`}
                >
                  <div className="question-header">
                    <div>
                      <h4>
                        Q{q.id}: {q.title}
                      </h4>
                      <p className="question-desc">{q.description}</p>
                    </div>
                    <span
                      className={`difficulty-badge ${q.difficulty.toLowerCase()}`}
                    >
                      {q.difficulty}
                    </span>
                  </div>

                  <div className="code-section">
                    <p className="code-label">Your Solution:</p>
                    <pre className="code-block">
                      <code>{q.given_answer}</code>
                    </pre>
                  </div>

                  <div className="question-footer">
                    {q.marks ? (
                      <span className="marks-earned">Marks: {q.marks}</span>
                    ) : (
                      <span className="marks-earned">Attempt: Completed</span>
                    )}
                    <span
                      className={`output-status ${
                        q.output_correct ? "success" : "error"
                      }`}
                    >
                      {q.output_correct
                        ? "✓ Output Correct"
                        : "✗ Output Incorrect"}
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
                <span className="proctoring-value">
                  {data.proctoring.flagged_faces}
                </span>
              </div>
              <div className="proctoring-item">
                <span className="proctoring-label">Focus Deviation</span>
                <span className="proctoring-value">
                  {data.proctoring.focus_deviation_percent}%
                </span>
              </div>
              <div className="proctoring-item">
                <span className="proctoring-label">Cheating Events</span>
                <span className="proctoring-value">
                  {data.proctoring.cheating_events}
                </span>
              </div>
              <div className="proctoring-item">
                <span className="proctoring-label">Activity Status</span>
                <span className="proctoring-value">
                  {data.proctoring.unusual_activity || "Normal"}
                </span>
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
  );
};

export default TestCases;
