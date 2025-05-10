import React, { useEffect, useState, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";

export default function EditCandidate() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [programChoices, setProgramChoices] = useState([]);
  const [statusChoices, setStatusChoices] = useState([]);

  const fetchCandidate = useCallback(async () => {
    try {
      const res = await axios.get(`/api/candidates/${id}/`);
      setCandidate(res.data);
      setProgramChoices(res.data.program_choices || []);
      setStatusChoices(res.data.status_choices || []);
    } catch (err) {
      console.error("Failed to fetch candidate:", err);
    }
  }, [id]);

  useEffect(() => {
    fetchCandidate();
  }, [fetchCandidate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setCandidate({ ...candidate, [name]: value });
  };

  const handleApplicationChange = (index, field, value) => {
    const updatedApplications = [...candidate.applications];
    updatedApplications[index][field] = value;
    setCandidate({ ...candidate, applications: updatedApplications });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/candidates/${id}/edit/`, candidate);
      navigate(`/candidates/${id}`);
    } catch (err) {
      console.error("Failed to save changes:", err);
    }
  };

  if (!candidate) return <div>Loading...</div>;

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h2 className="text-xl font-semibold mb-4">Edit Candidate</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          className="w-full border p-2"
          type="text"
          name="name"
          value={candidate.name || ""}
          onChange={handleChange}
          placeholder="Name"
        />
        <input
          className="w-full border p-2"
          type="email"
          name="email"
          value={candidate.email || ""}
          onChange={handleChange}
          placeholder="Email"
        />
        <select
          name="program_fit"
          className="w-full border p-2"
          value={candidate.program_fit || ""}
          onChange={handleChange}
        >
          <option value="">-- Select Program --</option>
          {programChoices.map(([val, label]) => (
            <option key={val} value={val}>{label}</option>
          ))}
        </select>
        <input
          className="w-full border p-2"
          type="number"
          name="gpa"
          step="0.01"
          value={candidate.gpa || ""}
          onChange={handleChange}
          placeholder="GPA"
        />
        <textarea
          className="w-full border p-2"
          name="academic_experience"
          value={candidate.academic_experience || ""}
          onChange={handleChange}
          placeholder="Academic Experience"
        />
        <textarea
          className="w-full border p-2"
          name="skills"
          value={candidate.skills || ""}
          onChange={handleChange}
          placeholder="Skills (comma-separated)"
        />
        <textarea
          className="w-full border p-2"
          name="projects"
          value={candidate.projects || ""}
          onChange={handleChange}
          placeholder="Projects (newline-separated)"
        />

        <h4 className="font-semibold mt-4">College Applications</h4>
        {candidate.applications.map((app, index) => (
          <div key={index} className="flex space-x-2 mb-2">
            <input
              type="text"
              className="border p-1 flex-1"
              value={app.college_name}
              onChange={(e) => handleApplicationChange(index, "college_name", e.target.value)}
              placeholder="College Name"
            />
            <select
              className="border p-1"
              value={app.application_status}
              onChange={(e) => handleApplicationChange(index, "application_status", e.target.value)}
            >
              {statusChoices.map(([val, label]) => (
                <option key={val} value={val}>{label}</option>
              ))}
            </select>
          </div>
        ))}

        <button className="btn btn-blue" type="submit">Save Changes</button>
      </form>
    </div>
  );
}
