import express from 'express';
import fetch from 'node-fetch';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json({ limit: '20mb' }));

const API_KEY = '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'; // nova chave

app.post('/analisar', async (req, res) => {
    try {
        const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req.body)
        });

        const data = await response.json();
        res.json(data);
    } catch (err) {
        res.status(500).json({ error: 'Erro ao se comunicar com OpenRouter.', details: err.message });
    }
});

app.listen(5000, () => {
    console.log('✅ Backend rodando em http://localhost:5000');
}); 