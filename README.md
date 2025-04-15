# Repogen: Clean Architecture .NET Repository & UnitOfWork Generator

Repogen is a Python-based CLI tool that automatically generates repository and unit of work classes following Clean Architecture principles for .NET projects. It streamlines the creation of boilerplate code for data access layers, saving development time and ensuring consistency across your codebase.

## Features

- **Automatic Repository Generation**: Creates repository interfaces and implementations for all entity classes
- **Unit of Work Pattern**: Generates Unit of Work interface and implementation
- **Generic Repository**: Creates a generic repository and interface for common CRUD operations
- **Clean Architecture Compliance**: Follows Clean Architecture principles with proper separation of concerns
- **Project Structure Detection**: Automatically detects your project context and entity classes
- **Dry Run Mode**: Preview generated files without writing to disk

## Prerequisites

- Python 3.6 or higher
- A .NET project following a standard Clean Architecture structure

## Installation

Clone this repository or download the source code:

```bash
git clone https://github.com/yourusername/repogen.git
cd repogen
```

## Project Structure Requirements

Repogen expects your .NET solution to follow this structure:

```
YourProject/
├── YourProject.Domain/
│   └── Entity/
│       ├── User.cs
│       ├── Product.cs
│       └── ...
└── YourProject.Infrastructure/
    └── Context/
        └── AppDbContext.cs (or any other DbContext)
```

The tool will create the following folders if they don't exist:

```
YourProject/
└── YourProject.Infrastructure/
    ├── Abstractions/       # Repository interfaces
    ├── Repositories/       # Repository implementations
    └── Base/               # Generic repository and unit of work
```

## Usage

Run the script from the command line:

```bash
python repogen.py --path /path/to/your/project [options]
```

### Command Line Arguments

| Argument | Description |
|----------|-------------|
| `--path` | (Required) Path to your project root directory |
| `--dry-run` | Preview generated files without writing to disk |
| `--verbose` | Enable detailed debug logging |

### Examples

Generate repositories for a project:

```bash
python repogen.py --path C:/Projects/MyProject
```

Preview what would be generated without writing files:

```bash
python repogen.py --path C:/Projects/MyProject --dry-run
```

With verbose logging:

```bash
python repogen.py --path C:/Projects/MyProject --verbose
```

## Generated Files

### Repository Pattern

For each entity in your Domain/Entity folder, Repogen generates:

1. An interface in the Abstractions folder:
   - `IUserRepository.cs`
   - `IProductRepository.cs`
   - etc.

2. An implementation in the Repositories folder:
   - `UserRepository.cs`
   - `ProductRepository.cs`
   - etc.

### Unit of Work Pattern

In the Base folder:
- `IUnitOfWork.cs`: Interface with properties for all repositories
- `UnitOfWork.cs`: Implementation of the Unit of Work pattern

### Generic Repository

In the Base folder:
- `IRepository.cs`: Generic repository interface with CRUD operations
- `Repository.cs`: Generic repository implementation

## Customization

Template files are stored in the `templates/templates.py` file. You can modify these templates to suit your specific needs.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.