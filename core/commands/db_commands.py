"""
Database management command for creating databases and running migrations.

This command handles database creation and Alembic migrations based on
the application's .env configuration.
"""
import os
import subprocess
import typer
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from core.bases.base_command import BaseCommand
from core.config import settings


class DbInitCommand(BaseCommand):
    def execute(
        self,
        create_db: bool = typer.Option(
            True,
            "--create-db/--no-create-db",
            help="Create database if it doesn't exist"
        ),
        run_migrations: bool = typer.Option(
            True,
            "--migrate/--no-migrate",
            help="Run Alembic migrations after creating database"
        ),
        upgrade_head: bool = typer.Option(
            True,
            "--upgrade/--no-upgrade",
            help="Upgrade to latest migration"
        ),
    ):
        """
        Initialize database: create DB and run migrations.
        
        Examples:
            python cli.py db-init
            python cli.py db-init --no-create-db
            python cli.py db-init --no-migrate
        """
        print("🔧 Database Initialization")
        print("=" * 50)
        
        if create_db:
            self._create_database()
        
        if run_migrations:
            self._run_migrations(upgrade_head)
        
        print("\n✅ Database initialization complete!")
    
    def _create_database(self):
        """Create the database if it doesn't exist."""
        print("\n📦 Creating database...")
        
        # Parse database URL to get database name
        db_url = settings.DATABASE_URI
        
        # Handle PostgreSQL
        if "postgresql" in db_url:
            self._create_postgresql_database(db_url)
        # Handle MySQL
        elif "mysql" in db_url:
            self._create_mysql_database(db_url)
        # Handle SQLite
        elif "sqlite" in db_url:
            self._create_sqlite_database(db_url)
        else:
            print(f"⚠️  Unsupported database type: {db_url}")
            return
    
    def _create_postgresql_database(self, db_url: str):
        """Create PostgreSQL database."""
        # Extract database name and connection URL
        # Format: postgresql://user:pass@host:port/dbname
        parts = db_url.split("/")
        db_name = parts[-1].split("?")[0]  # Remove query params
        base_url = "/".join(parts[:-1]) + "/postgres"  # Connect to default DB
        
        try:
            # Connect to default postgres database
            engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
            
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                )
                exists = result.fetchone() is not None
                
                if exists:
                    print(f"   ℹ️  Database '{db_name}' already exists")
                else:
                    # Create database
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"   ✅ Created database '{db_name}'")
            
            engine.dispose()
            
        except OperationalError as e:
            print(f"   ❌ Failed to create PostgreSQL database: {e}")
            raise typer.Exit(1)
    
    def _create_mysql_database(self, db_url: str):
        """Create MySQL database."""
        # Extract database name and connection URL
        # Format: mysql://user:pass@host:port/dbname
        parts = db_url.split("/")
        db_name = parts[-1].split("?")[0]
        base_url = "/".join(parts[:-1])  # Connect without database
        
        try:
            engine = create_engine(base_url)
            
            with engine.connect() as conn:
                # Check if database exists
                result = conn.execute(
                    text(f"SHOW DATABASES LIKE '{db_name}'")
                )
                exists = result.fetchone() is not None
                
                if exists:
                    print(f"   ℹ️  Database '{db_name}' already exists")
                else:
                    # Create database
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"   ✅ Created database '{db_name}'")
            
            engine.dispose()
            
        except OperationalError as e:
            print(f"   ❌ Failed to create MySQL database: {e}")
            raise typer.Exit(1)
    
    def _create_sqlite_database(self, db_url: str):
        """Create SQLite database."""
        # Extract file path from URL
        # Format: sqlite:///path/to/db.db
        db_path = db_url.replace("sqlite:///", "")
        
        if os.path.exists(db_path):
            print(f"   ℹ️  SQLite database already exists: {db_path}")
        else:
            # Create directory if needed
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
            
            # SQLite creates the file automatically on first connection
            engine = create_engine(db_url)
            engine.dispose()
            print(f"   ✅ Created SQLite database: {db_path}")
    
    def _run_migrations(self, upgrade: bool = True):
        """Run Alembic migrations."""
        print("\n🔄 Running migrations...")
        
        try:
            # Check if alembic is initialized
            if not os.path.exists("alembic.ini"):
                print("   ⚠️  Alembic not initialized. Run 'alembic init migrations' first")
                return
            
            if upgrade:
                # Run migrations
                result = subprocess.run(
                    ["alembic", "upgrade", "head"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    print("   ✅ Migrations applied successfully")
                    if result.stdout:
                        print(f"   {result.stdout}")
                else:
                    print(f"   ❌ Migration failed: {result.stderr}")
                    raise typer.Exit(1)
            else:
                print("   ℹ️  Skipping migration upgrade")
                
        except FileNotFoundError:
            print("   ❌ Alembic not found. Install it with: pip install alembic")
            raise typer.Exit(1)


class DbMigrateCommand(BaseCommand):
    def execute(
        self,
        message: str = typer.Argument(..., help="Migration message"),
        autogenerate: bool = typer.Option(
            True,
            "--autogenerate/--no-autogenerate",
            help="Auto-generate migration from models"
        ),
    ):
        """
        Create a new migration.
        
        Examples:
            python cli.py db-migrate "Add user table"
            python cli.py db-migrate "Update schema" --no-autogenerate
        """
        print(f"📝 Creating migration: {message}")
        
        try:
            cmd = ["alembic", "revision"]
            
            if autogenerate:
                cmd.append("--autogenerate")
            
            cmd.extend(["-m", message])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Migration created successfully")
                print(result.stdout)
            else:
                print(f"❌ Failed to create migration: {result.stderr}")
                raise typer.Exit(1)
                
        except FileNotFoundError:
            print("❌ Alembic not found. Install it with: pip install alembic")
            raise typer.Exit(1)


class DbUpgradeCommand(BaseCommand):
    def execute(
        self,
        revision: str = typer.Argument("head", help="Revision to upgrade to"),
    ):
        """
        Upgrade database to a specific revision.
        
        Examples:
            python cli.py db-upgrade
            python cli.py db-upgrade head
            python cli.py db-upgrade +1
        """
        print(f"⬆️  Upgrading database to: {revision}")
        
        try:
            result = subprocess.run(
                ["alembic", "upgrade", revision],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Database upgraded successfully")
                print(result.stdout)
            else:
                print(f"❌ Upgrade failed: {result.stderr}")
                raise typer.Exit(1)
                
        except FileNotFoundError:
            print("❌ Alembic not found. Install it with: pip install alembic")
            raise typer.Exit(1)


class DbDowngradeCommand(BaseCommand):
    def execute(
        self,
        revision: str = typer.Argument("-1", help="Revision to downgrade to"),
    ):
        """
        Downgrade database to a specific revision.
        
        Examples:
            python cli.py db-downgrade -1
            python cli.py db-downgrade base
        """
        print(f"⬇️  Downgrading database to: {revision}")
        
        try:
            result = subprocess.run(
                ["alembic", "downgrade", revision],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Database downgraded successfully")
                print(result.stdout)
            else:
                print(f"❌ Downgrade failed: {result.stderr}")
                raise typer.Exit(1)
                
        except FileNotFoundError:
            print("❌ Alembic not found. Install it with: pip install alembic")
            raise typer.Exit(1)
