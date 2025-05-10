import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";
import './statistics.css';
export default function ViewStatistics() {
  const [data, setData] = useState(null);
  const [filter, setFilter] = useState("mine");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    fetch(`/api/statistics/?filter=${filter}`)
      .then((res) => res.json())
      .then((data) => {
        setData(data);
        renderChart(data);
        setIsLoading(false);
      })
      .catch(() => setIsLoading(false));
  }, [filter]);

  const renderChart = (stats) => {
    const ctx = document.getElementById("statusChart");
    if (!ctx) return;

    if (window.statusChartInstance) {
      window.statusChartInstance.destroy();
    }

    window.statusChartInstance = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Accepted", "Rejected", "Pending", "Waitlisted"],
        datasets: [
          {
            label: "Number of Applications",
            data: [
              stats.accepted,
              stats.rejected,
              stats.pending,
              stats.waitlisted,
            ],
            backgroundColor: [
              "rgba(75, 192, 192, 0.6)",
              "rgba(255, 99, 132, 0.6)",
              "rgba(255, 206, 86, 0.6)",
              "rgba(54, 162, 235, 0.6)",
            ],
            borderColor: [
              "rgba(75, 192, 192, 1)",
              "rgba(255, 99, 132, 1)",
              "rgba(255, 206, 86, 1)",
              "rgba(54, 162, 235, 1)",
            ],
            borderWidth: 1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
          tooltip: {
            mode: "index",
            intersect: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
            },
          },
        },
      },
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-8 text-red-500">
        Failed to load statistics. Please try again later.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h2 className="text-2xl font-semibold">Application Statistics</h2>
        <div className="flex items-center">
          <label htmlFor="filter" className="mr-2 font-medium text-gray-700">
            View Candidates:
          </label>
          <select
            id="filter"
            className="form-control w-auto"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Candidates</option>
            <option value="mine">My Candidates</option>
          </select>
        </div>
      </div>

      <div className="responsive-grid">
        <div className="stat-card">
          <h3>Total Candidates</h3>
          <p className="stat-value">{data.total_candidates}</p>
        </div>
        <div className="stat-card">
          <h3>Total Applications</h3>
          <p className="stat-value">{data.total_college_applications}</p>
        </div>
        <div className="stat-card">
          <h3>Acceptance Ratio</h3>
          <p className="stat-value">{data.acceptance_ratio}%</p>
        </div>
      </div>

      <div className="dashboard-card">
        <h3 className="text-xl font-semibold mb-4">Application Status Distribution</h3>
        <div className="h-80">
          <canvas id="statusChart"></canvas>
        </div>
      </div>

      <div className="dashboard-card">
        <h3 className="text-xl font-semibold mb-4">Detailed Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <h4 className="font-medium mb-2">Application Status</h4>
            <ul className="space-y-1">
              <li className="flex justify-between">
                <span>Accepted:</span>
                <span className="font-medium">{data.accepted}</span>
              </li>
              <li className="flex justify-between">
                <span>Rejected:</span>
                <span className="font-medium">{data.rejected}</span>
              </li>
              <li className="flex justify-between">
                <span>Pending:</span>
                <span className="font-medium">{data.pending}</span>
              </li>
              <li className="flex justify-between">
                <span>Waitlisted:</span>
                <span className="font-medium">{data.waitlisted}</span>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-2">Ratios</h4>
            <ul className="space-y-1">
              <li className="flex justify-between">
                <span>Acceptance Ratio:</span>
                <span className="font-medium">{data.acceptance_ratio}%</span>
              </li>
              <li className="flex justify-between">
                <span>Rejection Ratio:</span>
                <span className="font-medium">
                  {Math.round((data.rejected / data.total_college_applications) * 100)}%
                </span>
              </li>
            </ul>
          </div>
        </div>

        <h4 className="font-medium mb-2">Candidate Acceptance Ratios</h4>
        <div className="overflow-x-auto">
          <table className="dashboard-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Total Applications</th>
                <th>Accepted</th>
                <th>Ratio (%)</th>
              </tr>
            </thead>
            <tbody>
              {data.candidate_acceptance_ratios.length > 0 ? (
                data.candidate_acceptance_ratios.map((c, idx) => (
                  <tr key={idx}>
                    <td>{c.name}</td>
                    <td>{c.total_applications}</td>
                    <td>{c.accepted_applications}</td>
                    <td>{c.acceptance_ratio}%</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center py-4 text-gray-500">
                    No candidates have applied yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}