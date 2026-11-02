# Карта проекта: «Закупки» для медицинских учреждений

Продуктовый анализ за 2025 год и дорожная карта развития для сегмента «медицинские
учреждения и клиники». Цель — увеличить потенциально монетизируемую ценность продукта
на 20%.

В репозитории: исходные данные кейса, аналитика по каждому источнику, кластеризация
обратной связи, связка проблем с метриками, список идей, приоритизация по ICE и оценка
бизнес-эффекта. Всё собрано в статический сайт в папке `docs/`.

## Быстрый старт

### Посмотреть локально

```bash
python -m http.server 8000 --directory docs
```

Откройте <http://localhost:8000>.

### Опубликовать на GitHub Pages

1. Создайте пустой репозиторий на GitHub, например `zakupki-med-project-map`.
2. Загрузите содержимое этой папки (через веб-интерфейс или git):

   ```bash
   git init -b main
   git add .
   git commit -m "Карта проекта: анализ и инициативы"
   git remote add origin https://github.com/<username>/zakupki-med-project-map.git
   git push -u origin main
   ```

   Если git не установлен, на странице репозитория нажмите **Add file → Upload files**
   и перетащите папки целиком.

3. В репозитории: **Settings → Pages**.
4. **Source**: `Deploy from a branch`, **Branch**: `main`, **Folder**: `/docs`.
5. Сохраните. Через минуту сайт будет доступен по адресу
   `https://<username>.github.io/zakupki-med-project-map/`.

Файл `docs/.nojekyll` уже добавлен: GitHub отдаёт статику как есть, без сборки Jekyll.

## Структура

```text
.
├── analysis/                  исходные Markdown-артефакты (анализ)
├── artifacts/                 исходные Markdown-артефакты (результат)
├── data/                      исходные данные кейса
├── docs/                      собранный статический сайт (GitHub Pages)
│   ├── index.html
│   ├── analysis/*.html
│   ├── artifacts/*.html
│   ├── data/                  копии данных для скачивания
│   ├── assets/style.css
│   └── .nojekyll
├── assets/style.css           исходник стилей
├── build.py                   сборка docs/ из Markdown
├── requirements.txt
├── .gitignore
└── .gitattributes
```

`docs/` генерируется из Markdown. Правьте `.md` в `analysis/` и `artifacts/`,
затем пересоберите сайт:

```bash
pip install -r requirements.txt
python build.py
```

## Содержание

### Анализ данных

| # | Документ | О чём |
|---|---|---|
| 1 | [Продажи](artifacts/01a-analiz-sales.md) | Воронка по месяцам, конверсии, тренд полугодий |
| 2 | [Отказы](artifacts/02a-analiz-non-clients.md) | 16 анкет клиентов, не начавших пользоваться продуктом |
| 3 | [Удержание](artifacts/03a-analiz-retention.md) | Когорты, отток к 12-му месяцу, провалы |
| 4 | [Функции](artifacts/04a-analiz-features.md) | Adoption ключевых функций, запуски и обрывы |
| 5 | [Сценарий](artifacts/05a-analiz-user-flow.md) | Успешность шагов с учётом SLA |
| 6 | [Поддержка](artifacts/06a-analiz-support.md) | 30 обращений: темы, роли, учреждения |
| 7 | [Лояльные клиенты](artifacts/07a-analiz-loyal-feedback.md) | 16 интервью: ценность, удержание, заброшенные функции |
| 8 | [Качественная кластеризация](analysis/kachestvennaya-klasterizaciya.md) | Темы из трёх качественных источников |
| 9 | [Связка метрик](analysis/08a-svyazka-metrik.md) | Проблема → метрика → количественное подтверждение |

### Результат

| # | Документ | О чём |
|---|---|---|
| 10 | [Список идей](artifacts/spisok-idej.md) | 15 сырых идей, отсев, отклонённые |
| 11 | [Приоритизация по ICE](artifacts/prioritizirovannye-iniciativy.md) | Рейтинг 7 инициатив, волны, чувствительность |
| 12 | [Оценка бизнес-эффекта](artifacts/ocenka-biznes-effekta.md) | Монетизационные события, сценарии, разрыв цели |

### Исходные данные

| Файл | Содержание |
|---|---|
| [sales.csv](data/sales.csv) | Воронка по месяцам 2025 |
| [retention.csv](data/retention.csv) | Когортное удержание, месяцы 1–12 |
| [features.csv](data/features.csv) | Adoption функций по месяцам |
| [user_flow.csv](data/user_flow.csv) | Успешность шагов сценария с учётом SLA |
| [support.txt](data/support.txt) | 30 обращений в поддержку |
| [non_clients.txt](data/non_clients.txt) | 16 анкет отказов |
| [loyal_feedback.txt](data/loyal_feedback.txt) | 16 интервью лояльных клиентов |
| [case-description.md](data/case-description.md) | Условие кейса и ограничения |

## Методика

1. **Baseline** — по каждому файлу считаются факты, закономерности и отклонения.
2. **Кластеризация** — качественная обратная связь сводится в темы с частотами и ролями.
3. **Связка** — каждая тема связывается с метрикой и количественным подтверждением;
   в инициативы проходят только подтверждённые потери.
4. **Инициативы** — 15 идей, отсев, 7 приоритетных.
5. **Приоритизация** — ICE (Impact × Confidence × Ease), шкалы 1–10.
6. **Эффект** — единица измерения «монетизационное событие» (первая оплата, продление,
   возврат, апгрейд, подключение модуля); три сценария и покрытие цели +20%.

## Ограничения

- В данных нет цен, выручки и маржи: эффект выражен в событиях и процентных пунктах.
- В `retention.csv` нет причин оттока, в `features.csv` — разреза по тарифам.
  Связи «причина → отток» и «тариф → использование» — гипотезы.
- Оценки трудоёмкости (Ease) — допущения, в данных их нет.
- Базовый сценарий закрывает 49,0% цели; разрыв закрывается исследовательским треком.
  Детали — в [оценке бизнес-эффекта](artifacts/ocenka-biznes-effekta.md).

## Соответствие исходным файлам

Имена переведены в ASCII, чтобы ссылки на GitHub и GitHub Pages работали без
URL-кодирования. Содержимое не менялось, кроме обновления ссылок на новые имена.

| Исходный файл | Файл в репозитории |
|---|---|
| `Анализ/08a_анализ_связка_метрик.md` | `analysis/08a-svyazka-metrik.md` |
| `Анализ/Качественная кластеризация.md` | `analysis/kachestvennaya-klasterizaciya.md` |
| `Артефакты/01a_анализ_sales.md` | `artifacts/01a-analiz-sales.md` |
| `Артефакты/02a_анализ_non_clients.md` | `artifacts/02a-analiz-non-clients.md` |
| `Артефакты/03a_анализ_retention.md` | `artifacts/03a-analiz-retention.md` |
| `Артефакты/04a_анализ_features.md` | `artifacts/04a-analiz-features.md` |
| `Артефакты/05a_анализ_user_flow.md` | `artifacts/05a-analiz-user-flow.md` |
| `Артефакты/06a_анализ_support.md` | `artifacts/06a-analiz-support.md` |
| `Артефакты/07a_анализ_loyal_feedback.md` | `artifacts/07a-analiz-loyal-feedback.md` |
| `Артефакты/список идей.md` | `artifacts/spisok-idej.md` |
| `Артефакты/приоритезированные инициативы.md` | `artifacts/prioritizirovannye-iniciativy.md` |
| `Артефакты/оценка бизнес-эффекта и доп мероприятия для достижение цели.md` | `artifacts/ocenka-biznes-effekta.md` |

## Примечание

Учебный кейс. Данные обезличены и предоставлены в рамках задания; публичные страницы
продукта — <https://zakupki.kontur.ru/site>.
