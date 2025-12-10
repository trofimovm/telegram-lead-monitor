# LiteLLM Proxy - Изолированная документация сервиса

## Резюме

Это документация по LiteLLM Proxy как самостоятельному сервису (llm.codenrock.com), который можно подключить к любому продукту. Информация полностью изолирована от основного приложения Vibe Assessment.

---

## 1. Что такое LiteLLM Proxy

**LiteLLM Proxy** - унифицированный прокси-сервер для доступа к 100+ LLM провайдерам через единый OpenAI-совместимый API.

| Параметр | Значение |
|----------|----------|
| **URL** | https://llm.codenrock.com |
| **Протокол** | HTTPS (Let's Encrypt автообновление) |
| **API** | OpenAI-совместимый (`/v1/chat/completions`) |
| **Аутентификация** | Bearer Token (LITELLM_MASTER_KEY) |
| **Image** | `ghcr.io/berriai/litellm:main-stable` |

---

## 2. Аутентификация

### Master Key
```
LITELLM_MASTER_KEY=sk-litellm-5d72bc9cb76846620c011e7708fcf4c9
```

### Использование в запросах
```bash
curl -X POST https://llm.codenrock.com/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-5d72bc9cb76846620c011e7708fcf4c9" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

---

## 3. Доступные модели

### OpenAI (primary)
| Model Name | Actual Model | Temperature | Max Tokens | Cost (input/output per 1K) |
|------------|--------------|-------------|------------|---------------------------|
| `gpt-5-mini` | gpt-5-mini-2025-08-07 | 1.0 | 400,000 | $0.00075 / $0.003 |
| `gpt-4o` | gpt-4o | 0.7 | 128,000 | $0.002 / $0.006 |
| `gpt-4o-mini` | gpt-4o-mini | 0.7 | 128,000 | $0.00015 / $0.0006 |

### Anthropic (secondary)
| Model Name | Actual Model | Temperature | Max Tokens | Cost (input/output per 1K) |
|------------|--------------|-------------|------------|---------------------------|
| `claude-opus-4.1` | claude-3-opus-20240229 | 0.7 | 200,000 | $0.015 / $0.075 |
| `claude-sonnet-4` | claude-3-5-sonnet-20241022 | 0.7 | 200,000 | $0.003 / $0.015 |
| `claude-opus-4-5-20251101` | claude-opus-4-5-20251101 | 0.1 | 200,000 | $0.015 / $0.075 |

### Google (tertiary)
| Model Name | Actual Model | Temperature | Max Tokens | Cost (input/output per 1K) |
|------------|--------------|-------------|------------|---------------------------|
| `gemini-2.5-pro` | gemini-1.5-pro | 0.7 | 2,000,000 | $0.00125 / $0.005 |
| `gemini-2.0-flash` | gemini-1.5-flash | 0.7 | 1,000,000 | $0.000075 / $0.0003 |

---

## 4. Fallback стратегии

Если основная модель недоступна, автоматически переключается на fallback:

```yaml
gpt-5-mini → gpt-4o → claude-opus-4.1 → gemini-2.5-pro
gpt-4o → gpt-4o-mini → claude-sonnet-4 → gemini-2.0-flash
claude-opus-4.1 → claude-sonnet-4 → gpt-4o → gemini-2.5-pro
gemini-2.5-pro → gemini-2.0-flash → gpt-4o → claude-sonnet-4
```

---

## 5. API Endpoints

### Chat Completions (основной)
```bash
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer sk-litellm-5d72bc9cb76846620c011e7708fcf4c9

{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

### Health Checks
```bash
GET /health              # Basic health
GET /health/readiness    # Readiness probe (используется K8s)
GET /health/liveliness   # Liveness probe
```

### Утилиты
```bash
GET /models              # Список доступных моделей
GET /usage               # Статистика использования
GET /metrics             # Prometheus метрики
```

### UI и документация
```
GET /docs                # Swagger UI
GET /ui                  # Admin UI (login: admin / sk-litellm-5d72bc9cb76846620c011e7708fcf4c9)
```

---

## 6. Rate Limiting

### NGINX Ingress (внешний)
- **100 RPS** per IP address
- **Burst multiplier**: 5x (до 500 RPS в пиковые моменты)

### LiteLLM Internal
- **1000 RPM** per model (requests per minute)
- **3 retries** с задержкой 2 секунды
- **10 минут** timeout на запрос

---

## 7. Пример интеграции (TypeScript)

```typescript
import axios from 'axios';

class LiteLLMClient {
  private baseUrl = 'https://llm.codenrock.com';
  private masterKey = 'sk-litellm-5d72bc9cb76846620c011e7708fcf4c9';

  async chatCompletion(
    model: string,
    messages: Array<{role: string; content: string}>,
    options?: {temperature?: number; max_tokens?: number}
  ): Promise<string> {
    const response = await axios.post(
      `${this.baseUrl}/v1/chat/completions`,
      {
        model,
        messages,
        temperature: options?.temperature ?? 0.7,
        max_tokens: options?.max_tokens ?? 1000,
      },
      {
        headers: {
          'Authorization': `Bearer ${this.masterKey}`,
          'Content-Type': 'application/json',
        },
        timeout: 600000, // 10 минут
      }
    );

    return response.data.choices[0].message.content;
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseUrl}/health/readiness`);
      return response.status === 200;
    } catch {
      return false;
    }
  }

  async getModels(): Promise<string[]> {
    const response = await axios.get(`${this.baseUrl}/models`, {
      headers: { 'Authorization': `Bearer ${this.masterKey}` }
    });
    return response.data.data.map((m: any) => m.id);
  }
}

// Использование
const client = new LiteLLMClient();
const answer = await client.chatCompletion(
  'gpt-4o-mini',
  [{ role: 'user', content: 'What is 2+2?' }]
);
console.log(answer);
```

---

## 8. Пример интеграции (Python)

```python
import requests

class LiteLLMClient:
    def __init__(self):
        self.base_url = "https://llm.codenrock.com"
        self.master_key = "sk-litellm-5d72bc9cb76846620c011e7708fcf4c9"

    def chat_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        response = requests.post(
            f"{self.base_url}/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.master_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=600  # 10 минут
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health/readiness")
            return response.status_code == 200
        except:
            return False

# Использование
client = LiteLLMClient()
answer = client.chat_completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 2+2?"}]
)
print(answer)
```

---

## 9. Пример интеграции (cURL)

```bash
# Health check
curl https://llm.codenrock.com/health/readiness

# Chat completion
curl -X POST https://llm.codenrock.com/v1/chat/completions \
  -H "Authorization: Bearer sk-litellm-5d72bc9cb76846620c011e7708fcf4c9" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Explain quantum computing in 2 sentences."}
    ],
    "temperature": 0.7,
    "max_tokens": 200
  }'

# Список моделей
curl -H "Authorization: Bearer sk-litellm-5d72bc9cb76846620c011e7708fcf4c9" \
  https://llm.codenrock.com/models
```

---

## 10. Безопасность

### Слои защиты
1. **HTTPS** - Let's Encrypt с автообновлением
2. **API Key** - Bearer token в каждом запросе
3. **Rate Limiting** - NGINX (100 RPS) + LiteLLM internal (1000 RPM)
4. **Fallbacks** - автоматическое переключение при ошибках

### Важно
- IP whitelist **отключен** (для доступа из динамических IP)
- Не делитесь LITELLM_MASTER_KEY публично
- Храните ключ в переменных окружения или secrets

---

## 11. Инфраструктура (для DevOps)

### Kubernetes ресурсы
- **Deployment**: 3 реплики (autoscaling 3-10)
- **CPU**: 500m request, 1000m limit
- **Memory**: 1Gi request, 2Gi limit
- **Port**: 4000

### Зависимости
- **PostgreSQL**: litellm:litellm-db-pass-2025@postgres-service:5432/litellm
- **NGINX Ingress Controller**
- **cert-manager** для SSL

### Health Probes
```yaml
livenessProbe:
  httpGet:
    path: /health/readiness
    port: 4000
  initialDelaySeconds: 60
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /health/readiness
    port: 4000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## 12. Troubleshooting

### 401 Unauthorized
**Причина**: Неверный или отсутствующий API ключ
```bash
# Проверить что используется правильный ключ
echo "sk-litellm-5d72bc9cb76846620c011e7708fcf4c9"
```

### 429 Too Many Requests
**Причина**: Превышен rate limit (>100 RPS)
**Решение**: Добавить экспоненциальный backoff в клиенте

### 500 Internal Server Error
**Причина**: Проблема с upstream провайдером (OpenAI/Anthropic)
**Решение**: Fallback автоматически переключит на альтернативную модель

### Timeout (>10 минут)
**Причина**: Сложный запрос или перегрузка модели
**Решение**: Разбить на несколько запросов или использовать streaming

---

## 13. Рекомендации для нового продукта

### Environment Variables
```bash
LITELLM_PROXY_URL=https://llm.codenrock.com
LITELLM_MASTER_KEY=sk-litellm-5d72bc9cb76846620c011e7708fcf4c9
```

### Рекомендуемые модели по use-case
| Use Case | Рекомендуемая модель | Причина |
|----------|---------------------|---------|
| Быстрые ответы | `gpt-4o-mini` | Дешево, быстро |
| Сложные задачи | `gpt-4o` или `claude-sonnet-4` | Высокое качество |
| Длинный контекст | `gemini-2.5-pro` | 2M tokens context |
| Минимальная цена | `gemini-2.0-flash` | Самая дешевая |
| Максимальное качество | `claude-opus-4.1` | Лучшее качество |

### Retry логика
```typescript
async function withRetry<T>(fn: () => Promise<T>, maxRetries = 3): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * Math.pow(2, i)));
    }
  }
  throw new Error('Max retries reached');
}
```

---

## Файлы конфигурации (для справки)

Все файлы находятся в директории `litellm/` в репозитории testsys:

| Файл | Назначение |
|------|-----------|
| `proxy_config.yaml` | Конфигурация моделей, fallbacks, rate limits |
| `secrets.yaml` | Kubernetes secrets (API ключи) |
| `deployment-simple.yaml` | Kubernetes Deployment |
| `service.yaml` | Kubernetes Service |
| `ingress.yaml` | Ingress с SSL и rate limiting |
| `hpa.yaml` | Horizontal Pod Autoscaler |
| `QUICK_DEPLOY.md` | Быстрый старт |
| `OPEN_ACCESS_GUIDE.md` | Полное руководство |
