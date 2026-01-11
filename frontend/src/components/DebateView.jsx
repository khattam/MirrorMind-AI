import { useEffect, useState, useRef } from 'react';
import TypewriterText from './TypewriterText';
import './TypewriterText.css';
import './DebateView.css';

function DebateView({ transcript, roundCount, currentThinkingAgent, onContinue, onJudge, onReset, isHistoryView = false, agentsInfo = {} }) {
  const [activeAgent, setActiveAgent] = useState(null);
  const [expandedRounds, setExpandedRounds] = useState(isHistoryView ? new Set() : new Set([0]));
  const [animatedTurns, setAnimatedTurns] = useState(new Set()); // Track which turns have been animated
  const prevTurnsLength = useRef(0);

  useEffect(() => {
    if (transcript.turns.length > 0 && !isHistoryView) {
      const lastTurn = transcript.turns[transcript.turns.length - 1];
      setActiveAgent(lastTurn.agent);
      
      // Only expand the latest round
      const currentRound = Math.floor((transcript.turns.length - 1) / 3);
      setExpandedRounds(new Set([currentRound]));
      
      // Mark new turns for animation
      if (transcript.turns.length > prevTurnsLength.current) {
        const newTurnIndex = transcript.turns.length - 1;
        // Don't add to animatedTurns yet - let it animate first
      }
      prevTurnsLength.current = transcript.turns.length;
      
      const timer = setTimeout(() => setActiveAgent(null), 1000);
      return () => clearTimeout(timer);
    }
  }, [transcript.turns.length, isHistoryView]);

  // Mark a turn as animated (animation complete)
  const handleAnimationComplete = (turnIndex) => {
    setAnimatedTurns(prev => new Set([...prev, turnIndex]));
  };

  // Check if a turn should animate (new turn that hasn't been animated yet)
  const shouldAnimate = (turnIndex) => {
    if (isHistoryView) return false; // No animation in history view
    return !animatedTurns.has(turnIndex);
  };

  // Custom gradient colors for custom agents
  const customGradients = [
    'linear-gradient(135deg, #f5af19 0%, #f12711 100%)',
    'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    'linear-gradient(135deg, #ee0979 0%, #ff6a00 100%)',
    'linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%)',
    'linear-gradient(135deg, #00c6ff 0%, #0072ff 100%)',
  ];

  const getAgentInfo = (agent) => {
    const defaultInfo = {
      Deon: { name: 'Deon', role: 'Deontologist', icon: '⚖️', gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
      Conse: { name: 'Conse', role: 'Consequentialist', icon: '◆', gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
      Virtue: { name: 'Virtue', role: 'Virtue Ethicist', icon: '✦', gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
    };
    
    // Check if it's a default agent
    if (defaultInfo[agent]) {
      return defaultInfo[agent];
    }
    
    // Check if we have info from agentsInfo prop
    if (agentsInfo[agent]) {
      const info = agentsInfo[agent];
      // Get a consistent gradient based on agent name hash
      const gradientIndex = agent.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % customGradients.length;
      return { 
        name: info.name || agent, 
        role: 'Custom Agent', 
        icon: info.avatar || '🤖', 
        gradient: customGradients[gradientIndex]
      };
    }
    
    // Fallback for unknown agents
    const gradientIndex = agent.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % customGradients.length;
    return { name: agent, role: 'Custom Agent', icon: '🤖', gradient: customGradients[gradientIndex] };
  };

  // Get unique agents from transcript instead of hardcoding
  const agents = [...new Set(transcript.turns.map(turn => turn.agent))];
  const isThinking = currentThinkingAgent !== null;

  // Group turns by rounds
  const getRounds = () => {
    const rounds = [];
    for (let i = 0; i < transcript.turns.length; i += 3) {
      rounds.push(transcript.turns.slice(i, i + 3));
    }
    return rounds;
  };

  const toggleRound = (roundIndex) => {
    const newExpanded = new Set(expandedRounds);
    if (newExpanded.has(roundIndex)) {
      newExpanded.delete(roundIndex);
    } else {
      newExpanded.add(roundIndex);
    }
    setExpandedRounds(newExpanded);
  };

  const rounds = getRounds();
  const latestRoundIndex = rounds.length - 1;

  return (
    <div className="debate-stage">
      <div className="stage-header">
        <div className="dilemma-card">
          <h2 className="dilemma-title">{transcript.dilemma.title}</h2>
          <div className="options-row">
            <div className="option-item">
              <span className="option-badge">A</span>
              <p>{transcript.dilemma.A}</p>
            </div>
            <div className="option-divider"></div>
            <div className="option-item">
              <span className="option-badge">B</span>
              <p>{transcript.dilemma.B}</p>
            </div>
          </div>
        </div>
      </div>

      {rounds.map((roundTurns, roundIndex) => {
        const isExpanded = expandedRounds.has(roundIndex);
        const isLatest = roundIndex === latestRoundIndex;
        const roundLabel = roundIndex === 0 ? 'Opening Arguments' : `Round ${roundIndex}`;

        return (
          <div key={roundIndex} className="round-container">
            {!isLatest && (
              <button 
                className="round-toggle"
                onClick={() => toggleRound(roundIndex)}
              >
                <span className="round-label">{roundLabel}</span>
                <span className="toggle-icon">{isExpanded ? '−' : '+'}</span>
              </button>
            )}
            
            {isLatest && (
              <div className="round-label-static">{roundLabel}</div>
            )}

            {(isExpanded || isLatest) && (
              <div className="agents-panel">
                {agents.map((agentName) => {
                  const turn = roundTurns.find(t => t.agent === agentName);
                  const turnIndex = turn ? transcript.turns.findIndex(t => t === turn) : -1;
                  const agentInfo = getAgentInfo(agentName);
                  const isActive = activeAgent === agentName && isLatest;
                  const isCurrentlyThinking = currentThinkingAgent === agentName && isLatest;

                  return (
                    <div 
                      key={agentName} 
                      className={`agent-panel ${isActive ? 'active' : ''} ${isCurrentlyThinking ? 'thinking' : ''} ${turn ? 'has-spoken' : ''}`}
                    >
                      <div className="agent-avatar" style={{ background: agentInfo.gradient }}>
                        <span className="agent-icon">{agentInfo.icon}</span>
                      </div>
                      
                      <div className="agent-details">
                        <h3 className="agent-name">{agentInfo.name}</h3>
                        <p className="agent-role">{agentInfo.role}</p>
                        {turn && (
                          <div className="agent-stance">
                            Position: <span className="stance-value">{turn.stance}</span>
                          </div>
                        )}
                      </div>

                      {isCurrentlyThinking && isLatest && (
                        <div className="thinking-overlay">
                          <div className="thinking-pulse"></div>
                          <span className="thinking-label">Thinking...</span>
                        </div>
                      )}

                      {turn && !isCurrentlyThinking && (
                        <div className="agent-speech">
                          <div className="speech-bubble">
                            <p>
                              {shouldAnimate(turnIndex) ? (
                                <TypewriterText 
                                  text={turn.argument} 
                                  speed={12}
                                  onComplete={() => handleAnimationComplete(turnIndex)}
                                />
                              ) : (
                                turn.argument
                              )}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        );
      })}

      {!isHistoryView && (
        <div className="stage-controls">
          <button 
            className="stage-btn primary-btn" 
            onClick={onContinue}
            disabled={isThinking}
          >
            Continue Debate
          </button>
          <button 
            className="stage-btn secondary-btn" 
            onClick={onJudge}
            disabled={isThinking}
          >
            Get Judgment
          </button>
          <button 
            className="stage-btn ghost-btn" 
            onClick={onReset}
            disabled={isThinking}
          >
            New Dilemma
          </button>
        </div>
      )}
    </div>
  );
}

export default DebateView;
