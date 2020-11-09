from datetime import timedelta
import singer
from singer import utils

LOGGER = singer.get_logger()


class DateWindowing:


    stream_id = None
    stream_name = None
    endpoint = None
    key_properties = None
    replication_keys = []
    replication_method = None
    _last_bookmark_value = None
    config = None
    state = None
    client = None
    MAX_API_RESPONSE_SIZE = 500
    params = {}

    # get date window according from config.json and/or state.json
    def _get_window_state(self):
        window_start = singer.get_bookmark(self.state, self.stream_id, 'last_record')
        sub_window_end = singer.get_bookmark(self.state, self.stream_id, 'sub_window_end')
        window_end = singer.get_bookmark(self.state, self.stream_id, 'window_end')

        # adjusting window to lookback 1 day
        adjusted_window_start = utils.strftime(utils.strptime_to_utc(window_start)
                                               -timedelta(days=1))

        start_date = self.config.get('start_date')
        end_date = utils.strftime(utils.now())

        window_start = utils.strptime_to_utc(max(adjusted_window_start, start_date))
        sub_window_end = sub_window_end and  utils.strptime_to_utc(min(sub_window_end, end_date))
        window_end = utils.strptime_to_utc(min(window_end, end_date))

        return window_start, sub_window_end, window_end

    # fill missing bookmarks with now()
    def on_window_started(self):
        if singer.get_bookmark(self.state, self.stream_id, 'sub_window_end') is None:
            if singer.get_bookmark(self.state, self.stream_id, 'last_record') is None:
                singer.write_bookmark(self.state, self.stream_id, 'last_record',
                                      self.config.get('start_date'))
            if singer.get_bookmark(self.state, self.stream_id, 'window_end') is None:
                now = utils.strftime(utils.now())
                singer.write_bookmark(self.state, self.stream_id, 'window_end',
                                      min(self.config.get('end_date', now), now))
        singer.write_state(self.state)

    # update bookmark for end state.json
    def on_window_finished(self):
        window_start = singer.get_bookmark(self.state, self.stream_id, 'window_end')
        singer.write_bookmark(self.state, self.stream_id, 'last_record', window_start)
        singer.clear_bookmark(self.state, self.stream_id, 'window_end')
        singer.write_state(self.state)

    # get the gecords by calling _paginate_windows()
    def get_records(self, format_values):
        window_start, sub_window_end, window_end = self._get_window_state()
        window_start -= timedelta(milliseconds=1)

        if sub_window_end is not None:
            for rec in self._paginate_window(window_start, sub_window_end, format_values):
                yield rec
        else:
            for rec in self._paginate_window(window_start, window_end, format_values):
                yield rec

    def _update_bookmark(self, key, value):
        singer.bookmarks.write_bookmark(
            self.state, self.stream_id, key, utils.strftime(value)
        )

    def _paginate_window(self, window_start, window_end, format_values):
        sub_window_end = window_end
        while True:
            records = self.client.get(self._format_endpoint(format_values),
                                      params={'take': self.MAX_API_RESPONSE_SIZE,
                                              'dateFrom': utils.strftime(window_start),
                                              'dateTo': utils.strftime(sub_window_end),
                                              **self.params})

            for rec in records:
                yield rec

            if len(records) == self.MAX_API_RESPONSE_SIZE:
                LOGGER.info('%s - Paginating within date_window %s to %s, due to max records being received.',
                            self.stream_id,
                            utils.strftime(window_start), utils.strftime(sub_window_end))

                sub_window_end = utils.strptime_to_utc(records[-1].get('CreatedAt',
                                                                       records[-1].get('Created'))) \
                                                                       + timedelta(milliseconds=1)
                self._update_bookmark('sub_window_end', sub_window_end)
                singer.write_state(self.state)
            else:
                LOGGER.info('%s - Finished syncing between %s and %s',
                            self.stream_id,
                            utils.strftime(window_start),
                            window_end)
                singer.bookmarks.clear_bookmark(self.state, self.stream_id,
                                                'sub_window_end')
                break

class Stream:
    stream_id = None
    stream_name = None
    endpoint = None
    key_properties = None
    replication_keys = []
    replication_method = None
    _last_bookmark_value = None
    MAX_API_RESPONSE_SIZE = 500
    params = {}

    def __init__(self, client, config, state):
        self.client = client
        self.config = config
        self.state = state


    def get_format_values(self): # pylint: disable=no-self-use
        return []

    def _format_endpoint(self, format_values):
        return self.endpoint.format(*format_values)

    def modify_record(self, record, **kwargs): # pylint: disable=no-self-use,unused-argument
        return record

    def build_custom_fields_maps(self, **kwargs): # pylint: disable=no-self-use,unused-argument
        return {}, {}

    def get_records(self, format_values, additional_params=None):
        if additional_params is None:
            additional_params = {}

        custom_fields_map, dropdown_options_map = self.build_custom_fields_maps(parent_id_list=format_values)

        records = self.client.get(
            self._format_endpoint(format_values),
            params={
                'take': self.MAX_API_RESPONSE_SIZE,
                **self.params,
                **additional_params
            })
        json_data = records

        while len(json_data) == self.MAX_API_RESPONSE_SIZE:
            last_entry = json_data[-1]['Id']
            records.remove(records[-1])
            json_data = self.client.get(self._format_endpoint(format_values),
                                        params={'take': self.MAX_API_RESPONSE_SIZE,
                                                'from': last_entry,
                                                **self.params,
                                                **additional_params})
            records = records + json_data

        for rec in records:
            yield self.modify_record(rec, parent_id_list=format_values,
                                     custom_fields_map=custom_fields_map,
                                     dropdown_options_map=dropdown_options_map)

    def sync(self):
        if self.replication_method == 'INCREMENTAL':
            self.on_window_started()
            for rec in self.get_records(self.get_format_values()):
                yield rec
            self.on_window_finished()
        else:
            for rec in self.get_records(self.get_format_values()):
                yield rec


class Contracts(Stream):
    stream_id = 'contracts'
    stream_name = 'contracts'
    endpoint = 'contracts'
    key_properties = ['Id']
    replication_method = 'FULL_TABLE'

class ContractChanges(Stream):
    stream_id = 'contract_changes'
    stream_name = 'contract_changes'
    endpoint = 'contractChanges'
    key_properties = ['Timestamp']
    replication_method = 'FULL_TABLE'

class Customers(Stream):
    stream_id = 'customers'
    stream_name = 'customers'
    endpoint = 'customers'
    key_properties = ['Id']
    replication_method = 'FULL_TABLE'

class Invoices(DateWindowing, Stream):
    stream_id = 'invoices'
    stream_name = 'invoices'
    endpoint = 'invoices'
    key_properties = ['Id']
    replication_method = 'INCREMENTAL'
    replication_keys = ['CreatedAt']

class Orders(DateWindowing, Stream):
    stream_id = 'orders'
    stream_name = 'orders'
    endpoint = 'orders'
    key_properties = ['Id']
    replication_method = 'INCREMENTAL'
    replication_keys = ['CreatedAt']

class PlanGroups(Stream):
    stream_id = 'plan_groups'
    stream_name = 'plan_groups'
    endpoint = 'planGroups'
    key_properties = ['Id']
    replication_method = 'FULL_TABLE'

class Plans(Stream):
    stream_id = 'plans'
    stream_name = 'plans'
    endpoint = 'plans'
    key_properties = ['Id']
    replication_method = 'FULL_TABLE'

class PlanVariants(Stream):
    stream_id = 'plan_variants'
    stream_name = 'plan_variants'
    endpoint = 'planVariants'
    key_properties = ['Id']
    replication_method = 'FULL_TABLE'

class TaxPolicies(Stream):
    stream_id = 'tax_policies'
    stream_name = 'tax_policies'
    endpoint = 'taxPolicies'
    key_properties = ['Id']
    replication_method = 'FULL_TABLE'

class Subscriptions(DateWindowing, Stream):
    stream_id = 'subscriptions'
    stream_name = 'subscriptions'
    endpoint = 'subscriptions'
    key_properties = ['Id']
    replication_method = 'INCREMENTAL'
    replication_keys = ['LastPhaseChange']

class PaymentTransactions(DateWindowing, Stream):
    stream_id = 'payment_transactions'
    stream_name = 'payment_transactions'
    endpoint = 'PaymentTransactions'
    key_properties = ['Id']
    replication_method = 'INCREMENTAL'
    replication_keys = ['StatusTimestamp']

class PaymentRefunds(DateWindowing, Stream):
    stream_id = 'payments_refunds'
    stream_name = 'payments_refunds'
    endpoint = 'PaymentRefunds'
    key_properties = ['Id']
    replication_method = 'INCREMENTAL'
    replication_keys = ['TimeStamp']

STREAM_OBJECTS = {
    'contracts' : Contracts,
    'contract_changes' : ContractChanges,
    'customers' : Customers,
    'invoices': Invoices,
    'orders': Orders,
    'plan_groups' : PlanGroups,
    'plans' : Plans,
    'plan_variants' : PlanVariants,
    'subscriptions' : Subscriptions,
    'payment_transactions': PaymentTransactions,
    'payment_refunds': PaymentRefunds,
    }
