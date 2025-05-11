import express from 'express';
import cors from 'cors';
import fetch from 'node-fetch';

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb' }));

const OPENROUTER_API_KEY = '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';
const OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions';
const MODEL = 'meta-llama/llama-4-maverick:free';

app.post('/analisar', async (req, res) => {
    try {
        const { prompt, image } = req.body;
        const payload = {
            model: MODEL,
            messages: [
                {
                    role: 'user',
                    content: [
                        { type: 'text', text: prompt },
                        { type: 'image_url', image_url: { url: `data:image/png;base64,${image}` } }
                    ]
                }
            ]
        };
        const response = await fetch(OPENROUTER_URL, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (response.ok) {
            res.json({ resposta: data.choices[0].message.content });
        } else {
            res.status(500).json({ erro: 'Erro ao consultar IA', detalhe: data });
        }
    } catch (err) {
        res.status(500).json({ erro: 'Erro no backend', detalhe: err.message });
    }
});

app.listen(5000, () => {
    console.log('Backend rodando em http://localhost:5000');
}); 