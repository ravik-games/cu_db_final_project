# Итоговый проект по курсу БД

Автор: **Близниченко Алексей**
## Инструкция

**Запуск БД**:
```bash
docker-compose up
```

Скрипты для генерации и загрузки данных написаны LLM. Запуск:
```python
python -m pip install requirements.txt

python generation.py
# Между этими шагами нужно создать схемы
python load_data.py
```
Данные в формате .csv лежат в папке `data/`.

Скрипты на SQL лежат в `queries.sql`.

Изображения концептуальной и логической схем лежат в папке `images/` (делал в ERDPlus)