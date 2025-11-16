import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


class ResultsDisplay:
    def __init__(self):
        self.color_map = {
            0: '#1f77b4',  # синий
            1: '#ff7f0e',  # оранжевый
            2: '#2ca02c',  # зеленый
            3: '#d62728',  # красный
            4: '#9467bd',  # фиолетовый
            5: '#8c564b',  # коричневый
        }

    def display_cluster_summary(self, cluster_stats):
        """
        Отображение сводки по кластерам
        """
        st.header("📊 Сводка по кластерам")

        # Создаем красивую таблицу с характеристиками кластеров
        summary_data = []
        for cluster_id, stats in cluster_stats.iterrows():
            summary_data.append({
                'Кластер': f"Кластер {cluster_id}",
                'Тип поставщиков': stats['cluster_type'],
                'Кол-во поставщиков': int(stats['suppliers_count']),
                'Надежность (%)': f"{stats['delivery_rate_mean'] * 100:.1f}%",
                'Средняя цена (руб/т)': f"{stats['price_mean']:.0f}",
                'Качество (1-10)': f"{stats['quality_mean'] * 10:.1f}",
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, width='stretch', hide_index=True)

    def display_cluster_plot(self, result_df):
        """
        Визуализация кластеров в 3D пространстве
        """
        st.header("📈 Визуализация кластеров")

        # Создаем 3D scatter plot
        fig = px.scatter_3d(
            result_df,
            x='delivery_rate',
            y='price',
            z='quality',
            color='cluster',
            hover_name='Название поставщика',
            color_continuous_scale='viridis',
            title='Кластеризация поставщиков в 3D пространстве',
            labels={
                'delivery_rate': 'Надежность поставок',
                'price': 'Стоимость (руб/т)',
                'quality': 'Качество песка',
                'cluster': 'Кластер'
            }
        )

        fig.update_layout(
            scene=dict(
                xaxis_title='Надежность поставок',
                yaxis_title='Стоимость (руб/т)',
                zaxis_title='Качество песка'
            ),
            height=600
        )

        st.plotly_chart(fig, width='stretch')

    def display_pair_plot(self, result_df):
        """
        Попарные scatter plots для лучшего понимания данных
        """
        st.header("🔍 Детальный анализ признаков")

        # Создаем subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Надежность vs Стоимость',
                'Надежность vs Качество',
                'Стоимость vs Качество',
                'Распределение по кластерам'
            )
        )

        # Надежность vs Стоимость
        for cluster in sorted(result_df['cluster'].unique()):
            cluster_data = result_df[result_df['cluster'] == cluster]
            fig.add_trace(
                go.Scatter(
                    x=cluster_data['delivery_rate'],
                    y=cluster_data['price'],
                    mode='markers',
                    name=f'Кластер {cluster}',
                    marker=dict(color=self.color_map.get(cluster, '#000000')),
                    text=cluster_data['Название поставщика'],
                    hovertemplate='<b>%{text}</b><br>Надежность: %{x:.2f}<br>Цена: %{y:.0f} руб<extra></extra>',
                    showlegend=True
                ),
                row=1, col=1
            )

        # Надежность vs Качество
        for cluster in sorted(result_df['cluster'].unique()):
            cluster_data = result_df[result_df['cluster'] == cluster]
            fig.add_trace(
                go.Scatter(
                    x=cluster_data['delivery_rate'],
                    y=cluster_data['quality'],
                    mode='markers',
                    name=f'Кластер {cluster}',
                    marker=dict(color=self.color_map.get(cluster, '#000000')),
                    text=cluster_data['Название поставщика'],
                    hovertemplate='<b>%{text}</b><br>Надежность: %{x:.2f}<br>Качество: %{y:.2f}<extra></extra>',
                    showlegend=False
                ),
                row=1, col=2
            )

        # Стоимость vs Качество
        for cluster in sorted(result_df['cluster'].unique()):
            cluster_data = result_df[result_df['cluster'] == cluster]
            fig.add_trace(
                go.Scatter(
                    x=cluster_data['price'],
                    y=cluster_data['quality'],
                    mode='markers',
                    name=f'Кластер {cluster}',
                    marker=dict(color=self.color_map.get(cluster, '#000000')),
                    text=cluster_data['Название поставщика'],
                    hovertemplate='<b>%{text}</b><br>Цена: %{x:.0f} руб<br>Качество: %{y:.2f}<extra></extra>',
                    showlegend=False
                ),
                row=2, col=1
            )

        # Распределение по кластерам (bar plot)
        cluster_counts = result_df['cluster'].value_counts().sort_index()
        fig.add_trace(
            go.Bar(
                x=[f'Кластер {i}' for i in cluster_counts.index],
                y=cluster_counts.values,
                marker_color=[self.color_map.get(i, '#000000') for i in cluster_counts.index],
                showlegend=False
            ),
            row=2, col=2
        )

        fig.update_layout(height=800, showlegend=True)
        st.plotly_chart(fig, width='stretch')

    def display_raw_data(self, result_df, cluster_stats):
        """
        Отображение исходных данных с метками кластеров
        """
        st.header("📋 Результаты кластеризации")

        # Создаем маппинг номеров кластеров на их типы
        cluster_mapping = {}
        for cluster_id, stats in cluster_stats.iterrows():
            cluster_mapping[cluster_id] = stats['cluster_type']

        # Создаем копию данных и заменяем номера кластеров на их типы
        display_df = result_df.copy()
        display_df['cluster_type'] = display_df['cluster'].map(cluster_mapping)

        # Показываем таблицу с результатами
        display_columns = [
            'Название поставщика',
            'cluster_type',
            'Коэффициент выполнения поставок в срок (%)',
            'Стоимость 1 тонны песка (руб)',
            'Содержание примесей (%)'
        ]

        display_df = display_df[display_columns].copy()

        # Переименовываем для красоты
        column_names = {
            'cluster_type': 'Тип кластера',
            'Название поставщика': 'Поставщик',
            'Коэффициент выполнения поставок в срок (%)': 'Надежность (%)',
            'Стоимость 1 тонны песка (руб)': 'Цена (руб/т)',
            'Содержание примесей (%)': 'Примеси (%)'
        }
        display_df.rename(columns=column_names, inplace=True)

        st.dataframe(display_df, width='stretch', hide_index=True)


# Создаем глобальный экземпляр display
results_display = ResultsDisplay()