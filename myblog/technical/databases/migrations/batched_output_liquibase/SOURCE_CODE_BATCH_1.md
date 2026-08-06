# Source Code Batch

This file contains 5 source files.

---

## File: .mvn/wrapper/maven-wrapper.properties

```
wrapperVersion=3.3.4
distributionType=only-script
distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.16/apache-maven-3.9.16-bin.zip
```

---

## File: HELP.md

```markdown
# Getting Started

### Reference Documentation
For further reference, please consider the following sections:

* [Official Apache Maven documentation](https://maven.apache.org/guides/index.html)
* [Spring Boot Maven Plugin Reference Guide](https://docs.spring.io/spring-boot/4.1.0/maven-plugin)
* [Create an OCI image](https://docs.spring.io/spring-boot/4.1.0/maven-plugin/build-image.html)
* [Spring Web](https://docs.spring.io/spring-boot/4.1.0/reference/web/servlet.html)
* [Spring Data JPA](https://docs.spring.io/spring-boot/4.1.0/reference/data/sql.html#data.sql.jpa-and-spring-data)
* [Liquibase Migration](https://docs.spring.io/spring-boot/4.1.0/how-to/data-initialization.html#howto.data-initialization.migration-tool.liquibase)

### Guides
The following guides illustrate how to use some features concretely:

* [Building a RESTful Web Service](https://spring.io/guides/gs/rest-service/)
* [Serving Web Content with Spring MVC](https://spring.io/guides/gs/serving-web-content/)
* [Building REST services with Spring](https://spring.io/guides/tutorials/rest/)
* [Accessing Data with JPA](https://spring.io/guides/gs/accessing-data-jpa/)

### Maven Parent overrides

Due to Maven's design, elements are inherited from the parent POM to the project POM.
While most of the inheritance is fine, it also inherits unwanted elements like `<license>` and `<developers>` from the parent.
To prevent this, the project POM contains empty overrides for these elements.
If you manually switch to a different parent and actually want the inheritance, you need to remove those overrides.

```

---

## File: README.md

```markdown
# Liquibase + Spring Boot — end-to-end demo

The **same** "library" app as the Flyway demo, but the schema is owned by
**Liquibase YAML changelogs**. Hibernate is `ddl-auto=validate` (validates only).

Spring Boot 4.1.0 · Java 17 · H2 (zero setup) · Liquibase.

## Run it

```bash
./mvnw test              # boots context -> runs Liquibase on H2 -> validates JPA -> asserts data
./mvnw spring-boot:run   # or: ./mvnw package && java -jar target/liquibase-demo-*.jar
```

```bash
curl localhost:8080/api/books
curl -X POST localhost:8080/api/authors -H 'Content-Type: application/json' \
     -d '{"name":"Octavia E. Butler","email":"octavia@example.com"}'
```

## How Liquibase works (the whole model in 6 lines)

- A **master changelog** (`db.changelog-master.yaml`) `include`s per-version changelogs in order.
- The unit of change is a **changeSet**, identified by `(id, author)` and stored with a checksum.
- A changeset runs **once**; `runOnChange:true` re-runs it when its checksum changes; `runAlways:true` every time.
- Changes are declared as **typed operations** (`createTable`, `addColumn`, `addForeignKeyConstraint`…), so Liquibase emits the right SQL per database — you don't write dialect SQL.
- Liquibase tracks state in two tables it creates: `DATABASECHANGELOG` (what ran) and `DATABASECHANGELOGLOCK` (concurrency lock).
- Spring Boot auto-runs the update before the JPA `EntityManagerFactory` is built.

## What each changelog teaches

| File | Liquibase feature |
|------|-------------------|
| `v1__create-author.yaml` | `createTable`, explicit `rollback` |
| `v2__create-book.yaml`   | one step as 3 small changesets: `createTable`, `addForeignKeyConstraint`, `createIndex` |
| `v3__add-author-email.yaml` | `preConditions` (`columnExists` + `onFail: MARK_RAN`), `addColumn`, `addUniqueConstraint` |
| `v4__seed-data.yaml`     | `context: dev` gating, `insert`, raw `sql`, `delete` rollbacks |
| `v5__book-catalog-view.yaml` | `runOnChange: true` + `createView replaceIfExists` (redefinable object) |

## Features shown that Flyway does differently

- **Database-agnostic change types** — the FK/index/unique constraints are declared, not
  hand-written SQL, so the same changelog targets H2 *and* PostgreSQL. (Liquibase also supports
  plain `.sql` changelogs if you prefer Flyway-style raw SQL.)
- **Built-in rollback** — every changeset here has a rollback, so `liquibase rollbackCount 1`
  (or `mvn liquibase:rollback`) can undo changes. Flyway's undo is a paid feature.
- **Preconditions** — assert database state before running (`v3`, and the `dbms` check in master).
- **Contexts** — `contexts=dev` includes the seed data; `contexts=prod` would skip it.

## Switching to PostgreSQL

Uncomment the Postgres datasource block in `application.properties` and start a DB
(`docker run -e POSTGRES_PASSWORD=pw -p 5432:5432 postgres`). The changelogs are unchanged —
Liquibase generates Postgres-specific DDL from the same declarations.
```

---

## File: pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>
	<parent>
		<groupId>org.springframework.boot</groupId>
		<artifactId>spring-boot-starter-parent</artifactId>
		<version>4.1.0</version>
		<relativePath/> <!-- lookup parent from repository -->
	</parent>
	<groupId>com.example</groupId>
	<artifactId>liquibase-demo</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>liquibase-demo</name>
	<description/>
	<url/>
	<licenses>
		<license/>
	</licenses>
	<developers>
		<developer/>
	</developers>
	<scm>
		<connection/>
		<developerConnection/>
		<tag/>
		<url/>
	</scm>
	<properties>
		<java.version>17</java.version>
	</properties>
	<dependencies>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-h2console</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-jpa</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-liquibase</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc</artifactId>
		</dependency>

		<dependency>
			<groupId>com.h2database</groupId>
			<artifactId>h2</artifactId>
			<scope>runtime</scope>
		</dependency>
		<dependency>
			<groupId>org.postgresql</groupId>
			<artifactId>postgresql</artifactId>
			<scope>runtime</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-data-jpa-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-liquibase-test</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc-test</artifactId>
			<scope>test</scope>
		</dependency>
	</dependencies>

	<build>
		<plugins>
			<plugin>
				<groupId>org.springframework.boot</groupId>
				<artifactId>spring-boot-maven-plugin</artifactId>
			</plugin>
		</plugins>
	</build>

</project>
```

---

## File: src/main/java/com/example/liquibasedemo/LiquibaseDemoApplication.java

```java
package com.example.liquibasedemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class LiquibaseDemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(LiquibaseDemoApplication.class, args);
	}

}
```

---

