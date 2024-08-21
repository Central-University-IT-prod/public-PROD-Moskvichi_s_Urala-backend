import json
import requests


def get_city_by_coordinates(lat, lon):
    result = requests.get(
        f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&namedetails=1")
    data = dict(json.loads(result.text))
    if not data.get("address"):
        return -1, -1
    address: dict = data.get('address')
    if not address.get('ISO3166-2-lvl4'):
        return -1, -1
    city_id = address['ISO3166-2-lvl4']
    if not data.get('display_name'):
        return -1, -1
    print(city_id, data["display_name"])
    return city_id, data["display_name"]
