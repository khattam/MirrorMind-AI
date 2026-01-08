import { useState, useEffect } from 'react';
import './AgentSelector.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function AgentSelector({ selectedAgents, onSelectionChange, onAgentsLoaded }) {
  const [availableAgents, setAvailableAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeSlot, setActiveSlot] = useState(null);
  const [showAgentPicker, setShowAgentPicker] = useState(false);

  // Default agents data
  const defaultAgents = [
    {
      id: 'deon',
      name: 'Deon',
      avatar: '⚖️',
      description: 'Deontologist - Rules, duties, universal principles',
      type: 'default'
    },
    {
      id: 'conse',
      name: 'Conse', 
      avatar: '◆',
      description: 'Consequentialist - Outcomes, happiness, utilitarian reasoning',
      type: 'default'
    },
    {
      id: 'virtue',
      name: 'Virtue',
      avatar: '✦', 
      description: 'Virtue Ethicist - Character, virtues, moral flourishing',
      type: 'default'
    }
  ];

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await fetch(`${API_URL}/api/agents`);
      if (response.ok) {
        const data = await response.json();
        const customAgents = data.agents.map(agent => ({
          ...agent,
          type: 'custom'
        }));
        const allAgents = [...defaultAgents, ...customAgents];
        setAvailableAgents(allAgents);
        
        // Build map and notify parent
        if (onAgentsLoaded) {
          const agentsMap = {};
          allAgents.forEach(agent => {
            agentsMap[agent.id] = agent;
          });
          onAgentsLoaded(agentsMap);
        }
      } else {
        setAvailableAgents(defaultAgents);
        if (onAgentsLoaded) {
          const agentsMap = {};
          defaultAgents.forEach(agent => {
            agentsMap[agent.id] = agent;
          });
          onAgentsLoaded(agentsMap);
        }
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
      setAvailableAgents(defaultAgents);
      if (onAgentsLoaded) {
        const agentsMap = {};
        defaultAgents.forEach(agent => {
          agentsMap[agent.id] = agent;
        });
        onAgentsLoaded(agentsMap);
      }
    } finally {
      setLoading(false);
    }
  };

  const getAgentById = (id) => {
    return availableAgents.find(agent => agent.id === id);
  };

  const handleSlotClick = (slotIndex) => {
    setActiveSlot(slotIndex);
    setShowAgentPicker(true);
  };

  const handleAgentSelect = (agentId) => {
    if (activeSlot !== null) {
      const newSelection = [...selectedAgents];
      newSelection[activeSlot] = agentId;
      onSelectionChange(newSelection);
    }
    setShowAgentPicker(false);
    setActiveSlot(null);
  };

  const handleRemoveAgent = (slotIndex) => {
    const newSelection = [...selectedAgents];
    newSelection[slotIndex] = null;
    onSelectionChange(newSelection);
  };

  if (loading) {
    return (
      <div className="agent-selector">
        <h3>Choose Your Debate Team</h3>
        <div className="loading-agents">Loading agents...</div>
      </div>
    );
  }

  return (
    <div className="agent-selector">
      <h3>Choose Your Debate Team</h3>
      <p className="selection-subtitle">Select 3 agents to participate in the ethical debate</p>
      
      {/* 3-Slot Team Builder */}
      <div className="team-builder">
        {[0, 1, 2].map((slotIndex) => {
          const agentId = selectedAgents[slotIndex];
          const agent = agentId ? getAgentById(agentId) : null;
          
          return (
            <div key={slotIndex} className="agent-slot">
              <div className="slot-label">Agent {slotIndex + 1}</div>
              
              {agent ? (
                <div className="selected-agent" onClick={() => handleSlotClick(slotIndex)}>
                  <div className="agent-avatar">
                    <span className="agent-icon">{agent.avatar}</span>
                  </div>
                  <div className="agent-details">
                    <h4 className="agent-name">{agent.name}</h4>
                    <p className="agent-type">{agent.type === 'default' ? 'Default' : 'Custom'}</p>
                  </div>
                  <button 
                    className="remove-agent-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleRemoveAgent(slotIndex);
                    }}
                    title="Remove agent"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div className="empty-slot" onClick={() => handleSlotClick(slotIndex)}>
                  <div className="add-icon">+</div>
                  <span>Choose Agent</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Agent Picker Modal */}
      {showAgentPicker && (
        <div className="agent-picker-overlay" onClick={() => setShowAgentPicker(false)}>
          <div className="agent-picker-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h4>Choose Agent for Slot {activeSlot + 1}</h4>
              <button 
                className="close-modal-btn"
                onClick={() => setShowAgentPicker(false)}
              >
                ×
              </button>
            </div>
            
            <div className="agents-list">
              <div className="agents-category">
                <h5>Default Agents</h5>
                {defaultAgents.map((agent) => (
                  <div
                    key={agent.id}
                    className={`agent-option ${selectedAgents.includes(agent.id) ? 'already-selected' : ''}`}
                    onClick={() => !selectedAgents.includes(agent.id) && handleAgentSelect(agent.id)}
                  >
                    <div className="agent-avatar small">
                      <span className="agent-icon">{agent.avatar}</span>
                    </div>
                    <div className="agent-info">
                      <h4 className="agent-name">{agent.name}</h4>
                      <p className="agent-description">{agent.description}</p>
                    </div>
                    {selectedAgents.includes(agent.id) && (
                      <span className="already-selected-badge">Selected</span>
                    )}
                  </div>
                ))}
              </div>

              {availableAgents.filter(a => a.type === 'custom').length > 0 && (
                <div className="agents-category">
                  <h5>Custom Agents</h5>
                  {availableAgents.filter(a => a.type === 'custom').map((agent) => (
                    <div
                      key={agent.id}
                      className={`agent-option ${selectedAgents.includes(agent.id) ? 'already-selected' : ''}`}
                      onClick={() => !selectedAgents.includes(agent.id) && handleAgentSelect(agent.id)}
                    >
                      <div className="agent-avatar small">
                        <span className="agent-icon">{agent.avatar}</span>
                      </div>
                      <div className="agent-info">
                        <h4 className="agent-name">{agent.name}</h4>
                        <p className="agent-description">{agent.description}</p>
                      </div>
                      {selectedAgents.includes(agent.id) && (
                        <span className="already-selected-badge">Selected</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentSelector;