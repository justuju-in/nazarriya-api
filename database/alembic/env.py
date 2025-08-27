from logging.config import fileConfig
from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool
from alembic import context
import os
import sys

# Add the server directory to the Python path
# Get the database directory (where this env.py file is located)
database_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory (nazarriya-api)
parent_dir = os.path.dirname(database_dir)
# Add the parent directory to Python path so we can import from server
sys.path.insert(0, parent_dir)

# Import models after setting up the path
try:
    from server.database import Base
    # We don't need to import specific models for manual migrations
except ImportError as e:
    print(f"Error importing models: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    raise

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    try:
        fileConfig(config.config_file_name)
    except Exception as e:
        # If logging config fails, set up basic logging to avoid format strings in output
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s: %(message)s'
        )

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Check if we're running in Docker (use environment variable)
    docker_db_url = os.getenv("DATABASE_URL")
    if docker_db_url:
        url = docker_db_url
    else:
        url = config.get_main_option("sqlalchemy.url")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Check if we're running in Docker (use environment variable)
    docker_db_url = os.getenv("DATABASE_URL")
    if docker_db_url:
        # Use the Docker database URL from environment
        url = docker_db_url
        print(f"Using Docker database URL: {url.replace(os.getenv('POSTGRES_PASSWORD', ''), '***')}")
    else:
        # Fall back to config file URL
        url = config.get_main_option("sqlalchemy.url")
        
        # Add password from environment variable if available
        pgpassword = os.getenv("POSTGRES_PASSWORD")
        if pgpassword:
            # Insert password into the URL
            if "://postgres@" in url:
                url = url.replace("://postgres@", f"://postgres:{pgpassword}@")
        
        print(f"Using config file database URL: {url.replace(pgpassword, '***') if pgpassword else url}")
    
    # Suppress alembic logging output to avoid format strings
    import logging
    alembic_logger = logging.getLogger('alembic')
    alembic_logger.setLevel(logging.WARNING)
    
    # Create engine with the resolved URL
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
