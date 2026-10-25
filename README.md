# Expense Tracker

Простое CLI-приложение для отслеживания личных расходов.

## Возможности

- Добавление расходов
- Просмотр списка расходов (активные и удалённые)
- Обновление расходов
- Мягкое удаление (soft delete через статус)
- Сводка расходов (общая и по месяцам)
- Установка месячного бюджета с отображением остатка
- Экспорт расходов в CSV

## Требования

- Python 3.7+

## Установка и запуск

```bash
python et.py --help
```

## Команды

### Добавить расход
```bash
py et.py add Lunch 100
py et.py add "Coffee with friends" 50
```

### Посмотреть список расходов
```bash
py et.py list
```

### Удалить расход
```bash
py et.py delete 1
```

### Обновить расход
```bash
py et.py update 1 "New description" 120
```

### Сводка расходов
```bash
py et.py summary          # общая сумма активных расходов
py et.py summary 10       # сумма за октябрь
```

### Установить бюджет на месяц
```bash
py et.py set-budget 10 5000
```

### Экспорт в CSV
```bash
py et.py export
py et.py export --output my_expenses.csv
```

## Хранение данных

- Расходы сохраняются в файле `expense-tracker.json`
- Бюджеты сохраняются в файле `budget.json`

## Пример использования

```bash
py et.py add Lunch 20
py et.py add Dinner 15
py et.py list
py et.py summary
py et.py set-budget 10 1000
py et.py delete 2
py et.py summary
py et.py export
```

## Особенности

- Удаление реализовано как soft delete (запись помечается статусом `deleted`)
- В списке отдельно отображаются активные и удалённые расходы
- При наличии бюджета в `list` показывается потраченная сумма и остаток
- Поддерживается экспорт всех расходов в CSV-файл

https://roadmap.sh/projects/expense-tracker