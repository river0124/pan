import React from 'react';
import './HeaderToolbar.css';

function HeaderToolbar({ onCommand }) {
  return (
    <div className="toolbar">
      <button onClick={() => onCommand('bold')}>B</button>
      <button onClick={() => onCommand('italic')}>I</button>
      <button onClick={() => onCommand('formatBlock', 'h3')}>Heading</button>
      <button onClick={() => onCommand('formatBlock', 'p')}>Action</button>
      <button onClick={() => onCommand('formatBlock', 'blockquote')}>Dialogue</button>
    </div>
  );
}

export default HeaderToolbar;