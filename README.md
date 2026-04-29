# 🔗 URL Shortener на Kubernetes

Учебный проект: полный цикл от Python-сервиса до продакшн-ready деплоя в Kubernetes.

## Стек

| Слой | Технологии |
|------|-----------|
| Backend | Python 3.11, FastAPI, SQLAlchemy, SQLite |
| Frontend | HTML/CSS/JS, nginx:alpine |
| Контейнеризация | Docker |
| Оркестрация | Kubernetes (Docker Desktop) |
| Балансировка | nginx Ingress Controller |
| Автоскейлинг | HPA + metrics-server |

## Архитектура

```
Browser
    │
    ▼
Ingress Controller (nginx)
    │
    ├─ /api/*  ──→  shortener-service  ──→  FastAPI pods (x2-6)
    ├─ /r/*    ──→  shortener-service  ──→  FastAPI pods
    └─ /*      ──→  frontend-service   ──→  nginx pod (UI)
                                               │
                                          PVC (SQLite)
```

## Структура проекта

```
my-k8s-web-app/
├── app/                        # FastAPI backend
│   ├── main.py                 # Эндпоинты + APIRouter
│   ├── config.py               # Конфигурация из env
│   ├── database.py             # SQLAlchemy engine + session
│   ├── models.py               # ORM модели
│   ├── schemas.py              # Pydantic схемы
│   ├── crud.py                 # CRUD операции
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # nginx + static UI
│   ├── index.html              # SPA: сокращение, статистика, admin
│   ├── nginx.conf
│   └── Dockerfile
├── k8s/                        # Kubernetes манифесты
│   ├── pvc.yaml                # 100Mi том для SQLite
│   ├── configmap.yaml          # BASE_URL, APP_NAME, APP_VERSION
│   ├── secret.yaml             # Структура (значения из .env)
│   ├── deployment.yaml         # 2-6 реплик, probes, resources
│   ├── service.yaml            # ClusterIP для FastAPI
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml   # ClusterIP для nginx
│   ├── ingress.yaml            # Path-based routing
│   └── hpa.yaml                # Автоскейлинг по CPU (цель 30%)
└── .env                        # Локальные секреты (в .gitignore!)
```

## API эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/shorten` | Создать короткую ссылку |
| `GET` | `/r/{code}` | Редирект по коду |
| `GET` | `/api/stats/{code}` | Статистика ссылки |
| `GET` | `/api/links` | Все ссылки (admin) |
| `DELETE` | `/api/links/{code}` | Удалить ссылку (admin) |
| `GET` | `/api/health` | Health check для K8s probes |
| `GET` | `/api/info` | Версия + hostname пода |

## Быстрый старт

### Требования

- Docker Desktop с включённым Kubernetes
- kubectl
- metrics-server (для HPA)

### 1. Настройка секретов

```bash
# Генерируем токен
openssl rand -hex 32

# Создаём .env
echo "ADMIN_TOKEN=<сгенерированный_токен>" > .env

# Добавляем в .gitignore
echo ".env" >> .gitignore
```

### 2. Сборка образов

```bash
docker build -t url-shortener:v1 ./app
docker build -t url-shortener-frontend:v1 ./frontend
```

### 3. Деплой в Kubernetes

```bash
# Секрет из .env
kubectl create secret generic shortener-secret --from-env-file=.env

# Все манифесты
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Проверка
kubectl get pods -w
```

### 4. Открываем UI

```
http://kubernetes.docker.internal
```

## Полезные команды

```bash
# Состояние кластера
kubectl get pods,svc,ingress,hpa,pvc

# Метрики подов
kubectl top pods

# Логи FastAPI
kubectl logs -l app=url-shortener --tail=50

# Обновить секрет
kubectl delete secret shortener-secret
kubectl create secret generic shortener-secret --from-env-file=.env
kubectl rollout restart deployment/url-shortener

# Нагрузочный тест (HPA)
hey -z 60s -c 50 -m POST \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/"}' \
  http://kubernetes.docker.internal/api/shorten
```

## Конфигурация

### ConfigMap (`k8s/configmap.yaml`)

| Ключ | Значение | Описание |
|------|---------|----------|
| `BASE_URL` | `http://kubernetes.docker.internal` | Базовый URL сервиса |
| `APP_NAME` | `URL Shortener` | Название приложения |
| `APP_VERSION` | `1.0.0` | Версия |

### Secret (из `.env`)

| Ключ | Описание |
|------|----------|
| `ADMIN_TOKEN` | Токен для admin-эндпоинтов (`X-Admin-Token` header) |

## HPA — Автоскейлинг

```
minReplicas: 2    maxReplicas: 6    targetCPUUtilization: 30%
```

Установка metrics-server для Docker Desktop:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system \
  --type "json" \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

## Что изучено

- [x] Docker: многослойная сборка, кеширование слоёв, `--no-cache`
- [x] K8s Deployment: rolling update, selector/labels, imagePullPolicy
- [x] PVC: персистентное хранилище, ReadWriteOnce
- [x] ConfigMap vs Secret: несекретные настройки vs токены
- [x] Readiness/Liveness Probes: защита от трафика на нездоровый под
- [x] Resources requests/limits: гарантированные и максимальные ресурсы
- [x] HPA: автоскейлинг по CPU, cooldown period
- [x] Path-based Ingress: маршрутизация по префиксу пути
- [x] Порядок маршрутов: конкретные пути до динамических (FastAPI и Ingress)
- [x] Rolling restart: `kubectl rollout restart` при обновлении ConfigMap/Secret
- [x] DNS: `/etc/hosts`, DoH, IPv4 vs IPv6, системный DNS

## TODO

- [ ] Cloudflare Tunnel — публичный доступ к локальному кластеру
- [ ] CI/CD — GitHub Actions: build → push → deploy
- [ ] Облачный деплой — DigitalOcean/GKE/Oracle Cloud
- [ ] PostgreSQL — замена SQLite для multi-node кластера
- [ ] Monitoring — Prometheus + Grafana
