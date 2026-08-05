Let me unpack this by showing what "stored as columns" actually means physically, then why it flips the performance trade-off.

## The setup: same table, two ways to store it

Say you have this table:

| id | name | country | age |
|---|---|---|---|
| 1 | Ana | US | 30 |
| 2 | Ben | UK | 25 |
| 3 | Cara | US | 40 |

A database has to lay this out as a **1-dimensional stream of bytes on disk**. There are two choices.

### Row-oriented (Postgres, MySQL) — store one full row, then the next

```
[1, Ana, US, 30] [2, Ben, UK, 25] [3, Cara, US, 40]
```

All the values of a **row** sit next to each other.

### Column-oriented (ClickHouse) — store one full column, then the next

```
ids:       [1, 2, 3]
names:     [Ana, Ben, Cara]
countries: [US, UK, US]
ages:      [30, 25, 40]
```

All the values of a **column** sit next to each other. This is exactly what your passage means by *"the values of each column are stored sequentially one after the other."*

## Why column operations (filter / aggregate) become much faster

Take the query:

```sql
SELECT AVG(age) FROM users;
```

**Row store:** ages are scattered — one every 4 values. To sum them, the DB must read `[1, Ana, US, 30]`, skip past id/name/country to grab `30`, then jump to the next row and do it again. It ends up **reading the entire table** (including names and countries it doesn't care about) just to pull out the age column.

**Column store:** the ages are already sitting together as `[30, 25, 40]`. The DB reads **only that one contiguous block** and ignores `id`, `name`, `country` entirely. On a table with 50 columns and a billion rows, that's the difference between reading 2% of the data and reading 100% of it.

Same idea for a filter like `WHERE country = 'US'` — it scans just the compact `countries` block.

## The bonus: compression (why the gap is often even bigger)

This is implied but worth adding. A column holds values of **the same type that are often similar** — the `countries` column is `[US, UK, US, US, US, ...]`, lots of repetition. Similar data compresses extremely well (often 10x+). So the column store not only reads *fewer* columns, it reads a *smaller, compressed* version of them. Less bytes off disk = faster still.

## The cost: restoring a single row becomes harder

This is your passage's *"harder to restore single rows... gaps between the row values."*

Take:

```sql
SELECT * FROM users WHERE id = 2;   -- give me Ben's whole row
```

In a **row store**, Ben's entire record `[2, Ben, UK, 25]` is one contiguous chunk — grab it in one read. Easy.

In a **column store**, Ben's data is **scattered across four separate places** on disk:
- his `id` is at position 2 in the `ids` block
- his `name` is at position 2 in the `names` block
- his `country` is at position 2 in the `countries` block
- his `age` is at position 2 in the `ages` block

To rebuild one row, the DB must visit **four different locations** and stitch position-2 from each back together. Those are the "gaps" — the pieces of a single row are spread out instead of together.

## The trade-off in one picture

| Operation | Row store | Column store |
|---|---|---|
| Read/write **one whole row** (`SELECT *`, insert one record) | ✅ Fast — it's contiguous | ❌ Slow — scattered, must reassemble |
| Aggregate/filter **one column over many rows** (`AVG`, `SUM`, `GROUP BY`) | ❌ Slow — reads everything | ✅ Fast — reads only that column, compressed |

## Why this makes ClickHouse an *analytics* database

The choice of layout **is** the choice of workload:

- **Transactional apps (OLTP)** constantly touch whole individual records — "load this user," "update this order." → **row store** (Postgres).
- **Analytical apps (OLAP)** run big aggregations over a few columns across millions of rows — "average revenue by country last quarter." → **column store** (ClickHouse).

So the passage is really describing *why ClickHouse is built the way it is*: it deliberately makes single-row access harder in exchange for making **large-scale column aggregations dramatically faster** — which is exactly what dashboards, reporting, and analytics need.

---
## How it builds back the row
Exactly right — that's precisely the mechanism. The **position (ordinal index) is the glue.** There's no stored link between the values; the rule is simply:

> *The Nth value in every column belongs to the same row.*

```
ids:       [ 1,   2,   3  ]
names:     [ Ana, Ben, Cara]
countries: [ US,  UK,  US ]
ages:      [ 30,  25,  40 ]
             ↑
          index 0  →  (1, Ana, US, 30)  = row 1
          index 1  →  (2, Ben, UK, 25)  = row 2
          index 2  →  (3, Cara, US, 40) = row 3
```

To rebuild row 1, the engine reads **position 0 from each column** and stitches them together. That shared position is the *implicit* join key — it's never written down, it's just "line them up by order." This is why the columns must all stay in the **exact same order**; the alignment is the only thing holding a row together.

## The critical consequence: order must be preserved forever

Because position *is* identity, a column store can't casually reorder or shuffle one column — that would silently corrupt every row. So:

- All columns are written **in the same insertion order**
- That order is **stable** — column stores are essentially append-only and load data in big sorted batches, not random single-row inserts

This is another reason column stores are bad at OLTP-style random updates and great at bulk analytical loads.

## Two refinements to your mental model

Real column stores don't literally count from 0 to a billion every time — that'd be slow. Two things make position lookups efficient:

**1. Blocks + marks (sparse index).** ClickHouse stores each column in **compressed blocks** (e.g. 8192 rows per "granule") and keeps a small **marks file** that says "row 800,000 starts at byte offset X in this block." So to find position 800,000 it jumps near the right block via the marks, then scans a little — not a billion-step count.

**2. Deletes/updates don't shift positions.** If you delete row 2, the engine does **not** slide rows 3, 4, 5… down by one (that would rewrite every column entirely). Instead it marks row 2 as deleted (a tombstone / mask) and physically cleans it up later during a background merge. This keeps positions stable so the alignment never breaks.

## So, to answer directly

> Is it by index=0 in each column array?

**Yes.** The row is reconstructed by reading the **same ordinal position** out of every column and zipping the values back together. The position isn't stored as a field — it's the implicit contract of the layout. The engine just makes finding that position fast (via marks/offsets) and keeps it stable (via tombstones instead of shifting).

One nice way to hold it: a row store keeps a row's fields **together in space**; a column store keeps them **together in position** — same row, aligned by *where* they sit in each column rather than *where* they sit on disk.
