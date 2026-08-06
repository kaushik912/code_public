# Source Code Batch

This file contains 2 source files.

---

## File: src/main/resources/application.properties

```
spring.application.name=flyway-demo

# ============================================================
# Datasource — H2 in-memory so the demo runs with ZERO setup.
# JDBC URL kept open for the life of the JVM (DB_CLOSE_DELAY=-1)
# so the H2 web console can inspect it while the app runs.
# ============================================================
spring.datasource.url=jdbc:h2:mem:library;DB_CLOSE_DELAY=-1
spring.datasource.username=sa
spring.datasource.password=

# H2 web console -> http://localhost:8080/h2-console  (use the JDBC URL above)
spring.h2.console.enabled=true

# ============================================================
# JPA — Flyway OWNS the schema. Hibernate must never create or
# alter tables; it only VALIDATES that the entities match the
# schema the migrations produced. This is the key discipline:
# ddl-auto=validate, never `update` in a migration-managed app.
# ============================================================
spring.jpa.hibernate.ddl-auto=validate
spring.jpa.open-in-view=false
spring.jpa.properties.hibernate.format_sql=true
# spring.jpa.show-sql=true

# ============================================================
# Flyway
#   - locations: where .sql migrations live (the default, shown
#     explicitly for clarity).
#   - baseline-on-migrate: stamp an existing DB as the baseline
#     the first time Flyway runs (useful for adopting Flyway on
#     a DB that already has tables).
#   - validate-on-migrate: fail fast if an already-applied
#     migration file was edited (checksum mismatch).
# ============================================================
spring.flyway.enabled=true
spring.flyway.locations=classpath:db/migration
spring.flyway.baseline-on-migrate=true
spring.flyway.validate-on-migrate=true

# ============================================================
# Real-world PostgreSQL — swap the datasource block above for
# this (e.g. `docker run -e POSTGRES_PASSWORD=pw -p 5432:5432 postgres`)
# and everything else stays identical. Flyway auto-detects the
# dialect via the flyway-database-postgresql dependency.
# ------------------------------------------------------------
# spring.datasource.url=jdbc:postgresql://localhost:5432/library
# spring.datasource.username=postgres
# spring.datasource.password=pw
# ============================================================
```

---

## File: src/test/java/com/example/flywaydemo/FlywayDemoApplicationTests.java

```java
package com.example.flywaydemo;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.flywaydemo.domain.AuthorRepository;
import com.example.flywaydemo.domain.BookRepository;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

/**
 * This is a genuine end-to-end check: booting the context runs Flyway against
 * H2, then Hibernate validates the entities against the migrated schema. If any
 * migration or mapping is wrong, the context fails to start and the test fails.
 */
@SpringBootTest
class FlywayDemoApplicationTests {

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
    void migrationsSeededData() {
        assertThat(authors.count()).isEqualTo(2);
        assertThat(books.count()).isEqualTo(4);
    }

    @Test
    void flywayRecordedEveryVersionedMigration() {
        Integer applied = jdbc.queryForObject(
                "SELECT COUNT(*) FROM \"flyway_schema_history\" WHERE \"success\" = TRUE AND \"version\" IS NOT NULL",
                Integer.class);
        assertThat(applied).isEqualTo(4); // V1..V4
    }

    @Test
    void repeatableViewIsQueryable() {
        Integer rows = jdbc.queryForObject("SELECT COUNT(*) FROM book_catalog", Integer.class);
        assertThat(rows).isEqualTo(4);
    }
}
```

---

