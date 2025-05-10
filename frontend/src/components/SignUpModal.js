// src/components/SignUpModal.js
import { useState } from 'react';
import './Modal.css';                       // same overlay / popup styles

export default function SignUpModal({ onClose }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: '',
    role: 'admin',                          // or 'officer' as default
  });
  const [error, setError] = useState(null);

  const handleChange = e =>
    setFormData({ ...formData, [e.target.name]: e.target.value });

  async function handleSubmit(e) {
    e.preventDefault();

    /* simple front-end check */
    if (formData.password1 !== formData.password2) {
      setError('Passwords do not match.');
      return;
    }

    /* POST to your Django/DRF endpoint */
    const res = await fetch('/api/signup/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: formData.username,
        email: formData.email,
        password1: formData.password1,
        password2: formData.password2,
        role: formData.role,
      }),
    });

    if (res.ok) {
      window.location.href = "/dashboard";
    } else {
      let msg = `Registration failed (HTTP ${res.status})`;
      try {
        const data = await res.json();
        msg = data.detail ?? JSON.stringify(data);
      } catch (_) { /* non‑JSON */ }
      setError(msg);
      console.error("Signup error:", msg);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Sign Up</h2>
          <button className="close-btn" onClick={onClose}>
            ×
          </button>
        </div>

        {error && <p className="error">{error}</p>}

        <form onSubmit={handleSubmit} className="stack">
          {/* USERNAME */}
          <label>
            Username
            <input
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </label>

          {/* EMAIL */}
          <label>
            Email
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />
          </label>

          {/* PASSWORD */}
          <label>
            Password
            <input
              type="password"
              name="password1"
              value={formData.password1}
              onChange={handleChange}
              required
            />
          </label>

          {/* CONFIRM PASSWORD */}
          <label>
            Confirm Password
            <input
              type="password"
              name="password2"
              value={formData.password2}
              onChange={handleChange}
              required
            />
          </label>

          {/* ROLE */}
          <label>
            Role
            <select name="role" value={formData.role} onChange={handleChange}>
              <option value="admin">Admin</option>
              <option value="officer">Admission Officer</option>
            </select>
          </label>

          {/* ACTION BUTTONS */}
          <div className="actions">
            <button type="submit" className="btn primary">
              Register
            </button>
            <button
              type="button"
              className="btn secondary"
              onClick={onClose}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
