# импорт необходимых библиотек
import requests
import logging

logging.basicConfig(level=logging.INFO, filename='/log_info.log', filemode='w')

class Weather:

    def __init__(self, api_key):
        self.api_key = api_key
        self.loc_key = None
        self.cached_data = None

    # функция получения погоды по координатам
    def get_loc_key_by_coords(self, lat, lon):
        #получение location key
        loc_key_url = f'http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={self.api_key}&q={lat},{lon}'
        r = requests.get(loc_key_url)
        if r.status_code == 200:
            loc_key = r.json()['Key']
            return loc_key
        else:
            logging.info(f"Ошибка {r.status_code}, get_loc_key_by_coords")
            return r.status_code

    def get_loc_key_by_city(self, name):
        loc_key_url = f'http://dataservice.accuweather.com/locations/v1/search?apikey={self.api_key}&q={name}'
        r = requests.get(loc_key_url)
        if r.status_code == 200 and r.json():
            loc_key = r.json()[0]['Key']
            return loc_key
        else:
            logging.info(f"Ошибка {r.status_code}, get_loc_key_by_city")
            return (r.status_code, 'Ошибка при обратботке названия города')

    def get_weather_data(self, city_name):
        #Получение loc_key по названию города
        self.loc_key = self.get_loc_key_by_city(city_name)

        #Получение данных о погоде, по location key
        weather_url = f'http://dataservice.accuweather.com/currentconditions/v1/{self.loc_key}?apikey={self.api_key}&language=ru&details=true&metric=true'
        r = requests.get(weather_url)
        if r.status_code == 200:
            weather_data = r.json()
        else:
            logging.info(f"Ошибка {r.status_code}, get_weather_data")
            return r.status_code

        #Извлечение ключевых параметров
        temperature = weather_data[0]['Temperature']['Metric']['Value']
        humidity = weather_data[0]['RelativeHumidity']
        wind_speed = weather_data[0]['Wind']['Speed']['Metric']['Value']
        weather_text = weather_data[0]['WeatherText']
        if not weather_data[0]['HasPrecipitation']:
            daily_forecasts_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/1day/{self.loc_key}?apikey={self.api_key}&language=ru&details=true&metric=true'
            r = requests.get(daily_forecasts_url)
            if r.status_code == 200:
                forecasts = r.json()
                prob_day = forecasts['DailyForecasts'][0]['Day']['RainProbability']
                prob_night = forecasts['DailyForecasts'][0]['Night']['RainProbability']
                rain_prob = ((prob_day+prob_night) - (prob_night*prob_day)/100)
            else:
                logging.info(f'Ошибка:{r.status_code}, error in get rain_prob')
                return r.status_code
        else:
            rain_prob = 100
        #Классификаци погодных условий плохие/хорошие

        if temperature<5 or temperature>30 or wind_speed>35 or rain_prob>70 or (temperature<15 and wind_speed>40):
            weather_type = f'Погода плохая, {weather_text.lower()}'
        else:
            weather_type = f'Погода хорошая, {weather_text.lower()}'

        #сохранение параметров
        self.cached_data = {
            'temp': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            "rain_prob": rain_prob,
            "weather_type": weather_type}

        return self.cached_data

    def get_forecast_weather_data(self, city_name, days=1):
        # Получение loc_key по названию города
        self.loc_key = self.get_loc_key_by_city(city_name)
        print(self.loc_key)
        if isinstance(self.loc_key, tuple):
            return self.loc_key
        # Получение прогнозных данных о погоде по location key
        forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{self.loc_key}?apikey={self.api_key}&language=ru&details=true&metric=true'
        r = requests.get(forecast_url)
        print(forecast_url)
        if r.status_code == 200:
            forecast_data = r.json()
        else:
            logging.info(f"Ошибка {r.status_code}, get_forecast_weather_data")
            return r.status_code

        forecasts = []
        for day in forecast_data['DailyForecasts'][:days]:
            date = day['Date'][:10]
            temp_min = day['Temperature']['Minimum']['Value']
            temp_max = day['Temperature']['Maximum']['Value']
            precipitation_prob = day['Day']['RainProbability']
            wind_speed = day['Day']['Wind']['Speed']['Value']
            weather_text = day['Day']['LongPhrase']
            
            # Извлечение влажности
            humidity_day = day['Day'].get('RelativeHumidity', 0)['Average']
            humidity_night = day['Night'].get('RelativeHumidity', 0)['Average']
            humidity = (humidity_day + humidity_night) / 2

            forecasts.append({
                'date': date,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'precipitation_prob': precipitation_prob,
                'wind_speed': wind_speed,
                'humidity': humidity,
                'weather_text': weather_text
            })

        print(forecasts)
        return forecasts


