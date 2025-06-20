import express from 'express';
import multer from 'multer';
import cors from 'cors';
import fetch from 'node-fetch'; // npm install node-fetch@2
import fs from 'fs';

const app = express();
const upload = multer({ dest: 'uploads/' });

app.use(cors({
  origin: 'http://localhost:3000', // or whatever your frontend port is
  credentials: true
}));

app.post('/upload', upload.single('file'), async (req, res) => {
  const filePath = req.file.path;
  try {
    const htmlContent = await fs.promises.readFile(filePath, 'utf8');
    // If you want to extract CSS separately, do so here. For now, just send empty string.
    const cssContent = "";

    const aiRes = await fetch('http://localhost:8000/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ html_content: htmlContent, css_content: cssContent })
    });
    const aiData = await aiRes.json();
    res.json(aiData);
  } catch (err) {
    res.status(500).json({ error: 'Failed to process with AI agent', details: err.message });
  } finally {
    fs.unlink(filePath, () => {}); // Clean up uploaded file
  }
});

app.listen(5000, () => {
  console.log('Backend listening on port 5000');
});