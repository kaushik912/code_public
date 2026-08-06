# Source Code Batch

This file contains 5 source files.

---

## File: src/main/java/com/example/liquibasedemo/domain/Author.java

```java
package com.example.liquibasedemo.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

/**
 * Maps to the {@code author} table created by V1 and altered by V3.
 * Because {@code ddl-auto=validate}, Hibernate will refuse to start if these
 * fields/columns drift from what the migrations actually produced.
 */
@Entity
@Table(name = "author")
public class Author {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(unique = true)
    private String email;

    protected Author() { // required by JPA
    }

    public Author(String name, String email) {
        this.name = name;
        this.email = email;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }
}
```

---

## File: src/main/java/com/example/liquibasedemo/domain/AuthorRepository.java

```java
package com.example.liquibasedemo.domain;

import org.springframework.data.jpa.repository.JpaRepository;

public interface AuthorRepository extends JpaRepository<Author, Long> {
}
```

---

## File: src/main/java/com/example/liquibasedemo/domain/Book.java

```java
package com.example.liquibasedemo.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

/** Maps to the {@code book} table created by V2. */
@Entity
@Table(name = "book")
public class Book {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(name = "published_year")
    private Integer publishedYear;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "author_id")
    private Author author;

    protected Book() { // required by JPA
    }

    public Book(String title, Integer publishedYear, Author author) {
        this.title = title;
        this.publishedYear = publishedYear;
        this.author = author;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public Integer getPublishedYear() {
        return publishedYear;
    }

    public Author getAuthor() {
        return author;
    }
}
```

---

## File: src/main/java/com/example/liquibasedemo/domain/BookRepository.java

```java
package com.example.liquibasedemo.domain;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface BookRepository extends JpaRepository<Book, Long> {

    /**
     * Join-fetch the author so the controller can read {@code book.getAuthor().getName()}
     * with {@code open-in-view=false} (no lazy-loading outside a transaction).
     */
    @Query("select b from Book b join fetch b.author order by b.publishedYear")
    List<Book> findAllWithAuthor();
}
```

---

## File: src/main/java/com/example/liquibasedemo/web/LibraryController.java

```java
package com.example.liquibasedemo.web;

import java.util.List;

import com.example.liquibasedemo.domain.Author;
import com.example.liquibasedemo.domain.AuthorRepository;
import com.example.liquibasedemo.domain.Book;
import com.example.liquibasedemo.domain.BookRepository;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Tiny REST layer so you can SEE the migrated schema through the app:
 *   GET  /api/authors        -> rows from the `author` table (V1 + V3 columns)
 *   GET  /api/books          -> rows via the join-fetch (V2 FK to author)
 *   POST /api/authors        -> prove writes work against the migrated schema
 */
@RestController
@RequestMapping("/api")
public class LibraryController {

    private final AuthorRepository authors;
    private final BookRepository books;

    public LibraryController(AuthorRepository authors, BookRepository books) {
        this.authors = authors;
        this.books = books;
    }

    public record AuthorView(Long id, String name, String email) {
    }

    public record BookView(Long id, String title, Integer publishedYear, String authorName) {
    }

    public record NewAuthor(String name, String email) {
    }

    @GetMapping("/authors")
    public List<AuthorView> listAuthors() {
        return authors.findAll().stream()
                .map(a -> new AuthorView(a.getId(), a.getName(), a.getEmail()))
                .toList();
    }

    @GetMapping("/books")
    public List<BookView> listBooks() {
        return books.findAllWithAuthor().stream()
                .map(b -> new BookView(b.getId(), b.getTitle(), b.getPublishedYear(),
                        b.getAuthor().getName()))
                .toList();
    }

    @PostMapping("/authors")
    public AuthorView create(@RequestBody NewAuthor body) {
        Author saved = authors.save(new Author(body.name(), body.email()));
        return new AuthorView(saved.getId(), saved.getName(), saved.getEmail());
    }
}
```

---

