# Source Code Batch

This file contains 3 source files.

---

## File: src/main/resources/db/changelog/changes/v5__book-catalog-view.yaml

```yaml
# runOnChange:true is Liquibase's answer to Flyway's REPEATABLE migrations.
# Normally a changeset runs once; with runOnChange, Liquibase re-applies it
# whenever its checksum changes. Combined with replaceIfExists this is the
# clean way to manage redefinable objects (views, procedures, functions):
# just edit the SELECT below and restart — Liquibase re-creates the view.
databaseChangeLog:
  - changeSet:
      id: v5-book-catalog-view
      author: demo
      runOnChange: true
      changes:
        - createView:
            viewName: book_catalog
            replaceIfExists: true
            selectQuery: |
              SELECT b.id             AS book_id,
                     b.title          AS title,
                     b.published_year AS published_year,
                     a.name           AS author_name
              FROM book b
              JOIN author a ON a.id = b.author_id
      rollback:
        - dropView:
            viewName: book_catalog
```

---

## File: src/main/resources/db/changelog/db.changelog-master.yaml

```yaml
# Master changelog — the single entry point Spring points at.
# It does nothing but (a) assert a global precondition and (b) include the
# per-version changelogs IN ORDER. Keeping one file per logical change and
# an ordered master is the standard Liquibase layout.
databaseChangeLog:
  # Global precondition: refuse to run against an unexpected database engine.
  # onFail=HALT (the default) stops the whole update if this fails.
  - preConditions:
      - dbms:
          type: h2, postgresql

  - include:
      file: changes/v1__create-author.yaml
      relativeToChangelogFile: true
  - include:
      file: changes/v2__create-book.yaml
      relativeToChangelogFile: true
  - include:
      file: changes/v3__add-author-email.yaml
      relativeToChangelogFile: true
  - include:
      file: changes/v4__seed-data.yaml
      relativeToChangelogFile: true
  - include:
      file: changes/v5__book-catalog-view.yaml
      relativeToChangelogFile: true
```

---

## File: src/test/java/com/example/liquibasedemo/LiquibaseDemoApplicationTests.java

```java
package com.example.liquibasedemo;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.liquibasedemo.domain.AuthorRepository;
import com.example.liquibasedemo.domain.BookRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

/**
 * End-to-end check: booting the context runs Liquibase against H2 (contexts=dev),
 * then Hibernate validates the entities against the changelog-produced schema.
 */
@SpringBootTest
class LiquibaseDemoApplicationTests {

    @Autowired
    AuthorRepository authors;
    @Autowired
    BookRepository books;
    @Autowired
    JdbcTemplate jdbc;

    @Test
    void contextLoads() {
    }

    @Test
    void changelogSeededData() {
        assertThat(authors.count()).isEqualTo(2); // v4 ran because context=dev is active
        assertThat(books.count()).isEqualTo(4);
    }

    @Test
    void liquibaseRecordedEveryChangeSet() {
        // Liquibase names its tracking table DATABASECHANGELOG (uppercase, unquoted).
        Integer applied = jdbc.queryForObject("SELECT COUNT(*) FROM DATABASECHANGELOG", Integer.class);
        assertThat(applied).isEqualTo(9); // v1(1) + v2(3) + v3(2) + v4(2) + v5(1)
    }

    @Test
    void runOnChangeViewIsQueryable() {
        Integer rows = jdbc.queryForObject("SELECT COUNT(*) FROM book_catalog", Integer.class);
        assertThat(rows).isEqualTo(4);
    }
}
```

---

