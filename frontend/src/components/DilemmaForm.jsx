import { useState } from 'react';
import AgentSelector from './AgentSelector';
import DebateLibrary from './DebateLibrary';
import './DilemmaForm.css';

function DilemmaForm({ onSubmit }) {
  const [currentStep, setCurrentStep] = useState(1);
  const [showLibrary, setShowLibrary] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    A: '',
    B: '',
    constraints: '',
  });
  
  const [selectedAgents, setSelectedAgents] = useState(['deon', 'conse', 'virtue']); // Default selection
  const [availableAgentsMap, setAvailableAgentsMap] = useState({}); // Map of agent id -> agent info

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleTemplateSelect = (template) => {
    setFormData(template);
    setShowLibrary(false);
  };

  const validateStep1 = () => {
    return formData.title.trim() && 
           formData.constraints.trim() && 
           formData.A.trim() && 
           formData.B.trim();
  };

  const handleNext = (e) => {
    e.preventDefault();
    if (validateStep1()) {
      setCurrentStep(2);
    } else {
      alert('Please fill in all fields before proceeding.');
    }
  };

  const handleBack = () => {
    setCurrentStep(1);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const validAgents = selectedAgents.filter(agent => agent !== null);
    if (validAgents.length !== 3) {
      alert('Please select exactly 3 agents for the debate.');
      return;
    }
    // Build agents info map for selected agents
    const agentsInfo = {};
    validAgents.forEach(agentId => {
      if (availableAgentsMap[agentId]) {
        const agent = availableAgentsMap[agentId];
        agentsInfo[agent.name] = agent;
      }
    });
    onSubmit(formData, validAgents, agentsInfo);
  };

  return (
    <div className="dilemma-form card">
      {/* Simple Step Indicator */}
      <div className="step-indicator">
        <span className="step-text">Step {currentStep} of 2</span>
      </div>

      {/* Step 1: Dilemma Setup */}
      {currentStep === 1 && (
        <div className="wizard-step">
          <div className="step-header">
            <div>
              <h2>Enter Your Ethical Dilemma</h2>
              <p className="step-subtitle">Describe the ethical scenario you want the agents to debate</p>
            </div>
            <button 
              type="button"
              className="btn btn-library"
              onClick={() => setShowLibrary(true)}
            >
              Browse Debate Library
            </button>
          </div>
          
          <form onSubmit={handleNext}>
            <div className="form-group">
              <label htmlFor="title">Title</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g., Academic Integrity vs Compassion"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="constraints">Constraints/Context</label>
              <textarea
                id="constraints"
                name="constraints"
                value={formData.constraints}
                onChange={handleChange}
                rows="3"
                placeholder="Any relevant constraints, background, or context that affects the decision..."
                required
              />
            </div>

            <div className="options-grid">
              <div className="form-group">
                <label htmlFor="A">Option A</label>
                <textarea
                  id="A"
                  name="A"
                  value={formData.A}
                  onChange={handleChange}
                  rows="3"
                  placeholder="Describe the first option..."
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="B">Option B</label>
                <textarea
                  id="B"
                  name="B"
                  value={formData.B}
                  onChange={handleChange}
                  rows="3"
                  placeholder="Describe the second option..."
                  required
                />
              </div>
            </div>

            <div className="wizard-actions">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={!validateStep1()}
              >
                Next: Choose Team →
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Step 2: Team Selection */}
      {currentStep === 2 && (
        <div className="wizard-step">
          <h2>Choose Your Debate Team</h2>
          <p className="step-subtitle">Select 3 agents to participate in the ethical debate</p>
          
          <AgentSelector 
            selectedAgents={selectedAgents}
            onSelectionChange={setSelectedAgents}
            onAgentsLoaded={setAvailableAgentsMap}
          />

          <div className="wizard-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={handleBack}
            >
              ← Back to Dilemma
            </button>
            <button 
              type="button" 
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={selectedAgents.filter(a => a !== null).length !== 3}
            >
              Start Debate
            </button>
          </div>
        </div>
      )}

      {/* Debate Library Modal */}
      {showLibrary && (
        <DebateLibrary 
          onSelectTemplate={handleTemplateSelect}
          onClose={() => setShowLibrary(false)}
        />
      )}
    </div>
  );
}

export default DilemmaForm;
