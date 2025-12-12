# Yandex Cloud Infrastructure Guide

**Общее руководство по развертыванию приложений в существующей инфраструктуре Yandex Cloud**

---

## Обзор инфраструктуры

Инфраструктура размещена в Yandex Cloud и включает:
- **Managed Kubernetes кластер** для запуска контейнеризованных приложений
- **Managed PostgreSQL** для баз данных
- **Container Registry** для хранения Docker образов
- **Application Load Balancer** для маршрутизации трафика
- **VPC с 3 зонами доступности** для высокой доступности

---

## Идентификаторы ресурсов

### Yandex Cloud
```
Cloud ID:     b1gsl6g7471gj8sujq45
Folder ID:    b1gb15knepaprmtojrcj
```

### Kubernetes
```
Cluster ID:   catq16c1d1eneue0lfh1
Cluster Name: main
Version:      1.29
Master IP:    51.250.43.40 (external) / 10.255.0.8 (internal)
```

### PostgreSQL
```
Cluster ID:   c9q81cb17vvrkt0e6rlc
Cluster Name: psql-gitlab-production
Host:         rc1d-f5izic6e4i1828zt.mdb.yandexcloud.net
Port:         6432
SSL:          required
```

### Container Registry
```
Registry ID (applications): crpf742dk953m6aqk69s
Registry ID (competitions): crpthrv6n8ipl0el255l
Registry URL:               cr.yandex/{registry-id}/
```

### Network
```
VPC ID:       enpngt9fglldjtfhjl33
VPC Name:     main
Zones:        ru-central1-a, ru-central1-b, ru-central1-d
```

---

## 1. Установка инструментов

### Yandex Cloud CLI
```bash
# macOS / Linux
curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
source ~/.bashrc  # или ~/.zshrc

# Проверка
yc --version
```

### kubectl
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Проверка
kubectl version --client
```

### Дополнительные инструменты
```bash
# jq для парсинга JSON
brew install jq  # macOS
apt-get install jq  # Linux

# Docker
brew install --cask docker  # macOS
# или https://docs.docker.com/engine/install/
```

---

## 2. Авторизация в Yandex Cloud

### Интерактивная авторизация (для разработки)
```bash
yc init
# Следуйте инструкциям, выберите cloud и folder
```

### Проверка текущего профиля
```bash
yc config list
# Должно показать:
# cloud-id: b1gsl6g7471gj8sujq45
# folder-id: b1gb15knepaprmtojrcj
```

### Переключение между профилями
```bash
# Список профилей
yc config profile list

# Активация профиля
yc config profile activate hackathon

# Создание нового профиля
yc config profile create my-profile
yc config set cloud-id b1gsl6g7471gj8sujq45
yc config set folder-id b1gb15knepaprmtojrcj
```

### Service Account (для CI/CD)
```bash
# Создание service account
yc iam service-account create --name my-app-sa

# Назначение ролей
yc resource-manager folder add-access-binding \
  --id b1gb15knepaprmtojrcj \
  --role container-registry.images.pusher \
  --service-account-name my-app-sa

yc resource-manager folder add-access-binding \
  --id b1gb15knepaprmtojrcj \
  --role k8s.admin \
  --service-account-name my-app-sa

# Создание ключа для CI/CD
yc iam key create \
  --service-account-name my-app-sa \
  --output my-app-sa-key.json
```

---

## 3. Подключение к Kubernetes

### Получение credentials
```bash
yc managed-kubernetes cluster get-credentials \
  --id catq16c1d1eneue0lfh1 \
  --external \
  --force

# Проверка подключения
kubectl cluster-info
kubectl get nodes
```

### Управление контекстами
```bash
# Список контекстов
kubectl config get-contexts

# Переключение контекста
kubectl config use-context yc-main

# Текущий контекст
kubectl config current-context
```

### Просмотр существующих namespaces
```bash
kubectl get namespaces
```

---

## 4. Работа с Container Registry

### Аутентификация Docker
```bash
yc container registry configure-docker
# Автоматически настраивает docker login для cr.yandex
```

### Сборка и push образа
```bash
# Сборка
docker build -t cr.yandex/crpf742dk953m6aqk69s/my-app:latest .

# Push
docker push cr.yandex/crpf742dk953m6aqk69s/my-app:latest

# С тегом версии
docker build -t cr.yandex/crpf742dk953m6aqk69s/my-app:v1.0.0 .
docker push cr.yandex/crpf742dk953m6aqk69s/my-app:v1.0.0
```

### Просмотр образов
```bash
yc container image list --registry-id crpf742dk953m6aqk69s
```

---

## 5. Работа с PostgreSQL

### Существующие базы данных
```
- psql-gitlab-db (psql-gitlab-user)
- psql-glitchtip-db (psql-glitchtip-user)
- psql-grafana-db (psql-grafana-user)
- psql-platform-staging (psql-platform-staging-user)
- psql-tg-bot-production (psql-tg-bot-production-user)
- psql-tg-bot-staging (psql-tg-bot-staging-user)
- psql-zitadel-db (psql-zitadel-user)
```

### Создание новой базы данных
```bash
# Создать пользователя
yc managed-postgresql user create my-app-user \
  --cluster-name psql-gitlab-production \
  --password "YOUR_SECURE_PASSWORD"

# Создать базу данных
yc managed-postgresql database create my-app-db \
  --cluster-name psql-gitlab-production \
  --owner my-app-user

# Connection string
postgresql://my-app-user:PASSWORD@rc1d-f5izic6e4i1828zt.mdb.yandexcloud.net:6432/my-app-db?sslmode=require
```

### Подключение к БД
```bash
# Через psql (требуется SSL)
psql "postgresql://my-app-user:PASSWORD@rc1d-f5izic6e4i1828zt.mdb.yandexcloud.net:6432/my-app-db?sslmode=require"

# Или через kubectl port-forward если включен internal access
```

---

## 6. GitHub Actions CI/CD

### Необходимые GitHub Secrets

**Инфраструктурные:**
```
YC_SERVICE_ACCOUNT_KEY   # JSON ключ service account
YC_CLOUD_ID              # b1gsl6g7471gj8sujq45
YC_FOLDER_ID             # b1gb15knepaprmtojrcj
YC_REGISTRY_ID           # crpf742dk953m6aqk69s (или другой)
YC_CLUSTER_ID            # catq16c1d1eneue0lfh1
```

**Для приложения:**
```
DB_HOST                  # rc1d-f5izic6e4i1828zt.mdb.yandexcloud.net
DB_PASSWORD              # Пароль от БД
JWT_SECRET               # Секрет для JWT (если нужен)
# ... другие секреты приложения
```

### Пример workflow: Build & Push

```yaml
name: Build and Push

on:
  push:
    branches: [develop]

env:
  YC_REGISTRY: cr.yandex

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install YC CLI
        run: |
          curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
          echo "$HOME/yandex-cloud/bin" >> $GITHUB_PATH

      - name: Configure YC CLI
        run: |
          echo "${{ secrets.YC_SERVICE_ACCOUNT_KEY }}" > key.json
          yc config profile create deploy
          yc config set service-account-key key.json
          yc config set cloud-id ${{ secrets.YC_CLOUD_ID }}
          yc config set folder-id ${{ secrets.YC_FOLDER_ID }}
          rm key.json
          yc container registry configure-docker

      - name: Build and Push
        run: |
          docker build -t $YC_REGISTRY/${{ secrets.YC_REGISTRY_ID }}/my-app:${{ github.sha }} .
          docker push $YC_REGISTRY/${{ secrets.YC_REGISTRY_ID }}/my-app:${{ github.sha }}
```

### Пример workflow: Deploy to K8s

```yaml
name: Deploy

on:
  push:
    branches: [develop]

env:
  NAMESPACE: my-app

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install YC CLI
        run: |
          curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
          echo "$HOME/yandex-cloud/bin" >> $GITHUB_PATH

      - name: Configure YC CLI
        run: |
          echo "${{ secrets.YC_SERVICE_ACCOUNT_KEY }}" > key.json
          yc config profile create deploy
          yc config set service-account-key key.json
          yc config set cloud-id ${{ secrets.YC_CLOUD_ID }}
          yc config set folder-id ${{ secrets.YC_FOLDER_ID }}
          rm key.json

      - name: Setup kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'v1.28.2'

      - name: Configure kubectl
        run: |
          yc managed-kubernetes cluster get-credentials \
            --id ${{ secrets.YC_CLUSTER_ID }} \
            --external --force

      - name: Create Namespace (if not exists)
        run: |
          kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

      - name: Create Secrets
        env:
          DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
        run: |
          DATABASE_URL="postgresql://my-app-user:${DB_PASSWORD}@${{ secrets.DB_HOST }}:6432/my-app-db?sslmode=require"
          kubectl create secret generic my-app-secrets -n $NAMESPACE \
            --from-literal=database-url="$DATABASE_URL" \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy
        run: |
          sed "s|IMAGE_TAG|${{ github.sha }}|g" k8s/deployment.yaml | kubectl apply -f -
          kubectl apply -f k8s/service.yaml
          kubectl wait --for=condition=available deployment/my-app \
            -n $NAMESPACE --timeout=300s
```

---

## 7. Kubernetes RBAC для CI/CD

Для работы GitHub Actions нужны права в Kubernetes:

```yaml
# github-actions-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: github-actions-deployer
  namespace: my-app  # Ваш namespace
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "statefulsets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["pods", "pods/log", "services", "configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: ["networking.k8s.io"]
    resources: ["ingresses"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: github-actions-deployer
  namespace: my-app
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: github-actions-deployer
subjects:
  - kind: User
    name: <SERVICE_ACCOUNT_ID>  # ID вашего service account
    apiGroup: rbac.authorization.k8s.io
```

Применение:
```bash
kubectl apply -f github-actions-role.yaml
```

---

## 8. Пример Kubernetes манифестов

### Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
  namespace: my-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: my-app
          image: cr.yandex/crpf742dk953m6aqk69s/my-app:IMAGE_TAG
          ports:
            - containerPort: 3000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: my-app-secrets
                  key: database-url
            - name: NODE_ENV
              value: "production"
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Service
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
  namespace: my-app
spec:
  type: ClusterIP
  ports:
    - port: 80
      targetPort: 3000
  selector:
    app: my-app
```

### Ingress (с SSL через cert-manager)
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  namespace: my-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts:
        - my-app.example.com
      secretName: my-app-tls
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app
                port:
                  number: 80
```

---

## 9. Полезные команды

### Диагностика
```bash
# Состояние кластера
kubectl get nodes
kubectl top nodes

# Pods в namespace
kubectl get pods -n my-app
kubectl describe pod <pod-name> -n my-app
kubectl logs <pod-name> -n my-app

# События
kubectl get events -n my-app --sort-by='.lastTimestamp'

# Ресурсы
kubectl top pods -n my-app
```

### Отладка
```bash
# Shell в pod
kubectl exec -it <pod-name> -n my-app -- /bin/sh

# Port forward для локального доступа
kubectl port-forward svc/my-app 3000:80 -n my-app
```

### Rollback
```bash
# История деплоев
kubectl rollout history deployment/my-app -n my-app

# Откат к предыдущей версии
kubectl rollout undo deployment/my-app -n my-app
```

---

## 10. Чеклист для нового приложения

1. **Создать базу данных:**
   ```bash
   yc managed-postgresql user create ...
   yc managed-postgresql database create ...
   ```

2. **Создать service account (если нужен отдельный):**
   ```bash
   yc iam service-account create ...
   yc iam key create ...
   ```

3. **Добавить GitHub Secrets:**
   - YC_SERVICE_ACCOUNT_KEY
   - YC_CLOUD_ID, YC_FOLDER_ID, YC_REGISTRY_ID, YC_CLUSTER_ID
   - DB_HOST, DB_PASSWORD
   - Другие секреты приложения

4. **Создать Kubernetes namespace:**
   ```bash
   kubectl create namespace my-app
   ```

5. **Применить RBAC:**
   ```bash
   kubectl apply -f github-actions-role.yaml
   ```

6. **Создать Kubernetes манифесты:**
   - deployment.yaml
   - service.yaml
   - ingress.yaml (если нужен внешний доступ)

7. **Настроить GitHub Actions workflows:**
   - build-push.yml
   - deploy.yml

8. **Настроить DNS:**
   - A-запись на IP Load Balancer

---

## Контакты и ресурсы

- **YC Console**: https://console.cloud.yandex.ru
- **YC CLI Docs**: https://yandex.cloud/ru/docs/cli/
- **Managed K8s Docs**: https://yandex.cloud/ru/docs/managed-kubernetes/
- **Managed PostgreSQL Docs**: https://yandex.cloud/ru/docs/managed-postgresql/
- **Pricing**: https://yandex.cloud/ru/prices

---

*Документ создан: 2025-12-09*

