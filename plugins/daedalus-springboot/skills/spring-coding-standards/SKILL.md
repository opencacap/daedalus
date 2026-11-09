---
name: spring-coding-standards
description: "Spring Boot coding conventions: controller naming, constructor injection, centralized exception handling, project layout, configuration properties, and test slices. Use when writing or reviewing Java in a Spring Boot service, together with daedalus-java:java-coding-standards."
metadata:
  origin: ECC
---

# Spring Coding Standards

Spring Boot conventions that extend `daedalus-java:java-coding-standards`. Apply both.

## Naming

```java
// PASS: REST controllers named as *Controller
public class MarketController {}
```

## Dependency Injection

```java
// PASS: Constructor injection (preferred over @Autowired on fields)
@Service
public class MarketService {
  private final MarketRepository marketRepository;

  public MarketService(MarketRepository marketRepository) {
    this.marketRepository = marketRepository;
  }
}

// FAIL: Field injection with @Autowired
@Autowired
private MarketRepository marketRepository; // use constructor injection
```

## Centralised Exception Handling

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
  @ExceptionHandler(MarketNotFoundException.class)
  public ResponseEntity<ErrorResponse> handle(MarketNotFoundException ex) {
    return ResponseEntity.status(404).body(ErrorResponse.from(ex));
  }
}
```

## Project Structure

```text
src/main/java/com/example/app/
  config/
  controller/
  service/
  repository/
  domain/
  dto/
  util/
src/main/resources/
  application.yml
src/test/java/... (mirrors main)
```

## Configuration

```java
@ConfigurationProperties(prefix = "market")
public record MarketProperties(int maxPageSize, Duration cacheTtl) {}
```

## Testing Expectations

- `@WebMvcTest` for controller slices, `@DataJpaTest` for repository slices
- `@SpringBootTest` reserved for full integration tests
- `@MockBean` for replacing beans in Spring context

```java
@WebMvcTest(MarketController.class)
class MarketControllerTest {
  @Autowired MockMvc mockMvc;
  @MockBean MarketService marketService;
}
```
