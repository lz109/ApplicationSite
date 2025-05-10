import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Messages.css"; // Optional CSS for styling

export default function Messages() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ recipient: "", subject: "", body: "" });
  const [sending, setSending] = useState(false);
  const [sendStatus, setSendStatus] = useState("");
  const [users, setUsers] = useState([]);


  useEffect(() => {
    fetchMessages();
    fetchUsers();
  }, []);

  const fetchMessages = async () => {
    try {
      const res = await axios.get("/api/messages/", { withCredentials: true });
      setMessages(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error(err);
      setError("Failed to load messages.");
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await axios.get("/api/recipients/", { withCredentials: true });
      setUsers(res.data);
    } catch (err) {
      console.error("Error fetching recipients:", err);
    }
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSend = async (e) => {
    e.preventDefault();
    setSending(true);
    setSendStatus("");

    try {
      await axios.post("/api/messages/", form, {
        headers: { "Content-Type": "application/json" },
        withCredentials: true,
      });
      setSendStatus("Message sent!");
      setForm({ recipient: "", subject: "", body: "" });
      fetchMessages(); // Refresh messages
    } catch (err) {
      console.error(err);
      setSendStatus("Failed to send message.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="messages-container">
      <h1>Your Messages</h1>

      <form onSubmit={handleSend} className="send-message-form">
        <h2>Send Message</h2>
        <select
            name="recipient"
            value={form.recipient}
            onChange={handleChange}
            required
            >
            <option value="">-- Select Recipient --</option>
            {users.map((user) => (
                <option key={user.role + "_" + user.id} value={user.id}>
                {user.username} ({user.role})
                </option>
            ))}
            </select>

        <input
          type="text"
          name="subject"
          placeholder="Subject"
          value={form.subject}
          onChange={handleChange}
          required
        />
        <textarea
          name="body"
          placeholder="Your message"
          value={form.body}
          onChange={handleChange}
          required
        ></textarea>
        <button type="submit" disabled={sending}>
          {sending ? "Sending..." : "Send Message"}
        </button>
        {sendStatus && <p className="status">{sendStatus}</p>}
      </form>

      <hr className="my-4" />

      {loading ? (
        <p>Loading messages...</p>
      ) : error ? (
        <p className="error">{error}</p>
      ) : messages.length > 0 ? (
        <div className="messages-list">
          {messages.map((msg) => (
            <div key={msg.id} className={`message-card ${msg.is_read ? "" : "unread"}`}>
              <div className="message-header">
                <span className="from">
                  <strong>{msg.sender.username}</strong> ➝ <strong>{msg.recipient.username}</strong>
                </span>
                <span className="date">{new Date(msg.sent_at).toLocaleString()}</span>
              </div>
              <h3>{msg.subject}</h3>
              <p>{msg.body}</p>
            </div>
          ))}
        </div>
      ) : (
        <p>No messages found.</p>
      )}
    </div>
  );
}
