import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from api_req import Weather
from api_key import API_KEY

weather_api = Weather(API_KEY)

def init_dash(server):
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    dash_app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Сравнение погоды по маршруту"), className="mb-4 mt-4", width=12)
        ]),
        dbc.Row([
            dbc.Col([
                dbc.Input(id='start-city', placeholder='Город отправления', type='text'),
            ], width=4),
            dbc.Col([
                dbc.Input(id='intermediate-cities', placeholder='Промежуточные города (через запятую)', type='text'),
            ], width=4),
            dbc.Col([
                dbc.Input(id='end-city', placeholder='Город назначения', type='text'),
            ], width=4),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col([
                dbc.Label("Количество дней прогноза:"),
                dcc.Dropdown(
                    id='forecast-days',
                    options=[
                        {'label': '1 день', 'value': 1},
                        {'label': '3 дня', 'value': 3},
                        {'label': '5 дней', 'value': 5},
                    ],
                    value=1,
                    clearable=False
                ),
            ], width=3),
            dbc.Col([
                dbc.Button("Показать на графиках", id='submit-button', color="primary", className="mt-4"),
            ], width=2),
        ], className="mb-4"),

        dbc.Alert(id='validation-alert', is_open=False, duration=4000, color="danger"),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='temp-graph')
            ], width=12, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='wind-speed-graph')
            ], width=12, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='humidity-graph')
            ], width=12, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='rain-prob-graph')
            ], width=12, className="mb-4"),
        ]),
    ], fluid=True)

    @dash_app.callback(
        [
            Output('temp-graph', 'figure'),
            Output('wind-speed-graph', 'figure'),
            Output('humidity-graph', 'figure'),
            Output('rain-prob-graph', 'figure'),
            Output('validation-alert', 'children'),
            Output('validation-alert', 'is_open')
        ],
        [Input('submit-button', 'n_clicks')],
        [
            State('start-city', 'value'),
            State('intermediate-cities', 'value'),
            State('end-city', 'value'),
            State('forecast-days', 'value')
        ]
    )
    def update_graphs(n_clicks, start_city, intermediate_cities, end_city, forecast_days):
        if not n_clicks:
            # Возвращаем пустые фигуры и скрываем алерт
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "", False

        # Валидация обязательных полей
        if not start_city or not end_city:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Пожалуйста, заполните поля 'Город отправления' и 'Город назначения'.", True

        # Обработка вводимых городов
        cities = []
        if start_city:
            cities.append(start_city.strip().capitalize())
        if intermediate_cities:
            intermediates = [city.strip().capitalize() for city in intermediate_cities.split(",") if city.strip()]
            cities.extend(intermediates)
        if end_city:
            cities.append(end_city.strip().capitalize())

        if not cities:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Пожалуйста, введите хотя бы один город.", True

        # Инициализация данных для графиков
        temp_avg_data = {}
        wind_speed_data = {}
        humidity_data = {}
        rain_prob_data = {}
        dates = []

        for city in cities:
            forecast = weather_api.get_forecast_weather_data(city, days=forecast_days)
            if isinstance(forecast, tuple):
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"Ошибка для города {city}: {forecast}", True
            elif isinstance(forecast, int):
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"Ошибка при получении данных для города {city}: {forecast}", True
            elif not forecast:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, f"Нет данных для города {city}.", True

            for day in forecast:
                date = day['date']
                if date not in dates:
                    dates.append(date)

            # Сортировка дат
            dates = sorted(dates)

            # Вычисление средней температуры
            temp_avg_data[city] = [ (day['temp_min'] + day['temp_max']) / 2 for day in forecast ]
            wind_speed_data[city] = [ day['wind_speed'] for day in forecast ]
            humidity_data[city] = [ day['humidity'] for day in forecast ]
            rain_prob_data[city] = [ day['precipitation_prob'] for day in forecast ]

        # Создание графиков
        # График температуры
        fig_temp = go.Figure()
        for city in cities:
            fig_temp.add_trace(go.Scatter(
                x=dates,
                y=temp_avg_data[city],
                mode='lines+markers',
                name=city
            ))
        fig_temp.update_layout(
            title="Средняя Температура",
            xaxis_title="Дата",
            yaxis_title="Температура (°C)",
            legend_title="Города",
            template='plotly_white'
        )

        # График скорости ветра
        fig_wind = go.Figure()
        for city in cities:
            fig_wind.add_trace(go.Scatter(
                x=dates,
                y=wind_speed_data[city],
                mode='lines+markers',
                name=city
            ))
        fig_wind.update_layout(
            title="Скорость ветра",
            xaxis_title="Дата",
            yaxis_title="Скорость ветра (км/ч)",
            legend_title="Города",
            template='plotly_white'
        )

        # График влажности
        fig_humidity = go.Figure()
        for city in cities:
            fig_humidity.add_trace(go.Scatter(
                x=dates,
                y=humidity_data[city],
                mode='lines+markers',
                name=city
            ))
        fig_humidity.update_layout(
            title="Влажность",
            xaxis_title="Дата",
            yaxis_title="Влажность (%)",
            legend_title="Города",
            template='plotly_white'
        )

        # График вероятности дождя
        fig_rain = go.Figure()
        for city in cities:
            fig_rain.add_trace(go.Scatter(
                x=dates,
                y=rain_prob_data[city],
                mode='lines+markers',
                name=city
            ))
        fig_rain.update_layout(
            title="Вероятность дождя",
            xaxis_title="Дата",
            yaxis_title="Вероятность дождя (%)",
            legend_title="Города",
            template='plotly_white'
        )

        # Возвращаем графики и скрываем алерт
        return fig_temp, fig_wind, fig_humidity, fig_rain, "", False

    return dash_app