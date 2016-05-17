"""Wrapper with convenience functions for EPA WATERS Point Indexing Service."""

import json
try:
    from urllib2 import urlopen  # Python 2
except:
    from urllib.request import urlopen  # Python 3

_base_url = 'http://ofmpub.epa.gov/waters10/PointIndexing.Service?'


def trace_to_stream(start_latitude, start_longitude):
    """Use flow direction grid to find nearest stream to input point."""

    pResolution = '3'  # 3 = medium-res (NHDPlus), 2 = hi-res
    pInputGeometry = 'POINT({0}%20{1})'.format(start_longitude, start_latitude)
    url = (_base_url + 'pResolution=' + pResolution +
           '&pPointIndexingMethod=RAINDROP' + '&pOutputPathFlag=TRUE' +
           '&pGeometry=' + pInputGeometry)
    response = urlopen(url)
    data = response.read()
    json_response = json.loads(data)

    # todo: handle errors or no results found

    # Build GeoJSON from the response
    features = []
    index_path = {'type': 'Feature',
                  'geometry': json_response['output']['indexing_path'],
                  'properties': {
                      'name': 'indexing_path',
                      'length_km': json_response['output']['path_distance']}}
    features.append(index_path)
    end_point = {'type': 'Feature',
                  'geometry': json_response['output']['end_point'],
                  'properties': {'name': 'end_point'}}
    features.append(end_point)
    geojson = {'type': 'FeatureCollection',
               'features': features}
    return geojson


if __name__ == '__main__':
    lat, lon = (30.400267, -97.780908)
    result = trace_to_stream(lat, lon)
    with open('trace_to_stream.json', 'wb') as f:
        f.write(json.dumps(result))
