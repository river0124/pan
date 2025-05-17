import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';

// ES 모듈에서 __dirname 대체
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 환경 변수 로드
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// CORS 설정 (개발 중 필요 시 포트 열어줌)
app.use(cors({
  origin: 'http://localhost:3000',
}));

app.use(express.json());

// ✅ Gemini API 호출
app.post('/api/analyze', async (req, res) => {
  const userPrompt = req.body.prompt;

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-002:generateContent?key=${process.env.GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: userPrompt }] }],
        }),
      }
    );

    console.log('📡 응답 코드:', response.status);
    const data = await response.json();
    console.log('🧠 Gemini 응답:', JSON.stringify(data, null, 2));

    res.json(data);
  } catch (err) {
    console.error('❌ Gemini API 호출 실패:', err);
    res.status(500).json({ error: 'Gemini API 호출 실패' });
  }
});

import multer from 'multer';
import fs from 'fs';

// 파일 업로드를 위한 multer 설정
const upload = multer({ dest: 'uploads/' });

app.post('/api/convert-hwp-txt', upload.single('file'), (req, res) => {
  const filePath = req.file.path;
  console.log('📁 업로드된 파일 경로:', filePath);
  const outputPath = `${filePath}.txt`;

  const command = `hwp5txt --output ${outputPath} ${filePath}`;
  console.log('💻 실행할 커맨드:', command);
  exec(command, (err, stdout, stderr) => {
    console.log('📄 hwp5txt 실행 결과:', stdout);
    if (err) {
      console.error('❌ pyhwp 변환 실패:', stderr);
      return res.status(500).json({ error: 'HWP 변환 실패', detail: stderr });
    }

    console.log('📂 변환된 파일 경로:', outputPath);
    fs.readFile(outputPath, 'utf-8', (readErr, text) => {
      fs.unlinkSync(filePath);
      if (fs.existsSync(outputPath)) fs.unlinkSync(outputPath);

      if (readErr) {
        console.error('❌ 변환된 파일 읽기 실패:', readErr);
        return res.status(500).json({ error: '변환된 파일 읽기 실패' });
      }
      res.json({ richText: `<pre>${text}</pre>` });
    });
  });
});

// ✅ 정적 파일 서빙 (Vite build output)
app.use(express.static(path.join(__dirname, 'dist')));

// ✅ SPA 지원 (Vue/React Router용)
app.get(/^\/(?!api).*/, (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// ✅ 서버 시작
app.listen(PORT, () => {
  console.log(`✅ Gemini 백엔드 서버 실행 중: http://localhost:${PORT}`);
});
