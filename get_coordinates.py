from geopy.geocoders import Nominatim
from shapely.geometry import Point


def get_coordinate(city: str, state="NA", country="NA") -> Point:
    if isinstance(state, float):
        state = ""

    if isinstance(country, float):
        country = ""

    geolocator = Nominatim(user_agent="MeetingPoint")


    location = geolocator.geocode(" ".join([city, state, country]))
    return Point([location.latitude, location.longitude])


def get_address(lat: float, lon: float) -> list[str]:
    geolocator = Nominatim(user_agent="MeetingPoint")

    location = geolocator.reverse(",".join([str(lat), str(lon)]))

    if location is None:
        return ["Middle", "of", "nowhere"]

    address = location.raw["address"]

    city_state_country = []
    try:
        city_state_country.append(address["city"])
    except KeyError:
        city_state_country.append(address["county"])

    city_state_country += [address["state"], address["country"]]

    return city_state_country
