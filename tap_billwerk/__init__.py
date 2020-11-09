import singer
from singer import utils
from singer.catalog import Catalog, write_catalog
from tap_billwerk.discover import do_discover
from tap_billwerk.sync import do_sync
from tap_billwerk.client import BillwerkClient

LOGGER = singer.get_logger()

@utils.handle_top_exception(LOGGER)
def main():
    # define required config file keys
    required_config_keys = ['client_id', 'client_secret', 'start_date']
    # check if required keys are in the config file
    args = singer.parse_args(required_config_keys)

    # get the input
    config = args.config
    catalog = args.catalog or Catalog([])
    state = args.state
    # instatiate the client
    client = BillwerkClient(config)

    if args.properties and not args.catalog:
        raise Exception(
            "DEPRECATED: Use of the 'properties' parameter is not supported. Please use --catalog instead"
        )

    if args.discover:
        LOGGER.info("Starting discovery mode")
        catalog = do_discover()
        write_catalog(catalog)
    else:
        LOGGER.info('Starting sync mode')
        do_sync(client, config, state, catalog)


if __name__ == '__main__':
    main()
