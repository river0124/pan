import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import fetch from 'node-fetch';

dotenv.config();

const app = express();
app.use(cors({ origin: 'http://localhost:3000' }));
app.use(express.json());

app.post('/api/analyze', async (req, res) => {
  const userPrompt = req.body.prompt;

  try {
    const response = await fetch(
      'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-002:generateContent?key=' + process.env.GEMINI_API_KEY,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contents: [{ parts: [{ text: userPrompt }] }]
        })
      }
    );

    const data = await response.json();
    console.log('📡 응답 코드:', response.status);
    console.log('🧠 Gemini 응답:', data);

    const reply = data.candidates?.[0]?.content?.parts?.[0]?.text || 'No response';
    res.json({ reply });
  } catch (err) {
    console.error('❌ Gemini 요청 실패:', err);
    res.status(500).json({ error: 'Gemini 요청 실패' });
  }
});

app.listen(3001, () => {
  console.log('✅ Gemini 백엔드 서버 실행 중: http://localhost:3001');
});