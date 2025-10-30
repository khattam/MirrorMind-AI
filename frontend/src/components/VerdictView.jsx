import './VerdictView.css';

function VerdictView({ verdict, onReset }) {
  const formatCriterion = (criterion) => {
    // Special case for autonomy_respect
    if (criterion === 'autonomy_respect') {
      return 'Autonomy';
    }
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
            <div className="scores-table">
              <div className="scores-table-header">
                <div className="table-cell header-cell">Option</div>
                {Object.keys(Object.values(verdict.scores)[0] || {}).map((criterion) => (
                  <div key={criterion} className="table-cell header-cell">
                    {formatCriterion(criterion)}
                  </div>
                ))}
              </div>
              {Object.entries(verdict.scores).map(([option, scores]) => {
                if (typeof scores === 'object') {
                  const optionLabel = option.replace('option_', '').toUpperCase();
                  return (
                    <div key={option} className="scores-table-row">
                      <div className="table-cell option-cell">Option {optionLabel}</div>
                      {Object.entries(scores).map(([criterion, score]) => (
                        <div key={`${option}-${criterion}`} className="table-cell score-cell">
                          <span className="score-value">{score}/2</span>
                        </div>
                      ))}
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
