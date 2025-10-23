import warnings

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')


class ClusteringSolver:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        self.features = None

    def prepare_data(self, df):
        """
        Подготовка данных для кластеризации с русскими названиями колонок
        """
        # Создаем копию данных
        data = df.copy()

        # Проверяем наличие обязательных колонок
        required_columns = [
            'Название поставщика',
            'Коэффициент выполнения поставок в срок (%)',
            'Стоимость 1 тонны песка (руб)',
            'Содержание примесей (%)'
        ]

        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Отсутствуют обязательные колонки: {missing_columns}")

        # Подготавливаем признаки
        features_data = {}

        # 1. Коэффициент выполнения заказов (нормализуем к 0-1)
        features_data['delivery_rate'] = data['Коэффициент выполнения поставок в срок (%)'] / 100.0

        # 2. Стоимость песка
        features_data['price'] = data['Стоимость 1 тонны песка (руб)']

        # 3. Качество песка (инвертируем - чем меньше примесей, тем лучше)
        max_impurity = data['Содержание примесей (%)'].max()
        features_data['quality'] = 1 - (data['Содержание примесей (%)'] / max_impurity)

        # Сохраняем названия поставщиков
        features_data['supplier_name'] = data['Название поставщика']

        # Собираем все признаки в один DataFrame
        self.features = pd.DataFrame(features_data)

        return self.features

    def find_optimal_clusters(self, data, max_k=8):
        """
        Поиск оптимального количества кластеров методом локтя
        """
        wcss = []  # Within-Cluster Sum of Square
        silhouette_scores = []

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(data)
            wcss.append(kmeans.inertia_)

            if len(np.unique(kmeans.labels_)) > 1:
                score = silhouette_score(data, kmeans.labels_)
                silhouette_scores.append(score)
            else:
                silhouette_scores.append(0)

        # Находим оптимальное k (простой метод локтя)
        optimal_k = 3  # по умолчанию
        if len(wcss) > 2:
            # Ищем "локоть" - точку, где уменьшение WCSS замедляется
            reductions = [wcss[i - 1] - wcss[i] for i in range(1, len(wcss))]
            if reductions:
                optimal_k = np.argmax(np.array(reductions) < np.mean(reductions)) + 2

        return optimal_k, wcss, silhouette_scores

    def perform_clustering(self, df, n_clusters=None):
        """
        Выполнение кластеризации
        """
        # Подготовка данных
        features = self.prepare_data(df)

        # Масштабирование признаков
        scaled_features = self.scaler.fit_transform(features[['delivery_rate', 'price', 'quality']])

        # Определение оптимального количества кластеров
        if n_clusters is None:
            n_clusters, wcss, silhouette_scores = self.find_optimal_clusters(scaled_features)
        else:
            wcss, silhouette_scores = [], []

        # Кластеризация K-means
        self.model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.model.fit_predict(scaled_features)

        # Добавляем метки кластеров к исходным данным
        result_df = df.copy()
        result_df['cluster'] = cluster_labels
        result_df['delivery_rate'] = features['delivery_rate']
        result_df['price'] = features['price']
        result_df['quality'] = features['quality']

        # Рассчитываем характеристики кластеров
        cluster_stats = self.calculate_cluster_stats(result_df)

        return result_df, cluster_stats, (wcss, silhouette_scores)

    def calculate_cluster_stats(self, df):
        """
        Расчет статистики по кластерам
        """
        stats = df.groupby('cluster').agg({
            'delivery_rate': ['mean', 'std'],
            'price': ['mean', 'std'],
            'quality': ['mean', 'std'],
            'Название поставщика': 'count'
        }).round(2)

        stats.columns = ['delivery_rate_mean', 'delivery_rate_std',
                         'price_mean', 'price_std',
                         'quality_mean', 'quality_std',
                         'suppliers_count']

        # Добавляем интерпретацию кластеров
        stats['cluster_type'] = self.interpret_clusters(stats)

        return stats

    def interpret_clusters(self, stats):
        """
        Интерпретация кластеров на основе характеристик
        """
        interpretations = []

        for idx, row in stats.iterrows():
            delivery = row['delivery_rate_mean']
            price = row['price_mean']
            quality = row['quality_mean']

            if delivery > 0.90 and quality > 0.75:
                if price > stats['price_mean'].mean():
                    interpretations.append("Премиум-поставщики")
                else:
                    interpretations.append("Оптимальные поставщики")
            elif delivery < 0.7:
                interpretations.append("Ненадежные поставщики")
            elif price < stats['price_mean'].mean() * 0.85:
                interpretations.append("Бюджетные поставщики")
            elif quality < 0.5:
                interpretations.append("Поставщики с низким качеством")
            else:
                interpretations.append("Стандартные поставщики")

        return interpretations


# Создаем глобальный экземпляр solver
clustering_solver = ClusteringSolver()
