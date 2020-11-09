import os
import json
from singer import metadata
from singer.catalog import Catalog
from tap_billwerk.streams import STREAM_OBJECTS


def _get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)

def _load_schemas():
    schemas = {}

    for filename in os.listdir(_get_abs_path('schemas')):
        path = _get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas


def do_discover():
    raw_schemas = _load_schemas()
    catalog_entries = []

    for stream_name, schema in raw_schemas.items():
        stream = STREAM_OBJECTS[stream_name]
        mdata = metadata.get_standard_metadata(
            schema=schema,
            key_properties=stream.key_properties,
            replication_method=stream.replication_method )
        mdata = metadata.to_map(mdata)

        if stream.replication_key:
            mdata = metadata.write(mdata, (), 'valid-replication-keys', [stream.replication_key])

        for field_name in schema['properties'].keys():
            if field_name in stream.key_properties or field_name == stream.replication_key:
                mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'automatic')
            else:
                mdata = metadata.write(mdata, ('properties', field_name), 'inclusion', 'available')

        catalog_entry = {
            'stream': stream_name,
            'tap_stream_id': stream_name,
            'schema': schema,
            'metadata': metadata.to_list(mdata),
            'key_properties': stream.key_properties}
        catalog_entries.append(catalog_entry)

    return Catalog.from_dict({'streams': catalog_entries})
