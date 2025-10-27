import React from 'react';
import './Dashboard.css';

const Dashboard = ({ onClose }) => {
  // Hardcoded stats for now - will be replaced with real API data later
  const stats = {
    totalDebates: 247,
    totalAgents: 12,
    avgDebateLength: 4.2,
    mostActiveAgent: "Deon",
    topPerformers: [
      { name: "Virtue", avatar: "✦", winRate: 68, debates: 89 },
      { name: "EcoWarrior", avatar: "🌱", winRate: 64, debates: 34 },
      { name: "Deon", avatar: "⚖️", winRate: 61, debates: 92 },
      { name: "Dr. Ethics", avatar: "🏥", winRate: 58, debates: 28 },
      { name: "Conse", avatar: "◆", winRate: 55, debates: 87 }
    ],
    recentActivity: [
      { title: "AI Surveillance Ethics", winner: "Virtue", confidence: 87, time: "2 hours ago" },
      { title: "Climate vs Economy", winner: "EcoWarrior", confidence: 92, time: "4 hours ago" },
      { title: "Medical Resource Allocation", winner: "Dr. Ethics", confidence: 78, time: "6 hours ago" },
      { title: "Social Media Moderation", winner: "Deon", confidence: 83, time: "8 hours ago" },
      { title: "Autonomous Vehicle Dilemma", winner: "Conse", confidence: 71, time: "1 day ago" }
    ],
    topicDistribution: [
      { topic: "Medical Ethics", count: 67, percentage: 27 },
      { topic: "AI & Technology", count: 54, percentage: 22 },
      { topic: "Environmental", count: 49, percentage: 20 },
      { topic: "Business Ethics", count: 42, percentage: 17 },
      { topic: "Social Issues", count: 35, percentage: 14 }
    ],
    weeklyDebates: [
      { day: "Mon", count: 12 },
      { day: "Tue", count: 18 },
      { day: "Wed", count: 15 },
      { day: "Thu", count: 22 },
      { day: "Fri", count: 19 },
      { day: "Sat", count: 8 },
      { day: "Sun", count: 6 }
    ]
  };

  return (
    <div className="dashboard-overlay">
      <div className="dashboard-container">
        <div className="dashboard-header">
          <h1>📊 Analytics Dashboard</h1>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="dashboard-content">
          {/* Key Metrics */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-icon">🎯</div>
              <div className="metric-value">{stats.totalDebates}</div>
              <div className="metric-label">Total Debates</div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🤖</div>
              <div className="metric-value">{stats.totalAgents}</div>
              <div className="metric-label">Active Agents</div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">⏱️</div>
              <div className="metric-value">{stats.avgDebateLength}</div>
              <div className="metric-label">Avg Rounds</div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">🏆</div>
              <div className="metric-value">{stats.mostActiveAgent}</div>
              <div className="metric-label">Most Active</div>
            </div>
          </div>

          <div className="dashboard-grid">
            {/* Top Performers */}
            <div className="dashboard-card">
              <h3>🏅 Top Performing Agents</h3>
              <div className="performers-list">
                {stats.topPerformers.map((agent, index) => (
                  <div key={agent.name} className="performer-item">
                    <div className="performer-rank">#{index + 1}</div>
                    <div className="performer-avatar">{agent.avatar}</div>
                    <div className="performer-info">
                      <div className="performer-name">{agent.name}</div>
                      <div className="performer-stats">{agent.debates} debates</div>
                    </div>
                    <div className="performer-winrate">
                      <div className="winrate-value">{agent.winRate}%</div>
                      <div className="winrate-bar">
                        <div 
                          className="winrate-fill" 
                          style={{ width: `${agent.winRate}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="dashboard-card">
              <h3>⚡ Recent Debates</h3>
              <div className="activity-list">
                {stats.recentActivity.map((debate, index) => (
                  <div key={index} className="activity-item">
                    <div className="activity-title">{debate.title}</div>
                    <div className="activity-details">
                      <span className="activity-winner">Winner: {debate.winner}</span>
                      <span className="activity-confidence">{debate.confidence}% confidence</span>
                      <span className="activity-time">{debate.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Topic Distribution */}
            <div className="dashboard-card">
              <h3>📈 Popular Topics</h3>
              <div className="topics-list">
                {stats.topicDistribution.map((topic, index) => (
                  <div key={topic.topic} className="topic-item">
                    <div className="topic-info">
                      <span className="topic-name">{topic.topic}</span>
                      <span className="topic-count">{topic.count} debates</span>
                    </div>
                    <div className="topic-bar">
                      <div 
                        className="topic-fill" 
                        style={{ width: `${topic.percentage}%` }}
                      ></div>
                      <span className="topic-percentage">{topic.percentage}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Weekly Activity */}
            <div className="dashboard-card">
              <h3>📅 Weekly Activity</h3>
              <div className="weekly-chart">
                {stats.weeklyDebates.map((day, index) => (
                  <div key={day.day} className="chart-bar">
                    <div 
                      className="bar-fill" 
                      style={{ height: `${(day.count / 25) * 100}%` }}
                    ></div>
                    <div className="bar-value">{day.count}</div>
                    <div className="bar-label">{day.day}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;