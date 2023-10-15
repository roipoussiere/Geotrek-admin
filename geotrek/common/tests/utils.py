from typing import List, Dict

import fiona


def update_gis(input_file_path: str, output_file_path: str, new_properties: Dict):
    '''
    Utility function that reads a GIS file (GeoPackage or Shapefile), update some properties,
    then write a new shapefile (typically in /tmp). Useful to test specific property values.
    '''

    with fiona.open(input_file_path) as source:
        with fiona.open(output_file_path,
                        mode='w',
                        crs=source.crs,
                        driver=source.driver,
                        schema=source.schema) as dest:
            for feat in source:
                dest.write(fiona.Feature(
                    geometry=feat.geometry,
                    properties={**feat.properties, **new_properties}
                ))


def gis_to_str(input_file_path: str) -> str:
    'Utility fonction that reads a GIS file and return its metadata and content as a string.'

    def dict_to_str(dic: Dict):
        return ''.join([f'\n      {k}: {v}' for k, v in dic.items()])

    with fiona.open(input_file_path) as source:
        gis_str = f'=== {input_file_path} ===\n'
        gis_str += f'  crs: {source.crs}\n'
        gis_str += f'  driver: {source.driver}\n'

        gis_str += '\n  schema:\n'
        for key, val in source.schema.items():
            gis_str += f'    {key}: {dict_to_str(val) if isinstance(val, dict) else str(val)}\n'

        gis_str += '\n  records:\n\n'
        for record in source:
            gis_str += f'    geometry:{dict_to_str(record.geometry)}\n'
            gis_str += f'    properties:{dict_to_str(record.properties)}\n\n'

    return gis_str[:-2]


def merge_dict(dict_a: dict, dict_b: dict):
    'Recursively merge dict_a into dict_b - based on https://stackoverflow.com/a/7205107'
    for key_b in dict_b:
        if key_b not in dict_a:
            dict_a[key_b] = dict_b[key_b]
        elif isinstance(dict_a[key_b], dict) and isinstance(dict_b[key_b], dict):
            merge_dict(dict_a[key_b], dict_b[key_b])
    return dict_a


class GISBuilder:
    'Utility class used to build various GID files from scratch.'

    def __init__(self, driver: str, epsg: int, schema: Dict, default_record: Dict):
        self.driver = driver
        self.crs = fiona.crs.CRS.from_epsg(epsg)
        self.schema = schema
        self.default_record = default_record

    def write(self, output_file_path: str, records: List[Dict]):
        'Write records on the GIS file and save it to provided path.'
        with fiona.open(output_file_path,
                        mode='w',
                        crs=self.crs,
                        driver=self.driver,
                        schema=self.schema) as dest:
            for record in records:
                dest.write(merge_dict(record, self.default_record))


# if __name__ == '__main__':
#     print(gis_to_str('geotrek/signage/tests/data/signage.shp'))
#     print(gis_to_str('geotrek/diving/tests/data/dive.shp'))
#     print(gis_to_str('geotrek/infrastructure/tests/data/infrastructure.shp'))
#     print(gis_to_str('geotrek/trekking/tests/data/poi.shp'))
#     print(gis_to_str('geotrek/trekking/tests/data/trek.shp'))
#     print(gis_to_str('geotrek/zoning/tests/data/city.shp'))
