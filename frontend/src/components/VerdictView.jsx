import './VerdictView.css';

function VerdictView({ verdict, onReset }) {
  const formatCriterion = (criterion) => {
    return criterion
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className="verdict-view card verdict-card">
      <h2>⚖️ Judge's Verdict</h2>

      <div className="verdict-content">
        <div className="verdict-section">
          <h3>Final Recommendation</h3>
          <div className="recommendation">Option {verdict.final_recommendation}</div>
        </div>

        <div className="verdict-section">
          <h3>Reasoning</h3>
          <p>{verdict.verdict}</p>
        </div>

        {verdict.scores && Object.keys(verdict.scores).length > 0 && (
          <div className="verdict-section full-width">
            <h3>Ethical Scores</h3>
            <div className="scores-container">
              {Object.entries(verdict.scores).map(([option, scores]) => {
                if (typeof scores === 'object') {
                  const optionLabel = option.replace('option_', '').toUpperCase();
                  return (
                    <div key={option} className="option-scores-row">
                      <div className="option-label">Option {optionLabel}</div>
                      <div className="scores-grid">
                        {Object.entries(scores).map(([criterion, score]) => (
                          <div key={`${option}-${criterion}`} className="score-item">
                            <div className="score-label">
                              {optionLabel}: {formatCriterion(criterion)}
                            </div>
                            <div className="score-value">{score}/2</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                }
                return null;
              })}
            </div>
          </div>
        )}
      </div>

      <button className="btn btn-primary" onClick={onReset}>
        Start New Debate
      </button>
    </div>
  );
}

export default VerdictView;
