"""
Функция контекст-процессора"""
from datetime import date


def year(request):
    """Переменная с текущим годом."""
    return {"year": date.today().year}
