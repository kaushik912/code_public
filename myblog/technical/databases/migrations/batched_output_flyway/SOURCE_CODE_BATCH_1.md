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
* [Flyway Migration](https://docs.spring.io/spring-boot/4.1.0/how-to/data-initialization.html#howto.data-initialization.migration-tool.flyway)

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
# Flyway + Spring Boot — end-to-end demo

A tiny "library" app whose **schema is owned entirely by Flyway SQL migrations**.
Hibernate is set to `ddl-auto=validate`, so it only checks that the JPA entities
match the schema the migrations produced — it never creates or alters tables.

Spring Boot 4.1.0 · Java 17 · H2 (zero setup) · Flyway.

## Run it

```bash
./mvnw test          # boots context -> runs Flyway on H2 -> validates JPA -> asserts seed data
./mvnw spring-boot:run   # or: ./mvnw package && java -jar target/flyway-demo-*.jar
```

Then:

```bash
curl localhost:8080/api/books
curl localhost:8080/api/authors
curl -X POST localhost:8080/api/authors -H 'Content-Type: application/json' \
     -d '{"name":"Octavia E. Butler","email":"octavia@example.com"}'
```

H2 console: http://localhost:8080/h2-console (JDBC URL `jdbc:h2:mem:library;DB_CLOSE_DELAY=-1`, user `sa`).

## How Flyway works (the whole model in 6 lines)

- Migrations live in `src/main/resources/db/migration` as `.sql` files.
- **Versioned**: `V<n>__desc.sql` — run once, in ascending version order, recorded forever.
- **Repeatable**: `R__desc.sql` — no version; re-run whenever the file's checksum changes; always after versioned ones.
- Flyway tracks state in a table it creates: `flyway_schema_history` (version, checksum, success…).
- On mismatch of an already-applied file's checksum, `validate-on-migrate` makes startup **fail fast**.
- Spring Boot auto-runs `flyway.migrate()` before the JPA `EntityManagerFactory` is built.

## The migrations in this demo

| File | Kind | What it teaches |
|------|------|-----------------|
| `V1__create_author_table.sql` | versioned | first object; naming convention |
| `V2__create_book_table.sql`   | versioned | child table + FK + index |
| `V3__add_author_email.sql`    | versioned | **evolve** an existing table (never edit V1) |
| `V4__seed_sample_data.sql`    | versioned | seed data + the IDENTITY-restart gotcha |
| `R__book_catalog_view.sql`    | repeatable | redefinable object (a VIEW) re-applied on checksum change |

## Golden rules this demo follows

1. **Never edit a migration that has already run** anywhere. Add a new `V` file instead.
   (In-memory H2 is recreated each boot, so *this* demo can be edited freely — a real
   database cannot.)
2. `ddl-auto=validate`, never `update`. Migrations are the single source of truth.
3. Seeding explicit primary keys? Restart the identity counter (see the comment in `V4`),
   or the next app-generated id will collide.

## Switching to PostgreSQL

Uncomment the Postgres datasource block in `application.properties`, start a DB
(`docker run -e POSTGRES_PASSWORD=pw -p 5432:5432 postgres`), and run. The same SQL
migrations apply unchanged; Flyway picks the Postgres dialect via the
`flyway-database-postgresql` dependency.
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
	<artifactId>flyway-demo</artifactId>
	<version>0.0.1-SNAPSHOT</version>
	<name>flyway-demo</name>
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
			<artifactId>spring-boot-starter-flyway</artifactId>
		</dependency>
		<dependency>
			<groupId>org.springframework.boot</groupId>
			<artifactId>spring-boot-starter-webmvc</artifactId>
		</dependency>
		<dependency>
			<groupId>org.flywaydb</groupId>
			<artifactId>flyway-database-postgresql</artifactId>
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
			<artifactId>spring-boot-starter-flyway-test</artifactId>
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

## File: src/main/java/com/example/flywaydemo/FlywayDemoApplication.java

```java
package com.example.flywaydemo;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class FlywayDemoApplication {

	public static void main(String[] args) {
		SpringApplication.run(FlywayDemoApplication.class, args);
	}

}
```

---

