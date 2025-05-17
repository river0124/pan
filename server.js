import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import path from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url';

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
