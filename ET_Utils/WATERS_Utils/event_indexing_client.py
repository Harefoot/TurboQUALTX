"""Wrapper with convenience functions for EPA WATERS Event Indexing Service."""

import json
try:
    from urllib2 import urlopen  # Python 2
except:
    from urllib.request import urlopen  # Python 3

_base_url = 'http://ofmpub.epa.gov/waters10/EventIndexing.Service?'


def trace_downstream(start_latitude, start_longitude, max_length_km):
    """Performs Downstream Mainline Indexing."""

    # Query EPA    
    pBatchResolution = '3'  # 3 = medium-res (NHDPlus), 2 = hi-res
    pInputGeometry = 'POINT({0}%20{1})'.format(start_longitude, start_latitude)
    url = (_base_url + 'pBatchResolution=' + pBatchResolution +
           '&pIndexingType=downstream_main' + '&optOut2D=TRUE' +
           '&pFlowDistance=' + str(max_length_km) +
           '&pInputGeometry=' + pInputGeometry)
    response = urlopen(url)
    data = response.read()
    json_response = json.loads(data)

    # todo: handle errors or no results found

    # Build GeoJSON from the response
    features = []
    for line in json_response['output']['line_events']:
        feature = {'type': 'Feature',
                   'geometry': line['shape'],
                   'properties': {
                       'reachcode': line['reachcode'],
                       'fmeasure': line['fmeasure'],
                       'tmeasure': line['tmeasure']}}
        features.append(feature)
  
    geojson = {'type': 'FeatureCollection',
               'features': features}
    return geojson


if __name__ == '__main__':
    from pprint import pprint
    lon, lat = (-97.782752, 30.397861)  # Bull Creek in zip 78759
    length_km = 5
    result = trace_downstream(lat, lon, length_km)
    print('Line event count: {}'.format(len(result['features'])))
    with open('bull_creek.json', 'wb') as f:
        f.write(json.dumps(result))
