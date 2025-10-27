import { useState, useEffect } from 'react';
import DilemmaForm from './components/DilemmaForm';
import DebateView from './components/DebateView';
import VerdictView from './components/VerdictView';
import Sidebar from './components/Sidebar';
import AgentBuilderScreen from './components/AgentBuilder/AgentBuilderScreen';
import KeyboardShortcuts from './components/KeyboardShortcuts';
import Dashboard from './components/Dashboard';
import './App.css';

const API_URL = 'http://127.0.0.1:8000';

function App() {
  const [stage, setStage] = useState('form'); // 'form', 'debate', 'verdict', 'agent-builder', 'dashboard'
  const [dilemma, setDilemma] = useState(null);
  const [transcript, setTranscript] = useState(null);
  const [verdict, setVerdict] = useState(null);
  const [roundCount, setRoundCount] = useState(0);
  const [currentThinkingAgent, setCurrentThinkingAgent] = useState(null);
  const [debateHistory, setDebateHistory] = useState([]);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);
  const [historyViewTab, setHistoryViewTab] = useState('debate');
  const [showDashboard, setShowDashboard] = useState(false);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e) => {
      // Ignore if user is typing in an input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      // Ctrl/Cmd + N: New debate
      if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        if (stage !== 'agent-builder') {
          handleReset();
        }
      }

      // Ctrl/Cmd + B: Open agent builder
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        if (stage !== 'agent-builder') {
          openAgentBuilder();
        }
      }

      // Ctrl/Cmd + D: Open dashboard
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        if (!showDashboard) {
          openDashboard();
        }
      }

      // Escape: Close modals/agent builder/dashboard
      if (e.key === 'Escape') {
        if (stage === 'agent-builder') {
          closeAgentBuilder();
        } else if (stage === 'history') {
          setStage('form');
        } else if (showDashboard) {
          closeDashboard();
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [stage]); // Re-run when stage changes

  const handleStartDebate = async (dilemmaData, selectedAgentIds = ['deon', 'conse', 'virtue']) => {
    setDilemma(dilemmaData);
    setTranscript({
      dilemma: dilemmaData,
      turns: [],
    });
    setRoundCount(0);
    setStage('debate');

    // Convert agent IDs to proper names for the API
    const agentNames = selectedAgentIds.map(id => {
      // Handle default agents
      if (id === 'deon') return 'Deon';
      if (id === 'conse') return 'Conse'; 
      if (id === 'virtue') return 'Virtue';
      // For custom agents, use the ID directly
      return id;
    });

    const turns = [];

    for (const agent of agentNames) {
      setCurrentThinkingAgent(agent);
      
      try {
        // For custom agents, use the ID directly; for default agents, use lowercase
        const agentEndpoint = ['Deon', 'Conse', 'Virtue'].includes(agent) 
          ? agent.toLowerCase() 
          : agent;
        
        const response = await fetch(`${API_URL}/agent/${agentEndpoint}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dilemmaData),
        });

        const turn = await response.json();
        turns.push(turn);
        
        setTranscript({
          dilemma: dilemmaData,
          turns: [...turns],
        });
      } catch (error) {
        console.error(`Error fetching ${agent}:`, error);
      }
    }

    setCurrentThinkingAgent(null);
  };

  const handleContinue = async () => {
    setRoundCount(roundCount + 1);
    
    // Get unique agent names from the current transcript
    const agents = [...new Set(transcript.turns.map(turn => turn.agent))];
    const currentTurns = [...transcript.turns];

    for (const agent of agents) {
      setCurrentThinkingAgent(agent);
      
      try {
        const response = await fetch(`${API_URL}/continue`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            ...transcript,
            turns: currentTurns,
          }),
        });

        const data = await response.json();
        const agentTurn = data.turns.find(t => t.agent === agent);
        
        if (agentTurn) {
          currentTurns.push(agentTurn);
          setTranscript({
            ...transcript,
            turns: [...currentTurns],
          });
        }
      } catch (error) {
        console.error(`Error fetching ${agent}:`, error);
      }
    }

    setCurrentThinkingAgent(null);
  };

  const handleJudge = async () => {
    setCurrentThinkingAgent('Judge');
    setStage('judging'); // New intermediate stage

    try {
      const response = await fetch(`${API_URL}/judge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transcript),
      });

      const data = await response.json();
      setVerdict(data);
      setCurrentThinkingAgent(null);
      setStage('verdict');
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to get judgment.');
      setCurrentThinkingAgent(null);
      setStage('debate');
    }
  };

  const handleReset = () => {
    // Save current debate to history if it exists
    if (transcript && verdict) {
      const historyItem = {
        id: Date.now(),
        title: transcript.dilemma.title,
        date: new Date().toLocaleDateString(),
        transcript,
        verdict,
        recommendation: verdict.final_recommendation,
        confidence: verdict.confidence
      };
      setDebateHistory(prev => [historyItem, ...prev]);
    }
    
    setStage('form');
    setDilemma(null);
    setTranscript(null);
    setVerdict(null);
    setRoundCount(0);
    setSelectedHistoryItem(null);
  };

  const viewHistoryItem = (item) => {
    setSelectedHistoryItem(item);
    setHistoryViewTab('debate');
    setStage('history');
  };

  const deleteHistoryItem = (id) => {
    setDebateHistory(prev => prev.filter(item => item.id !== id));
  };

  const openAgentBuilder = () => {
    setStage('agent-builder');
  };

  const closeAgentBuilder = () => {
    setStage('form');
  };

  const openDashboard = () => {
    setShowDashboard(true);
  };

  const closeDashboard = () => {
    setShowDashboard(false);
  };

  return (
    <div className="app">
      {stage !== 'agent-builder' && (
        <Sidebar 
          stage={stage}
          debateHistory={debateHistory}
          onNewDebate={handleReset}
          onViewHistory={viewHistoryItem}
          onDeleteHistory={deleteHistoryItem}
          onOpenAgentBuilder={openAgentBuilder}
          onOpenDashboard={openDashboard}
        />
      )}

      {stage === 'agent-builder' ? (
        <AgentBuilderScreen 
          onClose={closeAgentBuilder}
          onAgentCreated={(agent) => {
            // Handle agent creation success
            console.log('Agent created:', agent);
            closeAgentBuilder();
            // Force a re-render to refresh sidebar
            setStage('form');
          }}
        />
      ) : (
        <div className="main-area">
        <header className="header">
          <div>
            <h1>Ethical Debate Simulator</h1>
            <p className="subtitle">Watch AI agents debate complex moral dilemmas</p>
          </div>
        </header>

        <main className="main-content">
          {stage === 'form' && (
            <DilemmaForm onSubmit={handleStartDebate} />
          )}

          {stage === 'debate' && (
            <DebateView
              transcript={transcript}
              roundCount={roundCount}
              currentThinkingAgent={currentThinkingAgent}
              onContinue={handleContinue}
              onJudge={handleJudge}
              onReset={handleReset}
            />
          )}

          {stage === 'judging' && (
            <div className="judging-screen">
              <div className="judging-content">
                <div className="judge-avatar">⚖️</div>
                <h2>Judge is Deliberating</h2>
                <p>Analyzing all arguments and ethical considerations...</p>
                <div className="judging-spinner">
                  <div className="spinner-ring"></div>
                  <div className="spinner-ring"></div>
                  <div className="spinner-ring"></div>
                </div>
              </div>
            </div>
          )}

          {stage === 'verdict' && (
            <VerdictView verdict={verdict} onReset={handleReset} />
          )}

          {stage === 'history' && selectedHistoryItem && (
            <div className="history-view">
              <div className="history-header">
                <button className="back-btn" onClick={() => setStage('form')}>
                  ← Back
                </button>
                <h2>{selectedHistoryItem.title}</h2>
                <span className="history-date">{selectedHistoryItem.date}</span>
              </div>
              
              <div className="history-tabs">
                <button 
                  className={`history-tab ${historyViewTab === 'debate' ? 'active' : ''}`}
                  onClick={() => setHistoryViewTab('debate')}
                >
                  Debate
                </button>
                <button 
                  className={`history-tab ${historyViewTab === 'verdict' ? 'active' : ''}`}
                  onClick={() => setHistoryViewTab('verdict')}
                >
                  Verdict
                </button>
              </div>

              {historyViewTab === 'debate' && (
                <DebateView
                  transcript={selectedHistoryItem.transcript}
                  roundCount={Math.floor(selectedHistoryItem.transcript.turns.length / 3)}
                  currentThinkingAgent={null}
                  onContinue={() => {}}
                  onJudge={() => {}}
                  onReset={handleReset}
                  isHistoryView={true}
                />
              )}

              {historyViewTab === 'verdict' && (
                <VerdictView verdict={selectedHistoryItem.verdict} onReset={handleReset} />
              )}
            </div>
          )}
        </main>
        </div>
      )}
      
      {/* Dashboard Modal */}
      {showDashboard && (
        <Dashboard onClose={closeDashboard} />
      )}
      
      {/* Keyboard shortcuts helper - always visible */}
      {stage !== 'agent-builder' && <KeyboardShortcuts />}
    </div>
  );
}

export default App;
