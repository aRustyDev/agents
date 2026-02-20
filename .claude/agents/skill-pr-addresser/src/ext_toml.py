"""TOML configuration extension for Cement.

Allows using TOML files for configuration instead of INI files.
"""

from pathlib import Path
from typing import Any

import toml
from cement.ext.ext_configparser import ConfigParserConfigHandler


class TomlConfigHandler(ConfigParserConfigHandler):
    """Config handler that reads TOML files.

    Extends the default ConfigParser handler to support TOML format.
    """

    class Meta:
        label = "toml"

    def _parse_file(self, file_path: str) -> dict[str, Any]:
        """Parse a TOML file into a dictionary.

        Args:
            file_path: Path to the TOML file

        Returns:
            Dictionary with configuration values
        """
        path = Path(file_path).expanduser()
        if not path.exists():
            return {}

        with open(path) as f:
            return toml.load(f)

    def parse_file(self, file_path: str) -> bool:
        """Parse a TOML file and merge into configuration.

        Args:
            file_path: Path to the TOML file

        Returns:
            True if file was parsed, False otherwise
        """
        path = Path(file_path).expanduser()

        if not path.exists():
            return False

        try:
            data = self._parse_file(str(path))
            self.merge(data)
            return True
        except toml.TomlDecodeError as e:
            self.app.log.warning(f"Failed to parse TOML config {file_path}: {e}")
            return False


def load(app):
    """Load the TOML extension.

    Args:
        app: The Cement application instance
    """
    app.handler.register(TomlConfigHandler)
