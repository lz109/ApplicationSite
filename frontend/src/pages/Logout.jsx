import { FaSignOutAlt } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import axios from "axios";
function getCSRFToken() {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }

  export default function LogoutLink() {
    const navigate = useNavigate();
  
    const handleLogout = async (e) => {
      e.preventDefault();
      try {
        await axios.post("/api/logout/", null, {
          headers: {
            "X-CSRFToken": getCSRFToken(),
          },
          withCredentials: true,
        });
        navigate("/");
      } catch (err) {
        console.error("Logout failed", err);
        alert("Logout failed.");
      }
    };
  
    return (
      <a href="/" onClick={handleLogout} className="sidebar-link logout">
        <FaSignOutAlt /> <span>Logout</span>
      </a>
    );
  }