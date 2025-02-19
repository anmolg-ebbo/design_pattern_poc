# Design Patterns for Backend Systems

## Singleton Pattern

**What it is**: Ensures a class has only one instance and provides a global point of access to it.

### Key Characteristics:

- Private constructor
- Static instance holder
- Thread-safety considerations
- Global access point

### Where to Use:

- Database connection pools
- Configuration managers
- Logging services
- Cache managers
- Thread pools

## Repository Pattern

**What it is**: Mediates between the domain and data mapping layers, acting like an in-memory collection of domain objects.

### Key Characteristics:

- Abstracts data access logic
- Domain-focused interface
- Decouples business logic from data access
- Simplifies testing via mocking

### Where to Use:

- Data access layer
- API integration layers
- Microservice boundaries
- Legacy system integration
- Cross-database operations

## Builder Pattern

**What it is**: Separates the construction of complex objects from their representation.

### Key Characteristics:

- Step-by-step construction
- Fluent interface (method chaining)
- Director class (optional)
- Immutable objects creation

### Where to Use:

- Complex object creation
- API request/response builders
- Query builders
- Configuration objects
- Test data generation

## Factory Pattern

**What it is**: Creates objects without exposing instantiation logic to the client.

### Key Characteristics:

- Centralizes object creation
- Defers instantiation to subclasses (Factory Method)
- Creates families of related objects (Abstract Factory)
- Hides concrete class implementation details

### Where to Use:

- Data access objects (DAOs)
- Service providers
- Plugin architectures
- Multi-tenant applications
- Strategy implementations

## Adapter Pattern

**What it is**: Converts the interface of a class into another interface clients expect.

### Key Characteristics:

- Interface translation
- Legacy code integration
- Class adaptation (inheritance) or object adaptation (composition)
- No modification to existing code

### Where to Use:

- Third-party API integration
- Legacy system modernization
- Microservice communication
- Data format conversion
- Testing frameworks
