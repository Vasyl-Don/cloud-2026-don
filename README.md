# Cloud To-Do List — Лабораторні роботи з хмарних та GRID-технологій

## Структура проєкту

```
cloud-labs-project/
├── monolith/              # Монолітна версія застосунку
│   ├── app.py             # Flask додаток
│   ├── requirements.txt
│   ├── Dockerfile
│   └── templates/
│       └── index.html     # Веб-інтерфейс
├── microservices/         # Мікросервісна версія
│   ├── auth-service/      # Сервіс авторизації
│   ├── task-service/      # Сервіс завдань
│   └── gateway/           # Nginx API Gateway
├── .github/workflows/
│   └── ci-cd.yml          # CI/CD pipeline
├── docker-compose.yml     # Запуск моноліту
├── docker-compose.micro.yml  # Запуск мікросервісів
└── benchmark.py           # Скрипт порівняння
```

## Запуск

### Моноліт (Лаб. 1, 2)
```bash
docker-compose up --build
# Відкрити http://localhost:5000
```

### Мікросервіси (Лаб. 3)
```bash
docker-compose -f docker-compose.micro.yml up --build
# API доступний на http://localhost:8080
```

### Бенчмарк (Лаб. 3)
```bash
pip install requests
python benchmark.py --url http://localhost:5000 --label monolith
python benchmark.py --url http://localhost:8080 --label microservices
```

## Технології
- Python 3.11, Flask, SQLAlchemy
- PostgreSQL 15
- Docker, Docker Compose
- Nginx (API Gateway)
- GitHub Actions (CI/CD)
