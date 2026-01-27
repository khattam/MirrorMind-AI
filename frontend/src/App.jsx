import { useState, useEffect } from 'react';
import { Analytics } from '@vercel/analytics/react';
import DilemmaForm from './components/DilemmaForm';
import DebateView from './components/DebateView';
import VerdictView from './components/VerdictView';
import Sidebar from './components/Sidebar';
import AgentBuilderScreen from './components/AgentBuilder/AgentBuilderScreen';
import KeyboardShortcuts from './components/KeyboardShortcuts';
import Dashboard from './components/Dashboard';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

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
  const [selectedAgentsInfo, setSelectedAgentsInfo] = useState({});
  const [notification, setNotification] = useState(null); // For toast notifications

  // Load debate history on mount
  useEffect(() => {
    loadDebateHistory();
  }, []);

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

  const handleStartDebate = async (dilemmaData, selectedAgentIds = ['deon', 'conse', 'virtue'], agentsInfo = {}) => {
    setDilemma(dilemmaData);
    setSelectedAgentsInfo(agentsInfo);
    setTranscript({
      dilemma: dilemmaData,
      turns: [],
    });
    setRoundCount(0);
    setStage('debate');

    // Check and add to library IMMEDIATELY when debate starts
    checkAndAddToLibrary(dilemmaData);

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

  const checkAndAddToLibrary = async (dilemmaData) => {
    try {
      // Submit the debate for deduplication check
      const submission = {
        title: dilemmaData.title,
        context: dilemmaData.constraints,
        option_a: dilemmaData.A,
        option_b: dilemmaData.B
      };

      console.log('Submitting debate for deduplication check:', submission.title);

      const response = await fetch(`${API_URL}/api/debates/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submission),
      });

      const result = await response.json();
      console.log('Deduplication result:', result);
      
      if (result.success && result.added_template) {
        // Show success notification
        console.log('Showing success notification');
        setNotification({
          type: 'success',
          message: '✓ Debate added to library!'
        });
        setTimeout(() => setNotification(null), 4000);
      } else if (result.is_duplicate) {
        // Show info notification
        console.log('Showing duplicate notification');
        setNotification({
          type: 'info',
          message: 'ℹ This debate already exists in the library'
        });
        setTimeout(() => setNotification(null), 4000);
      }
    } catch (error) {
      console.error('Failed to check debate for library:', error);
      // Don't show error to user - this is a background operation
    }
  };

  const loadDebateHistory = async () => {
    try {
      const response = await fetch(`${API_URL}/api/debates?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setDebateHistory(data.debates || []);
      }
    } catch (error) {
      console.error('Failed to load debate history:', error);
    }
  };

  const handleReset = () => {
    // Debate is already saved to backend in handleJudge
    // Just reload history to get the latest
    loadDebateHistory();
    
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

  const deleteHistoryItem = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/debates/${id}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        setDebateHistory(prev => prev.filter(item => item.id !== id));
      } else {
        console.error('Failed to delete debate');
      }
    } catch (error) {
      console.error('Error deleting debate:', error);
    }
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
              agentsInfo={selectedAgentsInfo}
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
      
      {/* Notification Toast */}
      {notification && (
        <div className={`notification-toast ${notification.type}`}>
          {notification.message}
        </div>
      )}
      
      {/* Keyboard shortcuts helper - always visible */}
      {stage !== 'agent-builder' && <KeyboardShortcuts />}
      
      {/* Vercel Analytics */}
      <Analytics />
    </div>
  );
}

export default App;
