import React, { useEffect, useState } from "react";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [photo, setPhoto] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/profile/", {
      credentials: "include",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch profile");
        return res.json();
      })
      .then((data) => setUser(data))
      .catch((err) => {
        console.error("Profile fetch error:", err);
        setError("Could not load profile.");
      });
  }, []);

  const handlePhotoChange = (e) => {
    setPhoto(e.target.files[0]);
  };

  const handleUpload = (e) => {
    e.preventDefault();
    if (!photo) return;

    const formData = new FormData();
    formData.append("photo", photo);
    function getCSRFToken() {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; csrftoken=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
      }
      
    fetch("/api/profile/upload-photo/", {
        method: "POST",
        body: formData,
        credentials: "include",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
      })
      
      .then((res) => {
        if (!res.ok) throw new Error("Upload failed");
        return res.json();
      })
      .then((data) => {
        alert("Photo uploaded!");
        setUser((prev) => ({ ...prev, photo_url: data.photo_url }));
      })
      .catch((err) => {
        console.error("Upload error:", err);
        alert(err.message);
      });
  };

  if (error) return <p className="text-red-600">{error}</p>;
  if (!user) return <p className="text-gray-500">Loading profile...</p>;

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 shadow-md rounded-md mt-10">
      <h2 className="text-3xl font-bold mb-6 text-gray-800">Profile</h2>

      {user.photo_url && (
        <img
          src={user.photo_url}
          alt="Profile"
          className="w-32 h-32 object-cover rounded-full mb-4 border border-gray-300"
        />
      )}

      <form onSubmit={handleUpload} className="flex items-center mb-6 gap-3">
        <input
          type="file"
          accept="image/*"
          onChange={handlePhotoChange}
          className="block w-full text-sm text-gray-700"
        />
        <button
          type="submit"
          className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded"
        >
          Upload Photo
        </button>
      </form>

      <div className="space-y-2 text-lg text-gray-700">
        <p><strong>Username:</strong> {user.username}</p>
        <p><strong>Email:</strong> {user.email}</p>
        <p><strong>Role:</strong> {user.role_display}</p>
        <p><strong>Job Title:</strong> {user.job_title || "N/A"}</p>
      </div>

      <div className="mt-6">
        <a
          href="/edit-profile"
          className="inline-block text-blue-600 hover:text-blue-800 font-medium"
        >
          Edit Profile →
        </a>
      </div>
    </div>
  );
}
