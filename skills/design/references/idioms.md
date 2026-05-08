# Per-Language Idioms for Interface Design Principles

## Table of Contents
1. [Go](#go)
2. [Clojure](#clojure)
3. [Java](#java)
4. [Kotlin](#kotlin)
5. [TypeScript](#typescript)
6. [Python](#python)

---

## Go

Go is the reference implementation of these principles. The language enforces implicit satisfaction,
which makes consumer-side interface definition the natural and only sensible approach.

### Principle 1 — Consumer-side definition
```go
// consumer/package
type Notifier interface {
    Notify(msg string) error
}

// producer/package — knows nothing about Notifier
type EmailSender struct { ... }
func (e *EmailSender) Notify(msg string) error { ... }
```

### Principle 2 — Minimal surface
```go
// stdlib examples: the gold standard
type Reader interface { Read(p []byte) (n int, err error) }
type Writer interface { Write(p []byte) (n int, err error) }
type ReadWriter interface { Reader; Writer } // composition
```

### Principle 3 — Behavioral naming
```go
// Good
type Stringer interface { String() string }
type Closer interface { Close() error }
type Validator interface { Validate() error }

// Bad
type UserService interface { ... }
type Manager interface { ... }
```

### Principle 4 — No premature abstraction
```go
// Don't do this when you only have PostgresStore
type UserStore interface { FindByID(id int) (*User, error) }

// Do this when you add a second impl (e.g., InMemoryStore for tests)
// The interface emerges; it isn't declared upfront
```

### Principle 7 — Avoid empty interface
```go
// Bad
func Process(v interface{}) { ... }

// Good — use generics (Go 1.18+)
type Processable interface { Validate() error }
func Process[T Processable](v T) { ... }
```

### Principle 8 — Concrete returns
```go
// Good — return concrete, accept interface
func NewPostgresStore(cfg Config) *PostgresStore { ... }
func Save(s Storer, entity Entity) error { ... }
```

---

## Clojure

Clojure offers two mechanisms: **protocols** (for polymorphism on types) and **multimethods**
(for open dispatch on arbitrary values). Protocols are the closer analog to interfaces.

### Principle 1 — Consumer-side definition
```clojure
;; Define the protocol in the namespace that needs it
(ns myapp.notifications)

(defprotocol Notifier
  (notify [this msg]))

;; The EmailSender implementation can live anywhere
(ns myapp.email
  (:require [myapp.notifications :refer [Notifier]]))

(defrecord EmailSender [config]
  Notifier
  (notify [this msg]
    (send-email (:address config) msg)))
```

### Principle 2 — Minimal surface
```clojure
;; One function per protocol is common and idiomatic
(defprotocol Reader
  (read-data [this]))

(defprotocol Writer
  (write-data [this data]))

;; Compose via satisfies? or by implementing multiple protocols on one type
```

### Principle 3 — Behavioral naming
```clojure
;; Good — verb or capability noun
(defprotocol Fetchable (fetch [this id]))
(defprotocol Persistable (persist [this entity]))

;; Bad — role noun
(defprotocol UserRepository ...)
```

### Principle 4 — No premature abstraction
```clojure
;; Clojure's dynamic nature means you often don't need a protocol at all.
;; A plain function that accepts a map works until you genuinely need dispatch.
;; Protocol when: multiple dispatch targets OR you want Java interop.
```

### Principle 5 — Behavior, not data
```clojure
;; Bad — modeling data shape
(defprotocol User
  (get-name [this])
  (get-email [this]))

;; Good — use maps/records for data, protocols for behavior
(defprotocol Authenticatable
  (authenticate [this credentials]))
```

### Principle 6 — Composition
```clojure
;; Types can implement multiple protocols
(defrecord FileStore [path]
  Reader
  (read-data [this] ...)
  Writer
  (write-data [this data] ...))
```

### Principle 7 — Avoid untyped dispatch
```clojure
;; Clojure is dynamic, but avoid protocol methods that accept raw `Object`
;; when you can use spec or malli to validate at the boundary instead.
(defprotocol Processor
  (process [this ^:validated input])) ;; document expected shape via spec
```

### Note on multimethods
Use multimethods (`defmulti`/`defmethod`) when dispatch depends on a value attribute,
not a type. Protocols are for type-based dispatch. Don't conflate them.

---

## Java

Java's explicit `implements` declaration inverts the consumer-side principle by default.
You must compensate with discipline: keep interfaces in the consumer's package, and resist
the IDE's reflex to generate interfaces from every class.

### Principle 1 — Consumer-side definition
```java
// consumer/notifications/Notifier.java
package consumer.notifications;

public interface Notifier {
    void notify(String msg) throws NotificationException;
}

// producer/email/EmailSender.java — imports consumer package
import consumer.notifications.Notifier;

public class EmailSender implements Notifier {
    public void notify(String msg) throws NotificationException { ... }
}
```

### Principle 2 — Minimal surface + composition
```java
public interface Reader<T> { T read(); }
public interface Writer<T> { void write(T value); }

// Composition via extends
public interface ReadWriter<T> extends Reader<T>, Writer<T> {}
```

### Principle 3 — Behavioral naming
```java
// Good
public interface Validator<T> { ValidationResult validate(T input); }
public interface Closeable { void close() throws IOException; } // java.io.Closeable

// Bad
public interface UserServiceInterface { ... }
```

### Principle 4 — No premature abstraction
```java
// Do NOT generate this unless you have a second impl or a test double
public interface UserRepositoryInterface {
    User findById(Long id);
}
// Just use UserRepository (the concrete class) until you genuinely need substitution
```

### Principle 6 — Prefer composition over inheritance
```java
// Bad — deep hierarchy
public interface BaseService { ... }
public interface UserService extends BaseService { ... }
public interface AdminService extends UserService { ... }

// Good — flat, composable
public interface UserReader { User findById(Long id); }
public interface UserWriter { void save(User user); }
```

### Principle 7 — Avoid raw types / Object
```java
// Bad
public interface Processor { Object process(Object input); }

// Good — bounded generics
public interface Processor<T extends Validatable> {
    ProcessedResult<T> process(T input);
}
```

### Java-specific: default methods
Default methods in interfaces are useful for providing fallback behavior, but avoid using
them to smuggle in state or complex logic — that belongs in an abstract class or delegate.

---

## Kotlin

Kotlin's interfaces are more powerful than Java's (they can hold state via properties and
provide default implementations), which makes it easier to accidentally violate the minimal
surface principle. Apply extra discipline.

### Principle 1 — Consumer-side definition
```kotlin
// Kotlin's implicit interface satisfaction doesn't exist — explicit `implements` required.
// Compensate by defining interfaces in the consumer module.

// consumer module
interface Notifier {
    fun notify(msg: String)
}

// producer module
class EmailSender(private val config: Config) : Notifier {
    override fun notify(msg: String) { ... }
}
```

### Principle 2 — Minimal surface
```kotlin
fun interface Predicate<T> {  // SAM interface — single abstract method
    fun test(value: T): Boolean
}

// Compose via delegation
interface ReadWriter<T> : Reader<T>, Writer<T>
```

### Principle 3 — Behavioral naming + fun interface
```kotlin
// SAM / functional interfaces enable lambda syntax — prefer for single-method interfaces
fun interface Validator<T> {
    fun validate(input: T): Boolean
}

val notEmpty = Validator<String> { it.isNotBlank() }
```

### Principle 4 — Sealed classes as alternative
```kotlin
// When you have a closed, known set of implementations, prefer sealed classes over interfaces.
// Interfaces are for open extensibility. Sealed classes are for exhaustive dispatch.
sealed class Result<out T>
data class Success<T>(val value: T) : Result<T>()
data class Failure(val error: Throwable) : Result<Nothing>()
```

### Principle 5 — No data in interfaces
```kotlin
// Bad — interface modeling an entity
interface User {
    val name: String
    val email: String
    fun getName(): String  // redundant with property
}

// Good — data class for data, interface for behavior
data class User(val name: String, val email: String)

interface Authenticatable {
    fun authenticate(credentials: Credentials): AuthToken
}
```

### Principle 7 — Avoid Any
```kotlin
// Bad
interface Processor { fun process(input: Any): Any }

// Good — reified generics or bounded type parameter
interface Processor<T : Validatable> {
    fun process(input: T): ProcessedResult
}
```

---

## TypeScript

TypeScript's structural typing (like Go) makes consumer-side definition natural. The compiler
checks shape compatibility, not declaration. This is a superpower — use it.

### Principle 1 — Consumer-side definition (structural typing)
```typescript
// consumer/notifications.ts
interface Notifier {
  notify(msg: string): Promise<void>;
}

// producer/email-sender.ts — no import of Notifier needed
export class EmailSender {
  async notify(msg: string): Promise<void> { ... }
}

// At the call site, EmailSender satisfies Notifier structurally
function sendAlert(notifier: Notifier, msg: string) { ... }
sendAlert(new EmailSender(), "alert"); // works
```

### Principle 2 — Minimal surface
```typescript
interface Reader<T> { read(): Promise<T>; }
interface Writer<T> { write(value: T): Promise<void>; }

// Compose with intersection
type ReadWriter<T> = Reader<T> & Writer<T>;
```

### Principle 3 — Behavioral naming
```typescript
// Good
interface Serializable { serialize(): string; }
interface Comparable<T> { compareTo(other: T): number; }

// Bad
interface UserServiceInterface { ... }
```

### Principle 4 — No premature abstraction
```typescript
// TypeScript's structural typing means you often don't need an explicit interface at all —
// inline types work fine for single-use cases.
function save(store: { save(entity: Entity): void }, entity: Entity) { ... }
// Promote to a named interface only when used in 2+ places or for documentation value
```

### Principle 6 — Composition over extension
```typescript
// Bad — inheritance chain
interface BaseRepository<T> { findAll(): T[]; }
interface UserRepository extends BaseRepository<User> { findByEmail(email: string): User; }

// Good — compose
type UserStore = Reader<User> & { findByEmail(email: string): User | undefined; };
```

### Principle 7 — Avoid `any`
```typescript
// Bad
interface Processor { process(input: any): any; }

// Good — generic with constraint
interface Processor<T extends Validatable> {
  process(input: T): ProcessedResult<T>;
}

// Or discriminated union for closed sets
type Input = TextInput | ImageInput | AudioInput;
interface Processor { process(input: Input): Result; }
```

### TypeScript-specific: `type` vs `interface`
- Use `interface` for object shapes that will be implemented by classes or extended.
- Use `type` for unions, intersections, mapped types, and aliases.
- Prefer `interface` when defining an abstraction boundary (it signals intent better).

---

## Python

Python's duck typing means interfaces are implicit by default. Use `Protocol` (PEP 544,
Python 3.8+) for structural typing without inheritance, or `ABC` for explicit contracts.
Prefer `Protocol` — it's the closer analog to Go interfaces.

### Principle 1 — Consumer-side definition with Protocol
```python
# consumer/notifications.py
from typing import Protocol

class Notifier(Protocol):
    def notify(self, msg: str) -> None: ...

# producer/email_sender.py — no import of Notifier
class EmailSender:
    def notify(self, msg: str) -> None:
        send_email(msg)

# At call site — EmailSender satisfies Notifier structurally
def send_alert(notifier: Notifier, msg: str) -> None:
    notifier.notify(msg)

send_alert(EmailSender(), "alert")  # passes type checking
```

### Principle 2 — Minimal surface
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Reader(Protocol):
    def read(self) -> bytes: ...

class Writer(Protocol):
    def write(self, data: bytes) -> int: ...

# Composition via multiple Protocol inheritance
class ReadWriter(Reader, Writer, Protocol): ...
```

### Principle 3 — Behavioral naming
```python
# Good
class Serializable(Protocol):
    def serialize(self) -> str: ...

class Closeable(Protocol):
    def close(self) -> None: ...

# Bad
class UserManagerInterface(ABC): ...
```

### Principle 4 — No premature abstraction
```python
# Prefer duck typing + type hints for single-use cases
def save(store, entity: Entity) -> None:  # `store` typed structurally via Protocol only if needed
    store.save(entity)

# Introduce Protocol when: 2+ implementations, or you want static type checking guarantees
```

### Principle 5 — No data protocols
```python
# Bad — Protocol modeling data shape
class UserProtocol(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def email(self) -> str: ...

# Good — use dataclass for data, Protocol for behavior
@dataclass
class User:
    name: str
    email: str

class Authenticatable(Protocol):
    def authenticate(self, credentials: Credentials) -> AuthToken: ...
```

### Principle 7 — Avoid `Any`
```python
from typing import TypeVar, Protocol

# Bad
class Processor(Protocol):
    def process(self, input: Any) -> Any: ...

# Good — bounded TypeVar
class Validatable(Protocol):
    def validate(self) -> bool: ...

T = TypeVar("T", bound=Validatable)

class Processor(Protocol):
    def process(self, input: T) -> ProcessedResult[T]: ...
```

### ABC vs Protocol
| | `ABC` | `Protocol` |
|---|---|---|
| Satisfaction | Explicit (`class Foo(MyABC)`) | Structural (implicit) |
| Runtime check | `isinstance` works | Only with `@runtime_checkable` |
| Use when | You control all implementations | You don't (third-party, legacy) |
| Analog to | Java interfaces | Go interfaces / TypeScript interfaces |

**Prefer `Protocol` for the Go mental model. Use `ABC` only when you own all implementors
and want to enforce implementation at runtime.**
