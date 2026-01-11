import { useState, useEffect } from 'react';

function TypewriterText({ text, speed = 15, onComplete }) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!text) return;
    
    setDisplayedText('');
    setIsComplete(false);
    let index = 0;

    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1));
        index++;
      } else {
        clearInterval(timer);
        setIsComplete(true);
        if (onComplete) onComplete();
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed]);

  return (
    <span className={`typewriter-text ${isComplete ? 'complete' : 'typing'}`}>
      {displayedText}
      {!isComplete && <span className="cursor">|</span>}
    </span>
  );
}

export default TypewriterText;
