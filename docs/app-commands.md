# App-Specific Commands

The framework automatically discovers and registers commands from individual apps, allowing each app to define its own CLI commands.

## How It Works

The CLI automatically scans the `APPS_DIR` (configured in `.env`) for command files in each app's `commands/` directory.

**Directory Structure:**

```
<APPS_DIR>/
├── driver/
│   └── commands/
│       ├── __init__.py
│       └── new_driver.py
├── passenger/
│   └── commands/
│       ├── __init__.py
│       └── create_passenger.py
└── ...
```

## Creating a Command

1. **Create a commands directory** in your app:

   ```
   <APPS_DIR>/<your_app>/commands/
   ```

2. **Create a command file** (e.g., `new_driver.py`):

   ```python
   from core.bases.base_command import BaseCommand

   class NewDriverCommand(BaseCommand):
       def execute(self, name: str, age: int = 25):
           """Create a new driver."""
           print(f"🚗 Creating new driver: {name}, age: {age}")
           print(f"✅ Driver '{name}' created successfully!")
   ```

3. **The command is automatically registered** when you run `cli.py`:
   - Command name is auto-generated from the class name
   - `NewDriverCommand` becomes `new-driver`
   - Arguments are automatically parsed from the `execute` method signature

## Usage

```bash
# List all commands (including auto-discovered ones)
python cli.py --help

# Run your app-specific command
python cli.py new-driver "John Doe"
python cli.py new-driver "Jane Smith" --age 30
```

## Configuration

Set the `APPS_DIR` in your `.env` file:

```env
# Relative to project root
APPS_DIR=apps

# Or absolute path
APPS_DIR=/path/to/your/apps
```

## Command Naming Convention

- Class name: `NewDriverCommand` → CLI command: `new-driver`
- Class name: `CreatePassengerCommand` → CLI command: `create-passenger`
- Class name: `ListUsersCommand` → CLI command: `list-users`

## Tips

- Each command file can contain multiple command classes
- All classes inheriting from `BaseCommand` will be registered
- Use type hints in `execute()` for automatic argument parsing
- Use `typer.Option()` for optional arguments with defaults
- Commands are discovered at CLI startup
