import { useState } from "react";
import { Link } from "react-router-dom";
import './sidebar.css'; // Make sure this path is correct
import LogoutLink from "./Logout";
import {
  FaUser,
  FaEnvelope,
  FaChartBar,
  FaPlusCircle,
  FaCalendarAlt,
  FaEdit,
  FaPaperPlane,
  FaUsers,
  FaSignOutAlt,
} from "react-icons/fa";

export default function Sidebar() {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <header className="sidebar-header">
        <h1>Welcome, Advisor</h1>
        <p className="lead">
          As an <strong>Advisor</strong>, you can manage candidates, review applications, and schedule events.
        </p>
      </header>
      
      <button className="collapse-btn" onClick={toggleSidebar} aria-label="Toggle sidebar" />
      
      <nav className="sidebar-nav">
        {/* <Link to="/officer_dashboard/Profile" className="sidebar-link">
          <FaUser /> <span>My Profile</span>
        </Link> */}

        <Link to="/officer_dashboard/messages" className="sidebar-link">
          <FaEnvelope /> <span>Messages</span>
        </Link>

        <Link to="/officer_dashboard/statistics" className="sidebar-link">
          <FaChartBar /> <span>View Statistics</span>
        </Link>

        <Link to="/officer_dashboard/add-candidate" className="sidebar-link">
          <FaPlusCircle /> <span>Add Candidate</span>
        </Link>

        <Link to="/officer_dashboard/calendar" className="sidebar-link">
          <FaCalendarAlt /> <span>Event Calendar</span>
        </Link>

        <Link to="/officer_dashboard/create-event" className="sidebar-link">
          <FaEdit /> <span>Create Event</span>
        </Link>

        <Link to="/officer_dashboard/candidates" className="sidebar-link">
          <FaUsers /> <span>All Candidates</span>
        </Link>

        <LogoutLink />

      </nav>
    </aside>
  );
}