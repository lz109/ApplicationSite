import React, { useEffect, useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import './CandidateList.css'

export default function CandidateList() {
  const [candidates, setCandidates] = useState([]);
  const [filters, setFilters] = useState({
    program_fit: "",
    college_name: "",
    application_status: "",
    score_sort: "",
  });
  const [programChoices, setProgramChoices] = useState([]);
  const fetchCandidates = async () => {
    const params = new URLSearchParams(filters).toString();
    const res = await fetch(`/api/candidates/?${params}`);
    const data = await res.json();
    setCandidates(data.candidates || []);
    setProgramChoices(data.program_choices || []);
  };
  useEffect(() => {
    fetchCandidates();
  }, [filters]);

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const getGPAStyle = (gpa) => {
    if (gpa > 3.7) return { color: "green", fontWeight: "bold" };
    if (gpa < 2.5) return { color: "red", fontWeight: "bold" };
    return {};
  };

  return (
    <div className="candidate-list-container">
      <h3 className="candidate-list-header">All Candidates</h3>

      {/* Filters */}
      <div className="filter-grid">
        <select
          name="program_fit"
          className="filter-control"
          value={filters.program_fit}
          onChange={handleFilterChange}
        >
          <option value="">All Programs</option>
          {programChoices.map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>

        <input
          type="text"
          name="college_name"
          placeholder="College Name"
          className="filter-control"
          value={filters.college_name}
          onChange={handleFilterChange}
        />

        <select
          name="application_status"
          className="filter-control"
          value={filters.application_status}
          onChange={handleFilterChange}
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="accepted">Accepted</option>
          <option value="rejected">Rejected</option>
          <option value="waitlisted">Waitlisted</option>
        </select>

        <select
          name="score_sort"
          className="filter-control"
          value={filters.score_sort}
          onChange={handleFilterChange}
        >
          <option value="">Sort by GPA</option>
          <option value="high_to_low">High to Low</option>
          <option value="low_to_high">Low to High</option>
        </select>
      </div>

      {/* Candidate Table */}
      <table className="candidate-table">
        <thead className="table-header">
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Program Fit</th>
            <th>GPA</th>
            <th>Applications</th>
            <th>Score</th>
            <th>Message</th>
          </tr>
        </thead>
        <tbody>
          {candidates.length > 0 ? (
            candidates.map((c) => (
              <tr key={c.id} className="table-row">
                <td>
                  <Link to={`/candidates/${c.id}`} className="candidate-link">
                    {c.name}
                  </Link>
                </td>
                <td>{c.email}</td>
                <td>{c.program_fit}</td>
                <td className={c.gpa > 3.7 ? "gpa-excellent" : c.gpa < 2.5 ? "gpa-poor" : ""}>
                  {c.gpa}
                </td>
                <td>
                  <table className="applications-table">
                    <thead>
                      <tr>
                        <th>College</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {c.applications.map((a) => (
                        <tr key={a.id}>
                          <td>{a.college_name}</td>
                          <td>
                            <span className={`status-badge status-${a.application_status.toLowerCase()}`}>
                              {a.application_status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </td>
                <td>{c.score}</td>
                <td>
                  <textarea 
                    className="message-textarea" 
                    placeholder="Type your message..."
                  />
                  <button className="send-button">Send</button>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="7" className="empty-state">
                No candidates found matching your filters
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}