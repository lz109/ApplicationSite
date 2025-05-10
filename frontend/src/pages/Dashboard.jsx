import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import ViewStatistics from './ViewStatistics';
import AddCandidate from './AddCandidate';
import EventCalendar from './EventCalendar';
import CreateEvent from './CreateEvent';
import CandidateList from './CandidateList';

export default function Dashboard() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-6 bg-gray-100 overflow-y-auto">
        <Routes>
          <Route path="/" element={<ViewStatistics />} />
          <Route path="/add-candidate" element={<AddCandidate />} />
          <Route path="/calendar" element={<EventCalendar />} />
          <Route path="/create-event" element={<CreateEvent />} />
          <Route path="/candidates" element={<CandidateList />} />
        </Routes>
      </main>
    </div>
  );
}
