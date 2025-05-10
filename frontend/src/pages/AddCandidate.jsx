import React, { useState, useEffect } from "react";
import axios from "axios";

function getCSRFToken() {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; csrftoken=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

export default function AddCandidate() {
  const [officers, setOfficers] = useState([]);
  const [resumeFile, setResumeFile] = useState(null);
  const [message, setMessage] = useState("");
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    program_fit: "",
    gpa: "",
    shortlisted: false,
    academic_experience: "",
    skills: "",
    projects: "",
    officer: "",
    colleges: [{ name: "", status: "pending" }],
  });

  useEffect(() => {
    fetch("/api/officers/")
      .then(res => res.json())
      .then(data => setOfficers(data));
  }, []);
  const handleResumeUpload = async (e) => {
    e.preventDefault();
    if (!resumeFile) return;
  
    const data = new FormData();
    data.append("files", resumeFile);
  
    try {
      const res = await axios.post("/api/upload_resume/", data, {
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
        withCredentials: true,
      });
      setMessage(res.data.message);
      
      const extracted = res.data.results?.[0];
      if (extracted) {
        setFormData((prev) => ({
          ...prev,
          name: extracted.name || "",
          email: extracted.email || "",
          program_fit: extracted.program_fit || "",
          gpa: extracted.gpa || "",
          academic_experience: extracted.academic_experience || "",
          skills: extracted.skills || "",
          projects: extracted.projects || "",
          colleges: (extracted.colleges_applied || "")
            .split(",")
            .map((name) => ({ name: name.trim(), status: "pending" })),
        }));
      }
      
  
      setMessage(res.data.message);
    } catch (err) {
      setMessage("Error uploading resume.");
    }
  };

  const handleManualSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      ...formData,
      college_name: formData.colleges.map(c => c.name),
      application_status: formData.colleges.map(c => c.status),
    };

    try {
      const res = await axios.post("/api/add_candidate/", payload, {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        withCredentials: true,
      });
      setMessage(res.data.message);
    } catch (err) {
      setMessage("Error adding candidate.");
    }
  };

  const updateCollege = (i, field, value) => {
    const updated = [...formData.colleges];
    updated[i][field] = value;
    setFormData({ ...formData, colleges: updated });
  };

  return (
    <div className="add-candidate-container">
      <h2 className="add-candidate-header">Add New Candidate</h2>

      <form onSubmit={handleResumeUpload} className="candidate-form">
        <div className="form-group">
          <label>Upload Resume (.pdf or .docx):</label>
          <input 
            type="file" 
            className="file-input"
            accept=".pdf,.docx" 
            onChange={(e) => setResumeFile(e.target.files[0])} 
          />
        </div>
        <button type="submit" className="btn btn-blue">Upload</button>
      </form>

      <hr className="divider" />

      <form onSubmit={handleManualSubmit} className="candidate-form">
        <div className="form-group">
          <label>Full Name</label>
          <input 
            type="text" 
            className="form-control"
            placeholder="Full Name" 
            required
            value={formData.name}
            onChange={e => setFormData({ ...formData, name: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input 
            type="email" 
            className="form-control"
            placeholder="Email" 
            required
            value={formData.email}
            onChange={e => setFormData({ ...formData, email: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>Program Fit</label>
          <input 
            type="text" 
            className="form-control"
            placeholder="Program Fit"
            value={formData.program_fit}
            onChange={e => setFormData({ ...formData, program_fit: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>GPA</label>
          <input 
            type="number" 
            className="form-control"
            step="0.01" 
            min="0" 
            max="4" 
            placeholder="GPA"
            value={formData.gpa}
            onChange={e => setFormData({ ...formData, gpa: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>Academic Experience</label>
          <textarea 
            className="form-control"
            placeholder="Academic Experience"
            value={formData.academic_experience}
            onChange={e => setFormData({ ...formData, academic_experience: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>Skills</label>
          <textarea 
            className="form-control"
            placeholder="Skills"
            value={formData.skills}
            onChange={e => setFormData({ ...formData, skills: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>Projects</label>
          <textarea 
            className="form-control"
            placeholder="Projects"
            value={formData.projects}
            onChange={e => setFormData({ ...formData, projects: e.target.value })} 
          />
        </div>

        <div className="form-group">
          <label>Assigned Officer</label>
          <select 
            className="form-control"
            required 
            value={formData.officer}
            onChange={e => setFormData({ ...formData, officer: e.target.value })}
          >
            <option value="">-- Select Officer --</option>
            {officers.map(o => (
              <option key={o.id} value={o.id}>{o.username} ({o.email})</option>
            ))}
          </select>
        </div>

        <div className="form-section">
          <h4>Colleges Applied</h4>
          {formData.colleges.map((c, i) => (
            <div key={i} className="college-entry">
              <input 
                type="text" 
                className="form-control"
                placeholder="College Name" 
                required
                value={c.name}
                onChange={(e) => updateCollege(i, "name", e.target.value)} 
              />
              <select 
                className="form-control"
                value={c.status}
                onChange={(e) => updateCollege(i, "status", e.target.value)}
              >
                <option value="pending">Pending</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
                <option value="waitlisted">Waitlisted</option>
              </select>
            </div>
          ))}
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={() =>
              setFormData({ ...formData, colleges: [...formData.colleges, { name: "", status: "pending" }] })
            }
          >
            + Add Another College
          </button>
        </div>

        <button type="submit" className="btn btn-green">Add Candidate</button>
      </form>

      {message && (
        <div className={`status-message ${message.includes("Error") ? "status-error" : "status-success"}`}>
          {message}
        </div>
      )}
    </div>
  );
}