import React from 'react';
import './HeaderToolbar.css';

function HeaderToolbar({ onCommand, onHwpUpload }) {

  return (
    <div className="toolbar">
      <button onClick={() => onCommand('bold')}>B</button>
      <button onClick={() => onCommand('italic')}>I</button>
      <button onClick={() => onCommand('formatBlock', 'h3')}>Heading</button>
      <button onClick={() => onCommand('formatBlock', 'p')}>Action</button>
      <button onClick={() => onCommand('formatBlock', 'blockquote')}>Dialogue</button>
      <label className="upload-button">
        업로드
        <input
          type="file"
          accept=".hwp"
          style={{ display: 'none' }}
          onChange={(e) => {
            const file = e.target.files[0];
            if (file) {
              console.log('📂 업로드된 파일:', file.name);
              const formData = new FormData();
              formData.append('file', file);

              fetch('http://localhost:3001/api/convert-hwp-txt', {
                method: 'POST',
                body: formData,
              })
                .then((res) => res.json())
                .then((data) => {
                  console.log('✅ 서버 응답:', data);
                  if (typeof onHwpUpload === 'function') {
                    onHwpUpload(data.richText || '');
                  }
                })
                .catch((err) => {
                  console.error('❌ 업로드 실패:', err);
                });
            }
          }}
        />
      </label>
    </div>
  );
}

export default HeaderToolbar;