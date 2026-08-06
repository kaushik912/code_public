# Source Code Batch

This file contains 5 source files.

---

## File: src/main/resources/application.properties

```
spring.application.name=liquibase-demo

# ============================================================
# Datasource — H2 in-memory so the demo runs with ZERO setup.
# ============================================================
spring.datasource.url=jdbc:h2:mem:library;DB_CLOSE_DELAY=-1
spring.datasource.username=sa
spring.datasource.password=

# H2 web console -> http://localhost:8080/h2-console  (use the JDBC URL above)
spring.h2.console.enabled=true

# ============================================================
# JPA — Liquibase OWNS the schema. Hibernate only VALIDATES.
# ============================================================
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.open-in-view=false
spring.jpa.properties.hibernate.format_sql=true

# ============================================================
# Liquibase
#   - change-log: the single master changelog Spring runs at startup.
#   - contexts: only changesets tagged with these contexts run. Here we
#     run "dev", which pulls in the seed-data changesets. In prod you'd
#     set spring.liquibase.contexts=prod (or leave seed out entirely).
# ============================================================
spring.liquibase.change-log=classpath:db/changelog/db.changelog-master.yaml
spring.liquibase.contexts=dev

# ============================================================
# Real-world PostgreSQL — swap the datasource block above for this.
# The SAME changelogs apply unchanged (Liquibase abstracts the dialect).
# ------------------------------------------------------------
# spring.datasource.url=jdbc:postgresql://localhost:5432/library
# spring.datasource.username=postgres
# spring.datasource.password=pw
# ============================================================
```

---

## File: src/main/resources/db/changelog/changes/v1__create-author.yaml

```yaml
# A "changeSet" is Liquibase's unit of change. It is identified by the pair
# (id, author) and, once applied, is recorded in the DATABASECHANGELOG table
# with a checksum. A changeset is applied AT MOST ONCE and is never re-run
# (unless you mark it runOnChange/runAlways).
databaseChangeLog:
  - changeSet:
      id: v1-create-author
      author: demo
      comment: Create the author table
      changes:
        - createTable:
            tableName: author
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    nullable: false
              - column:
                  name: name
                  type: VARCHAR(200)
                  constraints:
                    nullable: false
      # Liquibase can auto-generate a rollback for createTable, but showing it
      # explicitly makes `liquibase rollback` behaviour obvious.
      rollback:
        - dropTable:
            tableName: author
```

---

## File: src/main/resources/db/changelog/changes/v2__create-book.yaml

```yaml
# One logical step ("add the book table") split into three changesets. Small,
# single-purpose changesets are the Liquibase idiom: each is independently
# tracked, rolled back, and reasoned about. Note we describe the FK and index
# as their OWN change types instead of raw SQL — this is what lets Liquibase
# generate correct SQL for H2, PostgreSQL, Oracle, etc. from one definition.
databaseChangeLog:
  - changeSet:
      id: v2-create-book-table
      author: demo
      changes:
        - createTable:
            tableName: book
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    nullable: false
              - column:
                  name: title
                  type: VARCHAR(300)
                  constraints:
                    nullable: false
              - column:
                  name: published_year
                  type: INT
              - column:
                  name: author_id
                  type: BIGINT
                  constraints:
                    nullable: false

  - changeSet:
      id: v2-fk-book-author
      author: demo
      changes:
        - addForeignKeyConstraint:
            constraintName: fk_book_author
            baseTableName: book
            baseColumnNames: author_id
            referencedTableName: author
            referencedColumnNames: id

  - changeSet:
      id: v2-idx-book-author
      author: demo
      changes:
        - createIndex:
            indexName: idx_book_author_id
            tableName: book
            columns:
              - column:
                  name: author_id
```

---

## File: src/main/resources/db/changelog/changes/v3__add-author-email.yaml

```yaml
# Evolving an existing table. The first changeset carries a PRECONDITION:
# only add the column if it doesn't already exist. onFail=MARK_RAN means
# "if the precondition fails, quietly record this changeset as run and skip
# it" — handy when adopting Liquibase on a DB that already had the column.
databaseChangeLog:
  - changeSet:
      id: v3-add-author-email
      author: demo
      preConditions:
        - onFail: MARK_RAN
        - not:
            - columnExists:
                tableName: author
                columnName: email
      changes:
        - addColumn:
            tableName: author
            columns:
              - column:
                  name: email
                  type: VARCHAR(320)
      rollback:
        - dropColumn:
            tableName: author
            columnName: email

  - changeSet:
      id: v3-unique-author-email
      author: demo
      changes:
        - addUniqueConstraint:
            tableName: author
            columnNames: email
            constraintName: uq_author_email
```

---

## File: src/main/resources/db/changelog/changes/v4__seed-data.yaml

```yaml
# Seed data guarded by a CONTEXT. These changesets only run when the active
# Liquibase contexts include "dev" (see spring.liquibase.contexts). Point the
# same app at prod with contexts=prod and this data simply won't be inserted.
databaseChangeLog:
  - changeSet:
      id: v4-seed-authors
      author: demo
      context: dev
      changes:
        - insert:
            tableName: author
            columns:
              - column: {name: id, valueNumeric: 1}
              - column: {name: name, value: "Ursula K. Le Guin"}
              - column: {name: email, value: "ursula@example.com"}
        - insert:
            tableName: author
            columns:
              - column: {name: id, valueNumeric: 2}
              - column: {name: name, value: "Terry Pratchett"}
              - column: {name: email, value: "terry@example.com"}
        # Same identity gotcha as the Flyway demo: explicit ids don't advance
        # the auto-increment counter, so restart it past the seeded rows.
        - sql:
            sql: ALTER TABLE author ALTER COLUMN id RESTART WITH 3
      rollback:
        - delete:
            tableName: author
            where: id IN (1, 2)

  - changeSet:
      id: v4-seed-books
      author: demo
      context: dev
      changes:
        - insert:
            tableName: book
            columns:
              - column: {name: title, value: "A Wizard of Earthsea"}
              - column: {name: published_year, valueNumeric: 1968}
              - column: {name: author_id, valueNumeric: 1}
        - insert:
            tableName: book
            columns:
              - column: {name: title, value: "The Left Hand of Darkness"}
              - column: {name: published_year, valueNumeric: 1969}
              - column: {name: author_id, valueNumeric: 1}
        - insert:
            tableName: book
            columns:
              - column: {name: title, value: "The Colour of Magic"}
              - column: {name: published_year, valueNumeric: 1983}
              - column: {name: author_id, valueNumeric: 2}
        - insert:
            tableName: book
            columns:
              - column: {name: title, value: "Mort"}
              - column: {name: published_year, valueNumeric: 1987}
              - column: {name: author_id, valueNumeric: 2}
      rollback:
        - delete:
            tableName: book
            where: author_id IN (1, 2)
```

---

