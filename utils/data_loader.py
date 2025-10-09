import pandas as pd
import streamlit as st
from io import StringIO


class DataLoader:
    def __init__(self):
        self.data_sources = {
            'supply_journal': None,
            'price_registry': None,
            'quality_claims': None,
            'production_plan': None,
            'budget': None,
            'suppliers': None
        }

    def load_csv(self, file, data_type):
        """Загрузка данных из CSV"""
        try:
            df = pd.read_csv(file)
            self.data_sources[data_type] = df
            return df
        except Exception as e:
            st.error(f"Ошибка загрузки файла: {e}")
            return None

    def get_data(self, data_type):
        """Получение данных по типу"""
        return self.data_sources.get(data_type)

    def get_available_data(self):
        """Получение списка загруженных данных"""
        return {k: v is not None for k, v in self.data_sources.items()}


# Глобальный экземпляр загрузчика
data_loader = DataLoader()


# Функции для обратной совместимости
def load_supply_journal(csv_file=None):
    if csv_file:
        return data_loader.load_csv(csv_file, 'supply_journal')
    # TODO: Добавить загрузку из БД позже
    return None