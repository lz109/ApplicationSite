import React from "react";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="hero">
        <h1>UniAdvisr</h1>
        <p>Empowering University Application Advisors</p>
        <div className="buttons">
          <a href="/signin" className="btn primary">Sign In</a>
          <a href="/signup" className="btn secondary">Sign Up</a>
        </div>
      </header>

      <section className="features">
        <h2>💡 Why UniAdvisr</h2>
        <div className="feature-grid">
          <div className="feature-box">
            <h3>📄 Evaluate Students</h3>
            <p>Upload and analyze resumes with automatic GPA, skills, and project extraction.</p>
          </div>
          <div className="feature-box">
            <h3>📅 Event Management</h3>
            <p>Schedule and organize interviews, seminars, and deadlines with ease.</p>
          </div>
          <div className="feature-box">
            <h3>📊 Track Applications</h3>
            <p>Centralized dashboard to monitor candidate progress and decisions.</p>
          </div>
        </div>
      </section>

      <footer className="footer">
        &copy; {new Date().getFullYear()} UniAdvisr. All rights reserved.
      </footer>
    </div>
  );
}

export default App;
