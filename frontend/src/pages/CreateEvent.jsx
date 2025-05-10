import React, { useEffect, useState } from "react";
import axios from "axios";
import "./CreateEvent.css";
function getCSRFToken() {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; csrftoken=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}
export default function CreateEvent() {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [date, setDate] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch("/api/candidates/")
      .then((res) => res.json())
      .then((data) => setCandidates(data.candidates || []));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      const res = await axios.post("/api/create_event/", {
        title,
        description,
        date,
        candidate_ids: selectedCandidates,
      },
      {
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        withCredentials: true,
      });
      setMessage("✅ Event created and candidates invited successfully!");
      // Clear form after success
      setTitle("");
      setDescription("");
      setDate("");
      setSelectedCandidates([]);
    } catch (err) {
      console.error(err);
      setMessage("❌ Failed to create event or invite candidates.");
    }
  };

  return (
    <div className="event-creation-container">
      <h2 className="event-creation-header">Create Event & Invite Candidates</h2>

      <form onSubmit={handleSubmit} className="event-form">
        <div className="form-group">
          <label>Event Title</label>
          <input
            type="text"
            className="form-control"
            placeholder="Enter event title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Event Description</label>
          <textarea
            className="form-control"
            placeholder="Describe the event"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Date & Time</label>
          <input
            type="datetime-local"
            className="form-control"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label>Select Candidates</label>
          <select
            multiple
            className="multi-select"
            value={selectedCandidates}
            onChange={(e) =>
              setSelectedCandidates([...e.target.selectedOptions].map((o) => o.value))
            }
          >
            {candidates.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name} ({c.email})
              </option>
            ))}
          </select>
          <small className="text-gray-500">Hold Ctrl/Cmd to select multiple</small>
        </div>

        <button type="submit" className="btn btn-green mt-4">
          Create & Invite
        </button>
      </form>

      {message && (
        <div className={`status-message ${message.startsWith("✅") ? "status-success" : "status-error"}`}>
          {message}
        </div>
      )}
    </div>
  );
}
