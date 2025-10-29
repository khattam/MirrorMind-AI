import React from 'react';
import './AgentDetailsModal.css';

function AgentDetailsModal({ agent, onClose, onDelete }) {
  if (!agent) return null;

  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete "${agent.name}"? This action cannot be undone.`)) {
      onDelete(agent.id, agent.name);
      onClose();
    }
  };

  return (
    <div className="agent-modal-overlay" onClick={onClose}>
      <div className="agent-modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="agent-modal-header">
          <div className="agent-modal-avatar" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            {agent.avatar}
          </div>
          <div className="agent-modal-title">
            <h2>{agent.name}</h2>
            <p>Custom Ethical Agent</p>
          </div>
          <button className="agent-modal-close" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="agent-modal-body">
          <div className="agent-modal-section">
            <h3>Personality & Values</h3>
            <p className="agent-modal-description">
              {agent.enhanced_prompt || agent.description}
            </p>
          </div>

          <div className="agent-modal-stats">
            <div className="stat-card">
              <div className="stat-icon">📅</div>
              <div className="stat-content">
                <span className="stat-label">Created</span>
                <span className="stat-value">{new Date(agent.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">💬</div>
              <div className="stat-content">
                <span className="stat-label">Usage</span>
                <span className="stat-value">{agent.usage_count} debates</span>
              </div>
            </div>
            {agent.average_rating > 0 && (
              <div className="stat-card">
                <div className="stat-icon">⭐</div>
                <div className="stat-content">
                  <span className="stat-label">Rating</span>
                  <span className="stat-value">{agent.average_rating.toFixed(1)} ({agent.rating_count})</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="agent-modal-footer">
          <button className="agent-modal-btn delete" onClick={handleDelete}>
            Delete Agent
          </button>
          <button className="agent-modal-btn primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

export default AgentDetailsModal;
