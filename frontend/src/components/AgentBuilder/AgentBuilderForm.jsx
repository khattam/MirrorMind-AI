import { useState } from 'react';
import './AgentBuilderForm.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function AgentBuilderForm({ onAgentCreated, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    avatar: '🤖',
    description: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [enhancement, setEnhancement] = useState(null);
  const [errors, setErrors] = useState({});
  const [step, setStep] = useState('input'); // 'input', 'enhancement', 'preview'

  const avatarOptions = ['🤖', '🧠', '⚖️', '🌱', '💡', '🔬', '🎭', '🏛️', '🌟', '🔥', '💎', '🌊'];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Agent name is required';
    } else if (formData.name.length > 50) {
      newErrors.name = 'Agent name must be 50 characters or less';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Agent description is required';
    } else if (formData.description.length < 50) {
      newErrors.description = 'Description must be at least 50 characters';
    } else if (formData.description.length > 1000) {
      newErrors.description = 'Description must be 1000 characters or less';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAnalyze = async () => {
    if (!validateForm()) return;
    
    setIsAnalyzing(true);
    try {
      const response = await fetch(`${API_URL}/api/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: formData.description })
      });
      
      if (!response.ok) {
        throw new Error('Failed to analyze description');
      }
      
      const enhancementData = await response.json();
      setEnhancement(enhancementData);
      setStep('enhancement');
    } catch (error) {
      console.error('Enhancement error:', error);
      setErrors({ general: 'Failed to analyze description. Please try again.' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCreateAgent = async (useEnhanced = true) => {
    try {
      const response = await fetch(`${API_URL}/api/agents/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          avatar: formData.avatar,
          description: useEnhanced && enhancement ? enhancement.enhanced_prompt : formData.description
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create agent');
      }
      
      const result = await response.json();
      onAgentCreated && onAgentCreated(result.agent);
      
      // Reset form
      setFormData({ name: '', avatar: '🤖', description: '' });
      setEnhancement(null);
      setStep('input');
      
    } catch (error) {
      console.error('Creation error:', error);
      setErrors({ general: error.message });
    }
  };

  const getCharacterCount = () => {
    return formData.description.length;
  };

  const getCharacterCountClass = () => {
    const count = getCharacterCount();
    if (count < 50) return 'char-count-low';
    if (count > 900) return 'char-count-high';
    return 'char-count-good';
  };

  return (
    <div className="agent-builder-form">
      <div className="form-header">
        <h2>Create Your Ethical Agent</h2>
        {onClose && (
          <button className="close-btn" onClick={onClose}>×</button>
        )}
      </div>

      {step === 'input' && (
        <div className="input-step">
          <div className="form-group">
            <label htmlFor="agent-name">Agent Name</label>
            <input
              id="agent-name"
              type="text"
              value={formData.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
              placeholder="e.g., EcoWarrior, LogicBot, CompassionateAI"
              maxLength={50}
              className={errors.name ? 'error' : ''}
            />
            {errors.name && <span className="error-text">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label>Choose Avatar</label>
            <div className="avatar-selector">
              {avatarOptions.map(emoji => (
                <button
                  key={emoji}
                  type="button"
                  className={`avatar-option ${formData.avatar === emoji ? 'selected' : ''}`}
                  onClick={() => handleInputChange('avatar', emoji)}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="agent-description">
              Describe Your Agent
              <span className="help-text">
                Explain what this agent believes, how it makes decisions, and what values it prioritizes
              </span>
            </label>
            <textarea
              id="agent-description"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder="This agent believes in environmental protection above all else. It prioritizes future generations and uses scientific evidence to make decisions. When evaluating ethical dilemmas, it always considers the long-term impact on the planet and wildlife..."
              rows={6}
              maxLength={1000}
              className={errors.description ? 'error' : ''}
            />
            <div className={`character-count ${getCharacterCountClass()}`}>
              {getCharacterCount()}/1000 characters
              {getCharacterCount() < 50 && <span className="min-note"> (minimum 50)</span>}
            </div>
            {errors.description && <span className="error-text">{errors.description}</span>}
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="analyze-btn primary"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !formData.name.trim() || formData.description.length < 50}
            >
              {isAnalyzing ? 'Analyzing...' : 'Analyze & Enhance'}
            </button>
            <button
              type="button"
              className="create-btn secondary"
              onClick={() => handleCreateAgent(false)}
              disabled={!formData.name.trim() || formData.description.length < 50}
            >
              Create Without Enhancement
            </button>
          </div>

          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}

          <div className="help-section">
            <h4>💡 Tips for Better Agents</h4>
            <ul>
              <li>Describe specific values and beliefs</li>
              <li>Explain how the agent makes decisions</li>
              <li>Include personality traits (logical, compassionate, strict, etc.)</li>
              <li>Give examples of what the agent would prioritize</li>
              <li>Mention any philosophical frameworks it follows</li>
            </ul>
          </div>
        </div>
      )}

      {step === 'enhancement' && enhancement && (
        <div className="enhancement-step">
          <div className="enhancement-header">
            <h3>AI Enhancement Results</h3>
            <div className="analysis-scores">
              {Object.entries(enhancement.analysis_scores).map(([key, score]) => (
                <div key={key} className="score-item">
                  <span className="score-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${(score / 10) * 100}%` }}
                    ></div>
                  </div>
                  <span className="score-value">{score.toFixed(1)}/10</span>
                </div>
              ))}
            </div>
          </div>

          <div className="comparison-panel">
            <div className="original-section">
              <h4>Your Original Description</h4>
              <div className="description-text">{formData.description}</div>
            </div>

            <div className="enhanced-section">
              <h4>AI-Enhanced Version</h4>
              <div className="description-text enhanced">{enhancement.enhanced_prompt}</div>
            </div>
          </div>

          {enhancement.improvements_made.length > 0 && (
            <div className="improvements-section">
              <h4>✨ Improvements Made</h4>
              <ul>
                {enhancement.improvements_made.map((improvement, index) => (
                  <li key={index}>{improvement}</li>
                ))}
              </ul>
            </div>
          )}

          {enhancement.suggestions.length > 0 && (
            <div className="suggestions-section">
              <h4>💡 Additional Suggestions</h4>
              <ul>
                {enhancement.suggestions.map((suggestion, index) => (
                  <li key={index}>{suggestion}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="enhancement-actions">
            <button
              className="accept-btn primary"
              onClick={() => handleCreateAgent(true)}
            >
              Create with Enhanced Version
            </button>
            <button
              className="original-btn secondary"
              onClick={() => handleCreateAgent(false)}
            >
              Use Original Description
            </button>
            <button
              className="back-btn"
              onClick={() => setStep('input')}
            >
              ← Back to Edit
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default AgentBuilderForm;