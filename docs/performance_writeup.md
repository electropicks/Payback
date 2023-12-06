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

We based this on the assumption that average group size would be 4 users, and each group had on average 2 shopping trips, with each trip having on average 10 items. Every member in the group is expected to pay at least 1 time per shopping trip.


## Performance Results
`POST /api/auth/register` 89 ms

`POST /api/auth/login` 352 ms

`POST /api/groups` 71 ms

`POST /api/groups/{group_id}/join` 84 ms

`POST /api/groups/register` 72 ms

`POST /api/groups/{group_id}/search` 122 ms

`POST /api/groups/{group_id}/searchByTrip` 121 ms

`GET /api/groups/{group_id}/trips` 77 ms

`POST /api/groups/calculate` 125 ms

`GET /api/groups/{group_id}/transactions` 68 ms


`POST /api/transactions/add`  45 ms

`POST /api/transactions/delete{transaction_id}` 63 ms


`GET /api/trips/{trip_id}` 63 ms

`POST /api/trips/create` 34 ms

`POST /api/trips/items` 53 ms

`POST /api/trips/{trip_id}/addItems` 61 ms

`POST /api/api/trips/{trip_id}/update_item_price` 42 ms

The three slowest endpoints were   
`POST /api/auth/login`, @ 352 ms
`POST /api/groups/calculate`  @ 125 ms
`POST /api/groups/{group_id}/search`, @ 122 ms

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

The explain tells us that a sequential scan is being done with a cost of 891, which seems very high. 
To fix this we can add an index on username.

`CREATE INDEX username_idx ON users (username);`


| QUERY PLAN                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------- |
| Index Scan using username_idx on users  (cost=0.29..8.31 rows=1 width=63) (actual time=0.652..0.653 rows=1 loops=1) |
|   Index Cond: (username = 'sualluri'::text)                                                                         |
| Planning Time: 1.252 ms                                                                                             |
| Execution Time: **0.732 ms**                                                                                            |

This had the performance improvement we expected as an index scan is being done instead of a sequential scan. 21.115 ms to 0.732 ms is a significant improvement.


## POST /api/groups/calculate
```
WITH paid_balance AS (
SELECT user_id,
    SUM(CASE WHEN from_id = 34892 AND to_id = user_id THEN change ELSE 0 END) AS amount_paid,
    SUM(CASE WHEN to_id = 34892 AND from_id = user_id THEN change ELSE 0 END) AS amount_owed
FROM transaction_ledger
JOIN transactions ON transaction_id = transactions.id
JOIN group_members ON transactions.group_id = group_members.group_id
WHERE (from_id = 34892 OR to_id = 34892) AND transactions.group_id = 3303
GROUP BY user_id
)
SELECT user_id, SUM(amount_owed - amount_paid) AS balance
FROM paid_balance
WHERE user_id != 34892
GROUP BY user_id
```

| QUERY PLAN                                                                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GroupAggregate  (cost=1000.59..6042.13 rows=4 width=40) (actual time=58.876..61.184 rows=0 loops=1)                                                                        |
|   Group Key: group_members.user_id                                                                                                                                         |
|   ->  GroupAggregate  (cost=1000.59..6042.01 rows=4 width=24) (actual time=58.875..61.182 rows=0 loops=1)                                                                  |
|         Group Key: group_members.user_id                                                                                                                                   |
|         ->  Nested Loop  (cost=1000.59..6041.90 rows=4 width=28) (actual time=58.873..61.180 rows=0 loops=1)                                                               |
|               ->  Index Only Scan using group_members_pkey on group_members  (cost=0.29..4.37 rows=4 width=16) (actual time=0.238..0.244 rows=4 loops=1)                   |
|                     Index Cond: (group_id = 3303)                                                                                                                          |
|                     Filter: (user_id <> 34892)                                                                                                                             |
|                     Heap Fetches: 0                                                                                                                                        |
|               ->  Materialize  (cost=1000.30..6037.48 rows=1 width=28) (actual time=14.657..15.233 rows=0 loops=4)                                                         |
|                     ->  Gather  (cost=1000.30..6037.48 rows=1 width=28) (actual time=58.615..60.921 rows=0 loops=1)                                                        |
|                           Workers Planned: 1                                                                                                                               |
|                           Workers Launched: 1                                                                                                                              |
|                           ->  Nested Loop  (cost=0.30..5037.38 rows=1 width=28) (actual time=55.469..55.471 rows=0 loops=2)                                                |
|                                 ->  Parallel Seq Scan on transaction_ledger  (cost=0.00..4906.35 rows=16 width=28) (actual time=8.612..55.293 rows=14 loops=2)             |
|                                       Filter: ((from_id = 34892) OR (to_id = 34892))                                                                                       |
|                                       Rows Removed by Filter: 134992                                                                                                       |
|                                 ->  Memoize  (cost=0.30..8.17 rows=1 width=16) (actual time=0.011..0.011 rows=0 loops=28)                                                  |
|                                       Cache Key: transaction_ledger.transaction_id                                                                                         |
|                                       Cache Mode: logical                                                                                                                  |
|                                       Hits: 4  Misses: 11  Evictions: 0  Overflows: 0  Memory Usage: 1kB                                                                   |
|                                       Worker 0:  Hits: 4  Misses: 9  Evictions: 0  Overflows: 0  Memory Usage: 1kB                                                         |
|                                       ->  Index Scan using transactions_pkey on transactions  (cost=0.29..8.16 rows=1 width=16) (actual time=0.012..0.012 rows=0 loops=20) |
|                                             Index Cond: (id = transaction_ledger.transaction_id)                                                                           |
|                                             Filter: (group_id = 3303)                                                                                                      |
|                                             Rows Removed by Filter: 1                                                                                                      |
| Planning Time: 1.396 ms                                                                                                                                                    |
| Execution Time: 61.533 ms                                                                                                                                                  |

The explain results tell us that several nested loops and sequential scans are being done along with several other processes that drastically reduce the speed of this query. To fix this, we can add indexes on the foreign keys, from_id and to_id, of the transaction ledger and the id and group_id of the transactions table.

```
CREATE INDEX idx_transaction_ledger_from_to_id ON transaction_ledger (from_id, to_id);
CREATE INDEX idx_transactions_id_group_id ON transactions (id, group_id);
```



| QUERY PLAN                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GroupAggregate  (cost=4686.77..4915.22 rows=4 width=40) (actual time=2.968..2.972 rows=0 loops=1)                                                                                    |
|   Group Key: group_members.user_id                                                                                                                                                   |
|   ->  GroupAggregate  (cost=4686.77..4915.10 rows=4 width=24) (actual time=2.967..2.970 rows=0 loops=1)                                                                              |
|         Group Key: group_members.user_id                                                                                                                                             |
|         ->  Nested Loop  (cost=4686.77..4914.99 rows=4 width=28) (actual time=2.965..2.969 rows=0 loops=1)                                                                           |
|               ->  Index Only Scan using group_members_pkey on group_members  (cost=0.29..8.37 rows=4 width=16) (actual time=0.076..0.079 rows=4 loops=1)                             |
|                     Index Cond: (group_id = 3303)                                                                                                                                    |
|                     Filter: (user_id <> 34892)                                                                                                                                       |
|                     Heap Fetches: 0                                                                                                                                                  |
|               ->  Materialize  (cost=4686.48..4906.57 rows=1 width=28) (actual time=0.721..0.722 rows=0 loops=4)                                                                     |
|                     ->  Nested Loop  (cost=4686.48..4906.56 rows=1 width=28) (actual time=2.877..2.880 rows=0 loops=1)                                                               |
|                           ->  Bitmap Heap Scan on transaction_ledger  (cost=4686.05..4786.08 rows=27 width=28) (actual time=2.758..2.806 rows=28 loops=1)                            |
|                                 Recheck Cond: ((from_id = 34892) OR (to_id = 34892))                                                                                                 |
|                                 Heap Blocks: exact=5                                                                                                                                 |
|                                 ->  BitmapOr  (cost=4686.05..4686.05 rows=27 width=0) (actual time=2.730..2.733 rows=0 loops=1)                                                      |
|                                       ->  Bitmap Index Scan on idx_transaction_ledger_from_to_id  (cost=0.00..4.53 rows=14 width=0) (actual time=0.024..0.025 rows=12 loops=1)       |
|                                             Index Cond: (from_id = 34892)                                                                                                            |
|                                       ->  Bitmap Index Scan on idx_transaction_ledger_from_to_id  (cost=0.00..4681.51 rows=13 width=0) (actual time=2.705..2.705 rows=16 loops=1)    |
|                                             Index Cond: (to_id = 34892)                                                                                                              |
|                           ->  Memoize  (cost=0.43..4.45 rows=1 width=16) (actual time=0.002..0.002 rows=0 loops=28)                                                                  |
|                                 Cache Key: transaction_ledger.transaction_id                                                                                                         |
|                                 Cache Mode: logical                                                                                                                                  |
|                                 Hits: 8  Misses: 20  Evictions: 0  Overflows: 0  Memory Usage: 2kB                                                                                   |
|                                 ->  Index Only Scan using idx_transactions_id_group_id on transactions  (cost=0.42..4.44 rows=1 width=16) (actual time=0.003..0.003 rows=0 loops=20) |
|                                       Index Cond: ((id = transaction_ledger.transaction_id) AND (group_id = 3303))                                                                   |
|                                       Heap Fetches: 0                                                                                                                                |
| Planning Time: 1.047 ms                                                                                                                                                              |
| Execution Time: **3.232 ms**                                                                                                                                                             |  

Adding these indexes reduced execution time from 61.533 ms to 3.232 ms, which is a substantial enough improvement to warrant keeping them. With the indexes, it doesn't have to spawn any workers like it did before.

## POST /api/groups/{group_id}/search
```
SELECT line_items.id, line_items.quantity, line_items.price, line_items.item_name, shopping_trips.id AS trip_id, shopping_trips.description AS trip_description
FROM line_items
JOIN shopping_trips ON line_items.trip_id = shopping_trips.id
WHERE shopping_trips.group_id = 2 AND line_items.item_name ILIKE 'low'
```

| QUERY PLAN                                                                                                                            |
| ------------------------------------------------------------------------------------------------------------------------------------- |
| Nested Loop  (cost=0.29..3009.86 rows=1 width=67) (actual time=75.591..75.592 rows=0 loops=1)                                         |
|   ->  Seq Scan on line_items  (cost=0.00..2892.40 rows=14 width=30) (actual time=0.076..73.586 rows=149 loops=1)                      |
|         Filter: (item_name ~~* 'three'::text)                                                                                         |
|         Rows Removed by Filter: 144225                                                                                                |
|   ->  Index Scan using expenses_pkey on shopping_trips  (cost=0.29..8.02 rows=1 width=45) (actual time=0.013..0.013 rows=0 loops=149) |
|         Index Cond: (id = line_items.trip_id)                                                                                         |
|         Filter: (group_id = 11)                                                                                                       |
|         Rows Removed by Filter: 1                                                                                                     |
| Planning Time: 1.925 ms                                                                                                               |
| Execution Time: 75.749 ms                                                                                                             |  

The explain results tell us that a nested loop and sequential scan is being used to filter the results. By adding indexes on trip_id and group_id foreign keys, we can make it much easier to find what items are associated with the group.


```
CREATE INDEX idx_line_items_trip_id ON line_items (trip_id);
CREATE INDEX idx_shopping_trips_group_id ON shopping_trips (group_id);
```



| QUERY PLAN                                                                                                                                        |
| ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Nested Loop  (cost=0.58..25.25 rows=1 width=67) (actual time=0.068..0.069 rows=0 loops=1)                                                         |
|   ->  Index Scan using idx_shopping_trips_group_id on shopping_trips  (cost=0.29..8.32 rows=2 width=45) (actual time=0.041..0.042 rows=2 loops=1) |
|         Index Cond: (group_id = 11)                                                                                                               |
|   ->  Index Scan using idx_line_items_trip_id on line_items  (cost=0.29..8.45 rows=1 width=30) (actual time=0.010..0.010 rows=0 loops=2)          |
|         Index Cond: (trip_id = shopping_trips.id)                                                                                                 |
|         Filter: (item_name ~~* 'three'::text)                                                                                                     |
|         Rows Removed by Filter: 7                                                                                                                 |
| Planning Time: 1.007 ms                                                                                                                           |
| Execution Time: **0.172 ms**                                                                                                                          |

Adding these two indices had a drastic performance improvement, bringing the actual execution time from 75.749ms to 0.172ms. Instead of having to use nested loop and sequential scan, it is able to just use an index scan.







