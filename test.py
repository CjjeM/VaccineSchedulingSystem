from geopy.geocoders import Nominatim
import openrouteservice as ors
import folium

nom = Nominatim(user_agent="vac_system")

ors_key = "5b3ce3597851110001cf6248c0c4c140d07742c4ac6cab0737c5984d"

address1 = "Calamba Doctors Hospital"
address2 = "mabuhay, mamatid, cabuyao, laguna"

n1 = nom.geocode(address1)
n2 = nom.geocode(address2)

client = ors.Client(key=ors_key)

start_coords = (14.217223350000001, 121.14196109281863)
folium_map = folium.Map(
    location=start_coords,
    zoom_start=17
)

folium.Marker(
    [n1.latitude, n1.longitude]
).add_to(folium_map)

folium.Marker(
    [n2.latitude, n2.longitude]
).add_to(folium_map)

directions = [[n1.longitude, n1.latitude], [n2.longitude, n2.latitude]]

print(directions)

route = client.directions(coordinates=directions,
                          profile='driving-car',
                          format='geojson'
                        )

folium.GeoJson(route, name="Route").add_to(folium_map)

folium_map.save('static/map1.html')
