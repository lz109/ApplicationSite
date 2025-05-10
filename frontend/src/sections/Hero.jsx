// src/sections/Hero.jsx
import { Button } from 'react-bootstrap';
import './hero.css';               // keep the gradient overlay + layout rules

export default function Hero({ onSignIn, onSignUp }) {
  // Anything inside /public is served at  /<filename>
  // PUBLIC_URL lets CRA/Webpack add the right prefix in production builds.
  const bg = `${process.env.PUBLIC_URL}/images/hero-classroom.png`;

  return (
    <header
      className="hero position-relative d-flex align-items-center"
      style={{
        background: `url(${bg}) center / cover no-repeat`,
        fontFamily: 'Roboto, sans-serif'
        /*  If you removed min-height from hero.css, keep it here */
        // minHeight: '90vh',
      }}
    >
      <div className="container position-relative">
        <h1 className="display-3 fw-bold mb-3">
          Streamline University
          <br />
          Admissions with UniAdvisor
        </h1>

        <p className="lead col-lg-7 mb-4">
          Empower your university admissions process with UniAdvisor, designed to simplify
          application reviews, event management, and student progress tracking for advisors and
          consultants.
        </p>

        <Button variant="success" size="lg" className="me-3" onClick={onSignIn}>
            Sign In
        </Button>
        <Button variant="success" size="lg" onClick={onSignUp}>
            Sign Up
        </Button>
        
        <div className="d-flex align-items-center gap-3 mt-4 stars">
          ★★★★★
        </div>
        <div className="rating-labels">
          <span>Efficiency</span>
          <span>·</span>
          <span>Organization</span>
        </div>


        <figure className="mt-4">
          <blockquote className="blockquote fst-italic mb-1">
            “UniAdvisor saved me hours of work!”
          </blockquote>
        </figure>
      </div>
    </header>
  );
}
