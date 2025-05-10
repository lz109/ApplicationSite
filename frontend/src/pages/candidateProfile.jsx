// CandidateProfile.jsx
import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

export default function CandidateProfile() {
  const { id } = useParams();
  const [candidate, setCandidate] = useState(null);

  useEffect(() => {
    axios.get(`/api/candidates/${id}/`).then((res) => setCandidate(res.data));
  }, [id]);

  if (!candidate) return <div>Loading...</div>;

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Candidate Profile</h2>
      <p><strong>Name:</strong> {candidate.name}</p>
      <p><strong>Email:</strong> {candidate.email}</p>
      <p><strong>Program Fit:</strong> {candidate.program_fit}</p>
      <p><strong>GPA:</strong> {candidate.gpa}</p>
      <p><strong>Skills:</strong> {candidate.skills}</p>
      <p><strong>Projects:</strong> <pre>{candidate.projects}</pre></p>
      <p><strong>Academic Experience:</strong> <pre>{candidate.academic_experience}</pre></p>

      <h3 className="text-xl font-semibold mt-4">College Applications</h3>
      <ul>
        {candidate.applications.map((app) => (
          <li key={app.id}>
            {app.college_name} - <em>{app.application_status}</em>
          </li>
        ))}
      </ul>

      <Link
        to={`/candidates/${candidate.id}/edit`}
        className="inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded"
      >
        Edit Candidate
      </Link>
    </div>
  );
}
