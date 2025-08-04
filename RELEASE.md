# Инструкции по релизу на PyPI

## Подготовка к релизу

1. **Обновите версию** в `pyproject.toml` и `setup.py`
2. **Добавьте email** в `pyproject.toml` и `setup.py` (замените пустые строки на ваш email)
3. **Проверьте все файлы** включены в пакет

## Установка инструментов для релиза

```bash
# Установите build и twine
pip install build twine

# Или используя uv
uv add build twine --dev
```

## Сборка пакета

```bash
# Очистите предыдущие сборки
rm -rf dist/ build/ *.egg-info/

# Соберите пакет
python -m build

# Или используя uv
uv run python -m build
```

## Проверка пакета

```bash
# Проверьте пакет на ошибки
twine check dist/*

# Протестируйте установку
pip install dist/afm_tda_tools-0.1.0.tar.gz
```

## Загрузка на PyPI

### Тестовый PyPI (рекомендуется сначала)
```bash
# Загрузите на тестовый PyPI
twine upload --repository testpypi dist/*

# Установите с тестового PyPI
pip install --index-url https://test.pypi.org/simple/ afm-tda-tools
```

### Основной PyPI
```bash
# Загрузите на основной PyPI
twine upload dist/*
```

## Проверка установки

```bash
# Проверьте, что пакет установился
pip show afm-tda-tools

# Проверьте CLI команду
afm-tda-tools --help
```

## Обновление версии

Для обновления версии:

1. Измените версию в `pyproject.toml` и `setup.py`
2. Создайте git tag: `git tag v0.1.1`
3. Запустите сборку и загрузку заново

## Полезные команды

```bash
# Просмотр информации о пакете
pip show afm-tda-tools

# Удаление пакета
pip uninstall afm-tda-tools

# Проверка зависимостей
pip check afm-tda-tools
```

## Примечания

- Убедитесь, что имя пакета `afm-tda-tools` доступно на PyPI
- Проверьте, что все зависимости корректно указаны
- Убедитесь, что README.md корректно отображается на PyPI
- Тестируйте сначала на TestPyPI перед загрузкой на основной PyPI 