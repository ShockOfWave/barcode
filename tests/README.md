# Тесты для afm_tda_tools

Этот каталог содержит unit тесты для пакета `afm_tda_tools`.

## Структура тестов

- `test_analyzers.py` - тесты для анализаторов (AutocorrelationAnalyzer, PersistenceAnalyzer, MinMaxAnalyzer, BottleneckAnalyzer)
- `test_api.py` - тесты для API функций
- `test_pipeline.py` - тесты для AnalysisPipeline

## Запуск тестов

### Установка зависимостей для тестирования

```bash
uv add --group dev pytest pytest-cov pytest-mock
```

### Запуск всех тестов

```bash
# Используя uv
uv run pytest

# Или напрямую
pytest
```

### Запуск конкретных тестов

```bash
# Тесты только анализаторов
uv run pytest tests/test_analyzers.py

# Тесты только API
uv run pytest tests/test_api.py

# Тесты только pipeline
uv run pytest tests/test_pipeline.py

# Конкретный тест
uv run pytest tests/test_analyzers.py::TestAutocorrelationAnalyzer::test_autocorrelation_computation
```

### Запуск тестов с покрытием

```bash
uv run pytest --cov=afm_tda_tools --cov-report=html
```

После этого откройте `htmlcov/index.html` в браузере для просмотра отчета о покрытии.

### Запуск тестов с реальными данными

Тесты с реальными данными помечены маркером `real_data` и требуют наличия файлов в `test_files/`:

```bash
# Запуск тестов с реальными данными
uv run pytest -m real_data

# Запуск тестов без реальных данных
uv run pytest -m "not real_data"
```

### Запуск быстрых тестов

```bash
# Исключить медленные тесты
uv run pytest -m "not slow"
```

## Типы тестов

### Unit тесты
- Тестируют отдельные компоненты изолированно
- Используют мок-данные или временные файлы
- Быстрые и не требуют внешних зависимостей

### Интеграционные тесты
- Тестируют взаимодействие между компонентами
- Могут использовать реальные данные
- Помечены маркером `integration`

### Тесты с реальными данными
- Используют файлы из `test_files/`
- Проверяют работу с реальными AFM данными
- Помечены маркером `real_data`

## Фикстуры

Тесты используют pytest фикстуры для:
- Создания временных файлов и директорий
- Генерации тестовых данных
- Настройки окружения

## Добавление новых тестов

1. Создайте новый файл `test_*.py` в каталоге `tests/`
2. Импортируйте тестируемые модули
3. Создайте классы тестов, наследующие от `unittest.TestCase` или используя pytest
4. Добавьте маркеры для категоризации тестов
5. Запустите тесты для проверки

## Пример добавления теста

```python
import pytest
from afm_tda_tools.your_module import YourClass

class TestYourClass:
    def test_your_method(self):
        """Тест для вашего метода."""
        obj = YourClass()
        result = obj.your_method()
        assert result is not None
        assert isinstance(result, expected_type)
```

## Отладка тестов

```bash
# Запуск с подробным выводом
uv run pytest -v

# Запуск с отладочной информацией
uv run pytest -s

# Запуск конкретного теста с отладкой
uv run pytest tests/test_analyzers.py::TestAutocorrelationAnalyzer::test_autocorrelation_computation -s -v
``` 