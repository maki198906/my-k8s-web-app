# My K8s Web App (FastAPI + Kubernetes)

Небольшое учебное приложение на FastAPI, упакованное в Docker и развёрнутое в локальном кластере Kubernetes (Kubernetes из Docker Desktop на macOS).

Цель репозитория — показать базовый путь:

**исходный код → Docker‑образ → Deployment → Service → Ingress → HTTP‑запрос из браузера.**

---

## Структура проекта

```text
my-k8s-web-app/
├─ app/
│  ├─ main.py        # FastAPI-приложение
│  └─ Dockerfile     # Образ с Python + FastAPI + uvicorn
│
├─ k8s/
│  ├─ deployment.yaml  # Deployment с 3 репликами
│  ├─ service.yaml     # ClusterIP Service для доступа к подам
│  └─ ingress.yaml     # Ingress (nginx) для внешнего HTTP-доступа
│
├─ .gitignore
└─ README.md
```

---

## Что делает приложение

Приложение — минимальный API на FastAPI с одним endpoint’ом:

- `GET /` — возвращает JSON с полями `status`, `message` и `hostname`.

`hostname` позволяет увидеть, из какого Pod’а Kubernetes пришёл ответ.

---

## 1. Локальный Docker‑образ

### Сборка образа

Из корня репозитория:

```bash
cd app
docker build -t my-k8s-web-app:v1 .
```

Образ содержит:

- Python (slim-образ),
- установленные `fastapi` и `uvicorn`,
- запуск `uvicorn main:app --host 0.0.0.0 --port 8080`.

### Тест локального контейнера (без Kubernetes)

```bash
docker run --rm -p 8080:8080 my-k8s-web-app:v1
```

Проверка:

- открыть в браузере `http://127.0.0.1:8080/`,
- увидеть JSON от FastAPI.

---

## 2. Локальный кластер Kubernetes (Docker Desktop)

Проект рассчитан на использование **Kubernetes внутри Docker Desktop** на macOS.

Шаги:

1. Открыть Docker Desktop → Settings → Kubernetes.  
2. Включить `Enable Kubernetes` и дождаться статуса `Running`.  
3. Проверить:

   ```bash
   kubectl config current-context
   kubectl get nodes
   ```

   Должна быть нода `docker-desktop` в статусе `Ready`.

---

## 3. Deployment и Service

### Применение манифестов

Из корня репозитория:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

Проверка состояния:

```bash
kubectl get deployments
kubectl get pods
kubectl get svc
```

Ожидается:

- Deployment `web-deployment` с 3 репликами.  
- Pods `web-deployment-...` в статусе `Running`.  
- Service `web-service` типа `ClusterIP` с портом `80/TCP`.

### Внутренний доступ через Service

Для локальной отладки можно пользоваться `port-forward`:

```bash
kubectl port-forward svc/web-service 8080:80
```

Потом открыть:

```text
http://127.0.0.1:8080/
```

и увидеть JSON уже **из Kubernetes** (включая `hostname` пода).

---

## 4. Ingress (nginx) и внешний HTTP‑доступ

### Установка nginx Ingress Controller

Один из вариантов для Docker Desktop:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.1/deploy/static/provider/cloud/deploy.yaml

kubectl get pods -n ingress-nginx
```

Нужно дождаться, пока pod `ingress-nginx-controller-...` будет в статусе `1/1 Running`.

### Применение Ingress

```bash
kubectl apply -f k8s/ingress.yaml
kubectl get ingress
```

Ожидается:

```text
NAME          CLASS   HOSTS                        ADDRESS     PORTS   AGE
web-ingress   nginx   kubernetes.docker.internal   localhost   80      ...
```

### Доступ через Ingress

Теперь можно зайти:

```text
http://kubernetes.docker.internal/
```

или:

```bash
curl http://kubernetes.docker.internal/
```

Маршрут запроса:

`браузер → ingress-nginx (localhost:80) → Ingress web-ingress → Service web-service:80 → Pods web-deployment-... :8080`.

---

## Кратко: роли объектов Kubernetes

- **Deployment**  
  Описывает желаемое количество подов и их шаблон (образ, порты, переменные окружения и т.д.) и поддерживает это состояние (3 реплики, rolling update и т.п.).

- **Service (ClusterIP)**  
  Даёт стабильное DNS‑имя и IP внутри кластера и по label’ам находит поды, балансируя трафик между ними.

- **Ingress**  
  Описывает правила входа HTTP/HTTPS трафика извне: по домену и пути направляет запросы к нужному Service.

---

## TODO (от простого к более сложному)

План дальнейшего развития проекта:

1. **Readiness и Liveness Probes**
   - Добавить `readinessProbe` и `livenessProbe` в `deployment.yaml` (HTTP‑проверки `/health`).
   - Потренироваться ломать/чинить приложение и смотреть, как k8s его перезапускает.

2. **Requests и Limits**
   - Задать `resources.requests` и `resources.limits` для CPU/памяти.
   - Посмотреть, как это влияет на планирование pod’ов.

3. **Horizontal Pod Autoscaler (HPA)**
   - Добавить HPA, который масштабирует Deployment по нагрузке (CPU).  
   - Смоделировать нагрузку и посмотреть динамику `replicas`.

4. **PersistentVolume / PersistentVolumeClaim**
   - Добавить PVC и примонтировать его в поды (`/data`).  
   - Проверить, что данные переживают перезапуск подов.

5. **ConfigMap и Secret**
   - Вынести конфигурацию (например, сообщения или флаги) в ConfigMap.  
   - Добавить Secret (например, фейковый API‑ключ) и примонтировать его в окружение контейнера.

6. **Более сложный Ingress**
   - Добавить второй сервис/endpoint и настроить path‑based routing (`/api`, `/admin` и т.п.).  
   - Поиграть с хостами и несколькими ingress‑правилами.

7. **Базовый CI/CD**
   - Добавить GitHub Actions workflow:
     - сборка Docker‑образа;  
     - пуш в registry (Docker Hub / GitHub Container Registry);  
     - деплой в локальный (или удалённый) кластер k8s через `kubectl apply`/`kustomize`.

8. **Monitoring / Logging (опционально)**
   - Подключить простое логирование и/или метрики (например, через сторонний стек).