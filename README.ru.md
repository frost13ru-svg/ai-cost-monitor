# AI Cost Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/frost13ru-svg/ai-cost-monitor)](https://github.com/frost13ru-svg/ai-cost-monitor/releases)
[![Python](https://img.shields.io/badge/python-3.10%2B-informational)](pyproject.toml)
[![Dependencies](https://img.shields.io/badge/dependencies-0-success)](#возможности)

[**EN version**](README.md) · **RU**

CLI-утилита без зависимостей для бенчмарка **задержки (TTFB / время до первого токена)**
и **цен** провайдеров с OpenAI-совместимым API. Узнай, какой провайдер и модель
отвечают быстрее и стоят дешевле — до того, как встроишь их в продакшен.

## Зачем

У AI-маркетплейсов нестабильное время до первого токена (TTFT): одна и та же модель
может ответить за 1.5 с, а может висеть 18 с из-за очереди на «холодных» воркерах
провайдера. Эта утилита измеряет это за тебя крошечными, почти бесплатными
запросами (`max_tokens=1`).

## Возможности

- `probe` — серия стриминговых запросов к эндпоинту/модели, отчёт: лучший / медианный / худший TTFT
- `models` — каталог `/v1/models` провайдера с ценами за миллион токенов и скидками
- **Ноль зависимостей** — чистая стандартная библиотека Python (3.10+)
- Несколько эндпоинтов рядом в одном файле `.env`
- Структурированное логирование в `logs/ai-cost-monitor.log`

## Быстрый старт

```bash
git clone https://github.com/frost13ru-svg/ai-cost-monitor.git
cd ai-cost-monitor
cp .env.example .env      # заполни URL + KEY
./run.sh probe --model gpt-6-luna --runs 3
```

Или без лаунчера:

```bash
PYTHONPATH=src python3 -m ai_cost_monitor probe --model gpt-6-luna
PYTHONPATH=src python3 -m ai_cost_monitor models --limit 15
```

Или полноценная установка:

```bash
pip install -e .
ai-cost-monitor probe --model gpt-6-luna
```

## Конфигурация

Каждый эндпоинт — один блок в `.env`:

```ini
CHEAPERINFERENCE__URL=https://api.cheaperinference.com/v1
CHEAPERINFERENCE__KEY=ci_live_...
CHEAPERINFERENCE__REF=https://cheaperinference.com/?ref=9mQjzQYhrL   # опционально, показывается в отчётах
```

Переменные окружения имеют приоритет над файлом — удобно для CI.

## Пример вывода

```
[cheaperinference] model=gpt-6-luna
  Successful runs: 3 (failed: 0)
  First token — best: 1464 ms | median: 4190 ms | worst: 5 s

💡 Хочешь такие же цены? Регистрируйся по нашей реф-ссылке: https://cheaperinference.com/?ref=9mQjzQYhrL
```

## Безопасность для кошелька

Зонды шлют `max_tokens=1` с промптом из одного слова. На маркетплейсах вроде
CheaperInference полный прогон бенчмарка стоит доли цента. Утилита предупреждает
перед любым расходом.

## Архитектура

```
src/ai_cost_monitor/
├── cli.py            # парсинг аргументов и диспетчеризация
├── app.py            # оркестрация воркфлоу
├── config.py         # разбор .env -> объекты Endpoint
├── constants.py      # все таймауты/дефолты/системные строки
├── exceptions.py     # иерархия кастомных ошибок
├── models/           # домейн-типы (Endpoint, LatencyMeasurement, ModelPricing)
├── services/         # api_client, latency_probe, model_catalog
├── output/           # консольные отчёты
└── utils/            # логгер, форматирование
```

## Лицензия

MIT

---

💡 **Powered by [Cheaper Inference](https://cheaperinference.com/?ref=9mQjzQYhrL)** —
OpenAI-совместимый маркетплейс со скидками до 80% от прайса OpenAI, Anthropic,
DeepSeek, Z.ai и других. Пополнение от $5, без ежемесячных обязательств.
Регистрация по ссылке поддерживает этот проект.
