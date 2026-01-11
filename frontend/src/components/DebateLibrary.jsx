import { useState, useEffect } from 'react';
import './DebateLibrary.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function DebateLibrary({ onSelectTemplate, onClose }) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await fetch(`${API_URL}/api/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  // Categorize templates
  const categories = {
    all: 'All Dilemmas',
    classic: 'Classic Philosophy',
    technology: 'Technology & AI',
    society: 'Society & Politics',
    personal: 'Personal Ethics'
  };

  const getCategory = (template) => {
    const slug = template.slug.toLowerCase();
    if (['trolley-switch', 'trolley-footbridge', 'transplant-surgeon', 'experience-machine', 'lying-to-protect'].includes(slug)) {
      return 'classic';
    }
    if (['self-driving-car', 'ai-lethal-autonomous-weapons', 'ai-deception-in-negotiation', 'ai-elder-care', 'ai-content-moderator', 'predictive-policing', 'data-collection-consent', 'algorithmic-fairness-vs-accuracy'].includes(slug)) {
      return 'technology';
    }
    if (['privacy-vs-security', 'refugee-admissions', 'free-speech-vs-hate-speech', 'cultural-heritage-vs-development', 'punishment-vs-rehabilitation', 'climate-geoengineering'].includes(slug)) {
      return 'society';
    }
    return 'personal';
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.context.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || getCategory(template) === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const handleSelect = (template) => {
    onSelectTemplate({
      title: template.title,
      A: template.option_a,
      B: template.option_b,
      constraints: template.context
    });
  };

  if (loading) {
    return (
      <div className="debate-library-overlay" onClick={onClose}>
        <div className="debate-library-modal" onClick={e => e.stopPropagation()}>
          <div className="library-loading">Loading debate library...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="debate-library-overlay" onClick={onClose}>
      <div className="debate-library-modal" onClick={e => e.stopPropagation()}>
        <div className="library-header">
          <h2>Debate Library</h2>
          <p>Choose from {templates.length} classic ethical dilemmas</p>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="library-filters">
          <input
            type="text"
            placeholder="Search dilemmas..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <div className="category-tabs">
            {Object.entries(categories).map(([key, label]) => (
              <button
                key={key}
                className={`category-tab ${selectedCategory === key ? 'active' : ''}`}
                onClick={() => setSelectedCategory(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        <div className="templates-grid">
          {filteredTemplates.map((template) => (
            <div 
              key={template.id} 
              className="template-card"
              onClick={() => handleSelect(template)}
            >
              <h3 className="template-title">{template.title}</h3>
              <p className="template-context">{template.context}</p>
              <div className="template-options">
                <div className="option-preview">
                  <span className="option-label">A:</span>
                  <span>{template.option_a.substring(0, 60)}...</span>
                </div>
                <div className="option-preview">
                  <span className="option-label">B:</span>
                  <span>{template.option_b.substring(0, 60)}...</span>
                </div>
              </div>
              <button className="use-template-btn">Use This Dilemma →</button>
            </div>
          ))}
        </div>

        {filteredTemplates.length === 0 && (
          <div className="no-results">
            No dilemmas found matching your search.
          </div>
        )}
      </div>
    </div>
  );
}

export default DebateLibrary;
