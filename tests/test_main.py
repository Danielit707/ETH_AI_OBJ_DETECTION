"""Tests for the desktop UI (main.py)."""

import sys
from unittest.mock import MagicMock, patch


class TestMainModule:
    def _import_main(self):
        """Import main.py with customtkinter mocked."""
        mock_ctk = MagicMock()
        with patch.dict(sys.modules, {"customtkinter": mock_ctk}):
            if "main" in sys.modules:
                del sys.modules["main"]
            import main
            return main

    def test_main_imports_successfully(self):
        """Verify main.py can be imported without errors."""
        mod = self._import_main()
        assert hasattr(mod, "API_URL")

    def test_api_url_default(self):
        """Default API URL should be localhost:8000."""
        mod = self._import_main()
        assert mod.API_URL == "http://127.0.0.1:8000"

    def test_api_url_from_env(self, monkeypatch):
        """API URL should be configurable via environment variable."""
        monkeypatch.setenv("DETECTION_API_URL", "http://192.168.1.100:9000")
        mod = self._import_main()
        assert mod.API_URL == "http://192.168.1.100:9000"
