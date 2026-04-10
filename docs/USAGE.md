# 📄 Guia de Uso — API de Extração de Comprovantes com Gemini

## Variáveis de Ambiente

| Variável         | Obrigatória | Descrição                                    |
|------------------|-------------|----------------------------------------------|
| `GEMINI_API_KEY` | Sim         | Chave de autenticação da API do Google Gemini |

```bash
export GEMINI_API_KEY="sua-chave-aqui"
```

> ⚠️ Nunca versione a chave. Adicione `.env` ao `.gitignore`.

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Subindo a API

```bash
uvicorn src.main:app --env-file .env --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`.

---

## Endpoint

### `POST /api/receipt`

Envia uma imagem de comprovante financeiro (via URL pública do Google Drive) para extração de dados e classificação automática como income ou expense.

### Request

```json
{
  "url": "https://drive.google.com/file/d/SEU_FILE_ID/view?usp=sharing",
  "webhook_url": "https://webhook.site/seu-endpoint"
}
```

| Campo         | Tipo   | Obrigatório | Descrição                                     |
|---------------|--------|-------------|------------------------------------------------|
| `url`         | string | Sim         | URL de compartilhamento público do Google Drive |
| `webhook_url` | string | Sim         | URL que receberá os dados extraídos via POST    |

> A imagem no Google Drive **deve estar com compartilhamento público** ("Qualquer pessoa com o link").

### Response — Sucesso (200)

```json
{
  "datetime": "2026-03-15T14:30:00",
  "amount": 187.50,
  "type": "expense",
  "receipt_url": "https://drive.google.com/file/d/SEU_FILE_ID/view?usp=sharing",
  "webhook_status": "sent"
}
```

### Erros

| HTTP | Cenário                                              |
|------|------------------------------------------------------|
| 400  | URL ausente, formato inválido ou não é Google Drive  |
| 400  | `webhook_url` ausente ou inválida                    |
| 400  | Falha no download da imagem (arquivo privado/quebrado)|
| 401  | `GEMINI_API_KEY` não configurada                     |
| 422  | Gemini não conseguiu extrair dados do comprovante    |
| 429  | Rate limit da API do Gemini                          |
| 502  | Erro do Gemini ou falha ao enviar para o webhook     |
| 504  | Timeout na comunicação com o Gemini                  |

---

## Exemplos de Chamada

### cURL

```bash
curl -X POST http://localhost:8000/api/receipt \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://drive.google.com/file/d/SEU_FILE_ID/view?usp=sharing",
    "webhook_url": "https://webhook.site/seu-endpoint"
  }'
```

### Python (httpx)

```python
import httpx

response = httpx.post(
    "http://localhost:8000/api/receipt",
    json={
        "url": "https://drive.google.com/file/d/SEU_FILE_ID/view?usp=sharing",
        "webhook_url": "https://webhook.site/seu-endpoint",
    },
)
print(response.json())
```

---

## Formatos de Imagem Aceitos

Apenas **JPEG** e **PNG**. Outros formatos serão rejeitados com erro 400.

---

## Dicas

- Use o [webhook.site](https://webhook.site) para testar o recebimento dos dados extraídos.
- Imagens com boa resolução e texto legível geram melhores resultados.
- A classificação (income/expense) é feita pelo LLM — em caso de dúvida, revise manualmente.
