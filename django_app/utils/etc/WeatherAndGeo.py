import requests


class Weather:
    def __init__(self, secret_key_weather, secret_key_google_geo, ):
        self.secret_key_weather = secret_key_weather
        self.secret_key_google_geo = secret_key_google_geo
        self.weather = dict()

    def get_geometry(self, *location):
        """
        좌표 to 지명
        :return:
        """
        url = "https://maps.googleapis.com/maps/api/geocode/json" \
              "?latlng={LATITUDE},{LONGITUDE}" \
              "&key={SECRET_KEY}" \
              "&language=ko" \
              "&result_type={result_type}".format(LATITUDE=location[0],
                                                  LONGITUDE=location[1],
                                                  SECRET_KEY=self.secret_key_google_geo,
                                                  result_type="sublocality", )
        address = requests.get(url).json()["results"][2]["formatted_address"]
        return address

    def get_weather_info(self, *location):
        url = "https://api.darksky.net/forecast/" \
              "{SECRET_KEY}/" \
              "{LATITUDE},{LONGITUDE}".format(
            SECRET_KEY=self.secret_key_weather,
            LATITUDE=location[0],
            LONGITUDE=location[1], )
        data = requests.get(url).json()
        addr = self.get_geometry(*location)

        if not addr in self.weather or \
                        (data["currently"]["time"].hour - self.weather[addr]["time"].hour) != 0:
            self.weather[addr] = {
                "time": data["hourly"]["data"][0]["time"],  # timeRange
                "icon": data["currently"]["icon"],  # weather
                "location_name": addr,
            }
