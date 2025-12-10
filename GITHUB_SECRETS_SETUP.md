# GitHub Secrets Setup для CI/CD Deployment

## Шаги настройки

### 1. Перейти в Settings репозитория

Откройте https://github.com/trofimovm/telegram-lead-monitor/settings/secrets/actions

### 2. Добавить следующие секреты (кликнуть "New repository secret")

| Secret Name | Value | Описание |
|------------|-------|----------|
| `YC_TOKEN` | `y0__xCxju3JAhjB3RMgv6C6_RQ8ugkzvQTSwnJnZVGdgRVLgxsBCQ` | Yandex Cloud OAuth token |
| `YC_CLOUD_ID` | `b1gsl6g7471gj8sujq45` | Yandex Cloud ID |
| `YC_FOLDER_ID` | `b1gb15knepaprmtojrcj` | Yandex Folder ID |
| `KUBE_CONFIG_DATA` | См. ниже | Kubernetes config (base64) |
| `SECRET_KEY` | `b8f342b9b544b4db745213986ee1cc5d022ba264ade14b3af432f23a60dc4006` | JWT Secret Key (production) |
| `ENCRYPTION_KEY` | `b2X1iEuQh4YXlRyxnU8CZ_3Nw0Wlx4Dw6Haoj4ZnyMk=` | Fernet Encryption Key |
| `TELEGRAM_API_ID` | `25721776` | Telegram API ID |
| `TELEGRAM_API_HASH` | `2c056a0b7ec2a111e1b51386b053690d` | Telegram API Hash |
| `TELEGRAM_BOT_TOKEN` | `8478336010:AAEk-fhKNUMl_dfVaRWC88zrlrMF7SGWTLQ` | Telegram Bot Token |
| `LLM_API_KEY` | `sk-litellm-5d72bc9cb76846620c011e7708fcf4c9` | LLM API Key |
| `DATABASE_URL` | `postgresql://tgcatch-production-user:wL/gdck240/ABoNuXLVBO4Pn/glCglvp@rc1d-f5izic6e4i1828zt.mdb.yandexcloud.net:6432/tgcatch-production?sslmode=require` | PostgreSQL Connection String |
| `SMTP_USER` | (оставить пустым) | SMTP User (опционально) |
| `SMTP_PASSWORD` | (оставить пустым) | SMTP Password (опционально) |

### 3. Получить KUBE_CONFIG_DATA

Выполнить в терминале:

```bash
kubectl config view --flatten --minify | base64
```

Скопировать весь output (длинная base64 строка) и вставить как значение `KUBE_CONFIG_DATA` секрета.

### 4. Проверка

После добавления всех секретов должно быть **13 secrets** в списке:
- YC_TOKEN
- YC_CLOUD_ID
- YC_FOLDER_ID
- KUBE_CONFIG_DATA
- SECRET_KEY
- ENCRYPTION_KEY
- TELEGRAM_API_ID
- TELEGRAM_API_HASH
- TELEGRAM_BOT_TOKEN
- LLM_API_KEY
- DATABASE_URL
- SMTP_USER
- SMTP_PASSWORD

### 5. Запуск Deployment

После добавления всех секретов:

**Вариант A: Автоматически при push**
```bash
git add .
git commit -m "feat: add GitHub Actions CI/CD workflow"
git push
```

**Вариант B: Вручную через GitHub UI**
1. Перейти в Actions tab: https://github.com/trofimovm/telegram-lead-monitor/actions
2. Выбрать "Deploy to Yandex Cloud" workflow слева
3. Кликнуть "Run workflow" → "Run workflow"

### 6. Мониторинг Deployment

Открыть: https://github.com/trofimovm/telegram-lead-monitor/actions

Статус workflow покажет прогресс deployment. Если все OK, в конце будет:
- ✅ Build and push Backend image
- ✅ Build and push Frontend image
- ✅ Apply ConfigMaps
- ✅ Deploy Redis
- ✅ Deploy Backend
- ✅ Deploy Worker
- ✅ Deploy Frontend
- ✅ Apply Ingress

### 7. Проверка после Deployment

```bash
# Проверить pods
kubectl get pods -n tgcatch

# Проверить services
kubectl get services -n tgcatch

# Проверить ingress
kubectl get ingress -n tgcatch

# Логи backend
kubectl logs -l app=backend -n tgcatch --tail=50

# Логи worker
kubectl logs -l app=worker -n tgcatch --tail=50
```

## Troubleshooting

### Ошибка "ImagePullBackOff"
Проверить что `YC_TOKEN` правильный и registry доступен.

### Ошибка "CrashLoopBackOff"
Проверить логи пода:
```bash
kubectl logs <pod-name> -n tgcatch
```

### Ошибка в Init Container (migrations)
Проверить что `DATABASE_URL` правильный:
```bash
kubectl logs <backend-pod> -c db-migrate -n tgcatch
```

## DNS Настройка

После успешного deployment нужно настроить DNS A-запись:

1. Получить IP Load Balancer:
```bash
kubectl get ingress tgcatch-ingress -n tgcatch -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

2. В панели управления доменом tgcatch.ru создать A-запись:
   - Host: `@` (root)
   - Type: `A`
   - Value: IP из шага 1
   - TTL: 300 (5 минут)

3. Проверка DNS (через 5-10 минут):
```bash
dig tgcatch.ru +short
nslookup tgcatch.ru
```

4. Проверка HTTPS:
```bash
curl -I https://tgcatch.ru
```

SSL сертификат будет выпущен автоматически через cert-manager (Let's Encrypt) через 5-10 минут после настройки DNS.

## Next Steps

После успешного deployment:
1. Открыть https://tgcatch.ru
2. Зарегистрировать первого пользователя
3. Подключить Telegram аккаунт
4. Добавить источники (каналы)
5. Создать правила мониторинга
6. Проверить что лиды генерируются

🎉 Production готов!
