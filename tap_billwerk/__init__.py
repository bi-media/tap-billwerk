import singer
from singer import utils
from singer.catalog import Catalog, write_catalog
from tap_billwerk.discover import do_discover
from tap_billwerk.sync import do_sync
import tap_billwerk.streams as streams
from tap_billwerk.client import BillwerkClient

LOGGER = singer.get_logger()

@utils.handle_top_exception(LOGGER)
def main():
    required_config_keys = ['client_id', 'client_secret', 'start_date']
    args = singer.parse_args(required_config_keys)
    

    config = args.config  # pylint:disable=unused-variable
    client = BillwerkClient(config)  # pylint:disable=unused-variable
    catalog = args.catalog or Catalog([])
    state = args.state # pylint:disable=unused-variable

    if args.properties and not args.catalog:
        raise Exception("DEPRECATED: Use of the 'properties' parameter is not supported. Please use --catalog instead")

    if args.discover: 
        LOGGER.info("Starting discovery mode")
        catalog = do_discover()
        write_catalog(catalog)
    else:
        LOGGER.info("Starting sync mode")
        do_sync(client, config, state, catalog)
        

if __name__ == "__main__":
    main()