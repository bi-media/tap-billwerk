# tap-billwerk

## UPDATE
### DONE
- fixed the nested schema structures
- deleted Subscriptions endpoint
- imlpemented pagination (!!! problem with ContractChanges endpoint)
- implemented incremental load (still needs some testing)

### TO DOs:
- Incremental load tests (orders and invoices)
- Talk to Billwerk about ContractChanges
- State.json file generation not working correctly
- Code comments and documentation


## PREPARE FILES
### config.json:
'''
{
  "client_id" : "",
  "client_secret" : "",
  "start_date" : "",
  "token" : ""
}
'''
start_date format:  2020-01-22T16:22:45.0000000Z
* token is not required field

### state.json
'''
{
  "bookmarks": {
    "orders": {
      "last_record": "2020-10-09T14:52:54.0000000Z"
    },
    "invoices": {
      "last_record" : "2020-01-22T16:22:45.0000000Z"
    }
  }
}
'''
### catalog.json
You can generate the catalog.json yourself with the command
  >> tap-billwerk --config config.json --discover > catalog.json
and add lines in the generated file to select which streams to select (see below)
OR
you can use the catalog file from the repository (catalog.json) - it has all the streams selected already. 

Selecting streams in the catalog.json:
'''
...
"stream": "orders",
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
		        "selected" : true,  <----------------- add this line for each stream
            "table-key-properties": [
              "Id"
            ],
            "forced-replication-method": "INCREMENTAL",
            "valid-replication-keys": [
              "CreatedAt"
            ],
            "inclusion": "available"
          }
        }
        ...
'''
## PREPARE THE PACKAGE
1. Download the repository
2. Create a virtual environment and activate
3. Install required packages
  > pip install -r requirements.txt
4. Install the tap-billwerk package
  > python setup.py build
  > python setup.py install
5. Execute the package (see next section) 
* if you want to call Billwerk and not the Billwerk Sandbox: comment out lines 9 and 10 in client.py and uncomment lines 13 and 14

## EXECUTE THE PACKAGE
If you include the state.json, orders and invoices endpoints will be synchronized since the timestamps provided in the state file:
  > tap-billwerk --config config.json --catalog catalog.json --state state.json | target-xxx --config config_xxx.json >> state.json
! The last part (>> state.json) should write an updated state file after the run but is not working correctly yet.

If you don't include the state file, all endpoints will be synchronized since the timestamp in the config.json ('start_date')
  > tap-billwerk --config config.json --catalog catalog.json | target-xxx --config config_xxx.json 
