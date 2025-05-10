import { useState } from "react";
import { useNavigate } from "react-router-dom";        // if you’re using React Router
import "./Modal.css";

/* Grab the CSRF token from the cookie Django sets */
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return "";
}

export default function SignInModal({ onClose }) {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState(null);

  const handleChange = (e) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
  
    try {
      const res = await fetch("/api/signin/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify(formData),
      });
  
      const data = await res.json();  // ← only call this once
  
      if (res.ok) {
        console.log("Login succeeded. Redirecting...");
        onClose();  // close the modal
        //window.location.href = data.redirect || "/dashboard";
        window.location.href = "http://localhost:8000/dashboard";

      } else {
        setError(data.detail || "Login failed.");
      }
    } catch (err) {
      setError(err.message);
    }
  }
  
  

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={(e) => e.stopPropagation()}>
        {/* — header — */}
        <div className="modal-header">
          <h2>Sign In</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        {/* — errors — */}
        {error && <p className="error">{error}</p>}

        {/* — form — */}
        <form onSubmit={handleSubmit} className="stack">
          <label>
            Username
            <input
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </label>

          <div className="actions">
            <button type="submit" className="btn primary">
              Login
            </button>
            <button type="button" className="btn secondary" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
