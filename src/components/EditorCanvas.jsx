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

    const requestBody = {
      contents: [
        {
          role: "user",
          parts: [
            {
              text: `다음 시나리오를 아래 JSON 형식으로 바꾸세요. 결과는 무조건 순수 JSON만 출력해야 하며, 마크다운이나 설명이 있으면 안됩니다.

[{
  "sceneNumber": "1",
  "heading": "씬 제목",
  "action": "지문",
  "dialogue": [
    {
      "character": "인물",
      "modifier": "수식어",
      "line": "대사"
    }
  ]
}]

**절대로 설명, 마크다운, 주석 없이 순수한 JSON 데이터만 반환해줘.**
**시작은 [ 로, 끝은 ] 로 해.**
**명령어는 "command" 키로 포함해줘.**

입력 시나리오:
${rawText}`
            }
          ]
        }
      ]
    };

    setLoading(true);

    try {
      const response = await fetch('http://localhost:3001/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      const aiText = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
      console.log('✅ Gemini 응답:', aiText);

      // JSON 배열만 정확히 추출 (줄바꿈 포함 허용)
      const jsonMatch = aiText.match(/^\s*(\[.*\])\s*$/s);
      if (!jsonMatch) {
        throw new Error('JSON 배열 형식이 아님');
      }

      const jsonText = jsonMatch[1];
      const parsed = JSON.parse(jsonText);
      setResult(JSON.stringify(parsed, null, 2));
    } catch (err) {
      console.error('❌ 분석 실패:', err);
      setResult('⚠️ JSON 분석 실패\n\n에러: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <HeaderToolbar 
        onCommand={handleCommand} 
        onHwpUpload={(hwpText) => {
          if (editorRef.current) {
            editorRef.current.innerHTML = hwpText;
          }
        }} 
      />
      
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
            overflowY: 'auto',
            maxHeight: '500px',
          }}
        >
          {result}
        </pre>
      )}
    </div>
  );
}

export default EditorCanvas;