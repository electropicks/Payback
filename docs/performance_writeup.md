# Performance 
## Fake Data Modeling
See [datafaker.py](../datafaker.py). 

### Fake Data distribution:
* 36000 rows users
* 9000 rows groups
* 36000 rows group_members
* 433065 rows line_item_members
* 144352 rows line_items
* 18000 rows shopping_trips
* 270000 rows transactions_ledger
* 90000 rows transactions

Total rows: 1036408



## Performance Results
`POST /api/auth/register` 89 ms

`POST /api/auth/login` 352 ms

`POST /api/groups` 71 ms

`POST /api/groups/{group_id}/join` 84 ms

`POST /api/groups/register` 72 ms

`POST /api/groups/{group_id}/search` 122 ms

`POST /api/groups/{group_id}/searchByTrip` 128 ms

`GET /api/groups/{group_id}/trips` 77 ms

`POST /api/groups/calculate` 103 ms

`GET /api/groups/{group_id}/transactions` 68 ms


`POST /api/transactions/add`  45 ms

`POST /api/transactions/delete{transaction_id}` 63 ms


`GET /api/trips/{trip_id}` 63 ms

`POST /api/trips/create` 34 ms

`POST /api/trips/items` 53 ms

`POST /api/trips/{trip_id}/addItems` 61 ms

`POST /api/api/trips/{trip_id}/update_item_price` 42 ms

The three slowest endpoints were   
`POST /api/auth/login`, 
`POST /api/groups/{group_id}/search` , 
`POST /api/groups/{group_id}/searchByTrip`

## Performance Tuning
### POST /api/auth/login

```
SELECT * FROM users
WHERE username = 'sualluri'
```
| QUERY PLAN                                                                                         |
| -------------------------------------------------------------------------------------------------- |
| Seq Scan on users  (cost=0.00..891.00 rows=1 width=63) (actual time=20.875..20.877 rows=1 loops=1) |
|   Filter: (username = 'sualluri'::text)                                                            |
|   Rows Removed by Filter: 36000                                                                    |
| Planning Time: 1.922 ms                                                                            |
| Execution Time: 21.115 ms                                                                          |


A sequential scan is being done and the cost is 891 which seems very high. 
To fix this we can add an index on username  

`CREATE INDEX username_idx ON users (username);`


| QUERY PLAN                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------- |
| Index Scan using username_idx on users  (cost=0.29..8.31 rows=1 width=63) (actual time=0.652..0.653 rows=1 loops=1) |
|   Index Cond: (username = 'sualluri'::text)                                                                         |
| Planning Time: 1.252 ms                                                                                             |
| Execution Time: 0.732 ms                                                                                            |

This had the performance improvement we expected. 21 ms to 0.7 ms is a great improvement.

