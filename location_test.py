import geopy

Latitude = str(-22.9519)
Longitude = str(-43.2105)
Coordinate = Latitude + ", " + Longitude
location = geopy.geocoders.Nominatim(user_agent="Cookiebot").reverse(Coordinate)
address = ""
vector = location.address.split(",")
i = 0
while i < len(vector)-7:
    address += vector[i]
    address += ","
    i += 1
address = address[:-1]

print(address)
