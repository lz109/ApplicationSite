import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Sidebar from './Sidebar';
import ViewStatistics from './ViewStatistics';
import AddCandidate from './AddCandidate';
import EventCalendar from './EventCalendar';
import CreateEvent from './CreateEvent';
import CandidateList from './CandidateList';
import MessagesPage from './Messages';
import CandidateProfile from "./candidateProfile"
import './officerDashboard.css';

export default function officerDashboard() {
  return (
    <div className="dashboard-container">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={
            <div className="dashboard-card route-transition">
              <ViewStatistics />
            </div>
          } />
          
          <Route path="/add-candidate" element={
            <div className="dashboard-card route-transition">
              <AddCandidate />
            </div>
          } />
          
          <Route path="/calendar" element={
            <div className="dashboard-card route-transition">
              <EventCalendar />
            </div>
          } />
          
          <Route path="/create-event" element={
            <div className="dashboard-card route-transition">
              <CreateEvent />
            </div>
          } />
          
          <Route path="/candidates" element={
            <div className="dashboard-card route-transition">
              <CandidateList />
            </div>
          } />
          <Route path="/candidates/:id" element={
            <div className="dashboard-card route-transition">
              <CandidateProfile />
            </div>
          } />
          
        <Route path="/messages" element={
            <div className="dashboard-card route-transition">
                <MessagesPage /> 
                </div>}    />
                </Routes>
      </main>
    </div>
  );
}