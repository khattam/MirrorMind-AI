import { useState } from 'react';
import './KeyboardShortcuts.css';

function KeyboardShortcuts() {
  const [isOpen, setIsOpen] = useState(false);

  const shortcuts = [
    { keys: ['Ctrl', 'N'], mac: ['⌘', 'N'], description: 'New debate' },
    { keys: ['Ctrl', 'B'], mac: ['⌘', 'B'], description: 'Open agent builder' },
    { keys: ['Esc'], mac: ['Esc'], description: 'Close modals' },
  ];

  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;

  return (
    <div className="keyboard-shortcuts">
      <button 
        className="shortcuts-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title="Keyboard shortcuts"
      >
        ⌨️
      </button>

      {isOpen && (
        <div className="shortcuts-panel">
          <div className="shortcuts-header">
            <h3>Keyboard Shortcuts</h3>
            <button className="close-btn" onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className="shortcuts-list">
            {shortcuts.map((shortcut, index) => (
              <div key={index} className="shortcut-item">
                <div className="shortcut-keys">
                  {(isMac ? shortcut.mac : shortcut.keys).map((key, i) => (
                    <span key={i}>
                      <kbd>{key}</kbd>
                      {i < (isMac ? shortcut.mac : shortcut.keys).length - 1 && <span className="plus">+</span>}
                    </span>
                  ))}
                </div>
                <div className="shortcut-description">{shortcut.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default KeyboardShortcuts;
