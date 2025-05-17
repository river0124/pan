import React, { useRef, useState } from 'react';
import HeaderToolbar from './HeaderToolbar';
import './EditorCanvas.css';

function EditorCanvas() {
  const editorRef = useRef(null);
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleCommand = (command, value = null) => {
    document.execCommand(command, false, value);
    editorRef.current.focus();
  };

  const handleAnalyze = async () => {
    const rawText = editorRef.current.innerText;
    setLoading(true);

    try {
      const response = await fetch('http://localhost:3001/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: rawText }),
      });

      const data = await response.json();
      const aiReply = data.reply || 'No response';
      console.log('✅ Gemini 응답:', aiReply);
      setResult(aiReply);
    } catch (err) {
      console.error('❌ 분석 실패:', err);
      setResult('분석 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <HeaderToolbar onCommand={handleCommand} />
      
      <div
        className="editor-area"
        contentEditable
        ref={editorRef}
        suppressContentEditableWarning
      >
        {/* 여기에 시나리오를 입력하세요 */}
      </div>

      <div style={{ textAlign: 'right', padding: '10px' }}>
        <button onClick={handleAnalyze} disabled={loading}>
          {loading ? '분석 중...' : '🔍 분석하기'}
        </button>
      </div>

      {result && (
        <pre
          style={{
            whiteSpace: 'pre-wrap',
            background: '#f4f4f4',
            padding: '16px',
            marginTop: '20px',
          }}
        >
          {result}
        </pre>
      )}
    </div>
  );
}

export default EditorCanvas;