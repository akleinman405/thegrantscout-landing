"""
Cross-platform path utilities for TheGrantScout.
Works on both Windows and macOS.
"""
import os
from pathlib import Path


def get_project_root():
    """Get TheGrantScout project root directory."""
    # Try common locations
    candidates = [
        Path.home() / "Documents" / "TheGrantScout",  # macOS
        Path.home() / "TheGrantScout",                 # macOS/Linux alternative
        Path("C:/TheGrantScout"),                      # Windows
        Path("/mnt/c/TheGrantScout"),                  # WSL
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError("TheGrantScout project directory not found")


def get_db_host():
    """Get database host based on environment."""
    # WSL uses bridged network, native uses localhost
    if os.path.exists("/mnt/c"):
        return "172.26.16.1"  # WSL
    return "localhost"        # macOS/Windows native


def get_db_config():
    """Get full database configuration."""
    return {
        'host': get_db_host(),
        'port': 5432,
        'database': 'thegrantscout',
        'user': 'postgres',
    }


def get_credentials_password():
    """Read database password from credentials file."""
    creds_file = get_project_root() / "1. Database" / "Postgresql Info.txt"
    if not creds_file.exists():
        raise FileNotFoundError(f"Credentials file not found: {creds_file}")

    with open(creds_file, 'r') as f:
        content = f.read()
        # Parse password - typically on its own line or after "Password:"
        for line in content.split('\n'):
            line = line.strip()
            if line.lower().startswith('password'):
                # Handle "Password: xxx" or "Password=xxx" format
                if ':' in line:
                    return line.split(':', 1)[1].strip()
                elif '=' in line:
                    return line.split('=', 1)[1].strip()
            elif line and not any(x in line.lower() for x in ['host', 'port', 'user', 'database']):
                # If it's a non-empty line that's not another config, might be the password
                continue

    raise ValueError("Could not parse password from credentials file")


# Convenience paths (lazy-loaded to avoid errors on import)
_project_root = None

def _get_cached_root():
    global _project_root
    if _project_root is None:
        _project_root = get_project_root()
    return _project_root


@property
def PROJECT_ROOT():
    return _get_cached_root()


# Common subdirectories
def get_database_dir():
    return _get_cached_root() / "1. Database"


def get_credentials_file():
    return get_database_dir() / "Postgresql Info.txt"


def get_embeddings_dir():
    return get_database_dir() / "4. Semantic Embeddings"


def get_reports_dir():
    return _get_cached_root() / "5. Reports"


def get_admin_dir():
    return _get_cached_root() / "6. Admin"


# For backward compatibility, expose as module-level when script is run directly
if __name__ == "__main__":
    print(f"Project root: {get_project_root()}")
    print(f"Database host: {get_db_host()}")
    print(f"Database dir: {get_database_dir()}")
    print(f"Credentials file: {get_credentials_file()}")
