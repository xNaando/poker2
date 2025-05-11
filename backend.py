from flask import Flask, request, jsonify
import requests
import base64

app = Flask(__name__)

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "meta-llama/llama-4-maverick:free"

@app.route('/analisar', methods=['POST'])
def analisar():
    data = request.json
    prompt = data['prompt']
    image_b64 = data['image']

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
                ]
            }
        ]
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "X-Title": "Poker Analyzer"
    }
    response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
    if response.status_code == 200:
        resposta = response.json()["choices"][0]["message"]["content"]
        return jsonify({"resposta": resposta})
    else:
        return jsonify({"erro": "Erro ao consultar IA", "detalhe": response.text}), 500

if __name__ == '__main__':
    app.run(port=5000) 