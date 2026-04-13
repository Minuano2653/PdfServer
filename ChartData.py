from pydantic import BaseModel


class DataPoint(BaseModel):
    date: str    # "YYYY-MM-DD"
    value: float


class PatientReport(BaseModel):
    full_name: str            # ФИО пациента
    activity: float           # Активность пользователя (числовое)
    height: float             # Рост (см)
    weight: float             # Вес (кг)
    birth_date: str           # Дата рождения ("DD.MM.YYYY")
    email: str                # Почта
    psv_data: list[DataPoint] # ПСВ: [{"date": "2024-02-01", "value": 380.0}, ...]
    ast_data: list[DataPoint] # АСТ: [{"date": "2024-02-01", "value": 14.0}, ...]
