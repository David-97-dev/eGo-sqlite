import json
import os
import folium
import time
import pandas as pd
from folium.plugins import MarkerCluster
from folium.plugins import Search
import css_html_js_minify as minifier


class mapper:

    @staticmethod
    def draw_map(connection):

        # https://georgetsilva.github.io/posts/mapping-points-with-folium/
        # https://geoffboeing.com/2015/10/exporting-python-data-geojson/
        # https: // stackoverflow.com / questions / 60585689 / how - to - display - information - in -geojson - popup - python
        # https://stackoverflow.com/questions/50998176/6-millions-of-markers-in-folium-leaflet-map

        start_time = time.time()

        df = mapper.retrieve_points(connection)

        cols = df.columns
        raw_json = mapper.df_to_geojson(df, cols)

        locations = df[['latitude', 'longitude']]
        location_list = locations.values.tolist()
        print(df.head())

        with open('searchdata.json', 'w') as fp:
            json.dump(raw_json, fp)

        print("--- %s seconds ---" % (time.time() - start_time))

        print('Drawing Map...')

        start_time = time.time()

        m = folium.Map(location=[54.968220, -1.868530], zoom_start=7, prefer_canvas=True)  # lat/long

        with open('searchdata.json') as access_json:
            read_content = json.load(access_json)

        geojson_obj = folium.GeoJson('searchdata.json', popup=folium.GeoJsonPopup(fields=cols.tolist())).add_to(m)

        Search(layer=geojson_obj, search_zoom=12, search_label='name', collapsed=False).add_to(m)

        folium.LayerControl().add_to(m)
        folium.plugins.LocateControl().add_to(m)

        m.save('map.html')
        # mapper.minify()
        print("--- %s seconds ---" % (time.time() - start_time))

        print('\nOpen \'map.html\' in a browser to view generated map')

    @staticmethod
    def df_to_geojson(df, properties, lat='latitude', lon='longitude'):
        geojson = {'type': 'FeatureCollection', 'features': []}
        for _, row in df.iterrows():
            feature = {'type': 'Feature',
                       'properties': {},
                       'geometry': {'type': 'Point',
                                    'coordinates': []}}
            feature['geometry']['coordinates'] = [row[lon], row[lat]]
            for prop in properties:
                feature['properties'][prop] = row[prop]
            geojson['features'].append(feature)
        return geojson

    @staticmethod
    def retrieve_points(connection):
        print('Retrieving points...')

        data = connection.execute(
            'SELECT reference, name, latitude, longitude FROM registry WHERE name IS NOT NULL AND latitude <> \'\' LIMIT 100;').fetchall()

        df = pd.DataFrame(data, columns=['name', 'reference', 'latitude', 'longitude'])

        return df


    @staticmethod
    def minify():

        print('File size before minify: ')
        print(int(os.path.getsize('map.html')))
        print('Minifying...')
        minifier.process_single_html_file('map.html', overwrite=True)
        print('File size after minify: ')
        print(int(os.path.getsize('map.html')))
