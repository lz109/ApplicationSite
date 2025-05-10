import React from 'react';
import './UniAdvisor.css';

const UniAdvisor = () => {
  return (
    <div className="uni-advisor-container">
      <header className="hero-section">
        <h1>Enhance University Guidance</h1>
        <p className="hero-description">
          UniAdvisor provides tools to save time, stay organized, and offer improved guidance to undergraduates, postgraduates, and international applicants.
        </p>
      </header>

      <section className="features-section">
        <div className="feature-card">
          <div className="feature-img-container">
            <img src="/images/student_eval.png" alt="Application Review" className="feature-img" />
          </div>
          <h2>Efficient Application Reviews</h2>
          <p>
            Simplify and streamline the application review process, allowing advisors to focus on quality guidance rather than administrative tasks.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-img-container">
            <img src="/images/event.jpg" alt="Event Management" className="feature-img" />
          </div>
          <h2>Event Management Made Easy</h2>
          <p>
            Manage university events seamlessly within the platform, ensuring advisors can coordinate and track important admissions events.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-img-container">
            <img src="/images/track_application.png" alt="Student Progress" className="feature-img" />
          </div>
          <h2>Track Student Progress</h2>
          <p>
            Monitor and track student progress effectively with visual dashboards and progress indicators.
          </p>
        </div>

        <div className="feature-card">
          <div className="feature-img-container">
            <img src="/images/feature-tools.png" alt="Guidance Tools" className="feature-img" />
          </div>
          <h2>Comprehensive Guidance Tools</h2>
          <p>
            UniAdvisor offers a comprehensive set of tools for personalized student advising and resource management.
          </p>
        </div>
      </section>
    </div>
  );
};

export default UniAdvisor;