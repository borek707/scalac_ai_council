from __future__ import annotations

import os
from pathlib import Path

from council.config.env_loader import load_dotenv_file, load_dotenv_from_cwd


class TestLoadDotenvFile:
    def test_loads_quoted_and_unquoted_values(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.delenv("DOTENV_ALPHA", raising=False)
        monkeypatch.delenv("DOTENV_BETA", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text(
            '# comment\nDOTENV_ALPHA="hello"\nDOTENV_BETA=world\n',
            encoding="utf-8",
        )

        load_dotenv_file(env_file)

        assert os.environ["DOTENV_ALPHA"] == "hello"
        assert os.environ["DOTENV_BETA"] == "world"

    def test_does_not_override_existing_env(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.setenv("DOTENV_KEEP", "original")
        env_file = tmp_path / ".env"
        env_file.write_text("DOTENV_KEEP=replaced\n", encoding="utf-8")

        load_dotenv_file(env_file)

        assert os.environ["DOTENV_KEEP"] == "original"

    def test_missing_file_is_noop(self, tmp_path: Path) -> None:
        load_dotenv_file(tmp_path / "missing.env")

    def test_skips_malformed_lines(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.delenv("DOTENV_OK", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text("\nnoequals\nDOTENV_OK=1\n", encoding="utf-8")

        load_dotenv_file(env_file)

        assert os.environ["DOTENV_OK"] == "1"


class TestLoadDotenvFromCwd:
    def test_loads_dotenv_from_current_directory(self, tmp_path: Path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("DOTENV_CWD", raising=False)
        (tmp_path / ".env").write_text("DOTENV_CWD=loaded\n", encoding="utf-8")

        load_dotenv_from_cwd()

        assert os.environ["DOTENV_CWD"] == "loaded"
