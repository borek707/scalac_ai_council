from __future__ import annotations

"""Tests for council.interactive — provider screen logic, API key modal,
provider constants, and prompt_for_args entry point."""

import argparse
from unittest.mock import MagicMock, patch

import pytest
from textual.widgets import Input, OptionList

from council.interactive import (
    _PROVIDERS,
    ApiKeyModal,
    CouncilMenuApp,
    ProviderScreen,
    prompt_for_args,
)
from council.llm.secrets import KEY_REQUIRED_PROVIDERS

# ── TestProvidersList ────────────────────────────────────────────────────────


class TestProvidersList:
    """Tests for the _PROVIDERS constant."""

    def test_providers_has_six_entries(self) -> None:
        """_PROVIDERS has exactly 6 entries (no duplicate openrouter)."""
        assert len(_PROVIDERS) == 6

    def test_no_duplicate_provider_keys(self) -> None:
        """All provider keys in _PROVIDERS are unique."""
        keys = [key for key, _name, _model in _PROVIDERS]
        assert len(keys) == len(set(keys))

    def test_openrouter_uses_claude_35_sonnet(self) -> None:
        """OpenRouter default model is anthropic/claude-3-5-sonnet-20241022."""
        openrouter = next((p for p in _PROVIDERS if p[0] == "openrouter"), None)
        assert openrouter is not None
        assert openrouter[2] == "anthropic/claude-3-5-sonnet-20241022"

    def test_provider_keys(self) -> None:
        """All expected provider keys are present."""
        keys = {key for key, _name, _model in _PROVIDERS}
        expected = {"openai", "anthropic", "openrouter", "ollama", "kimi-code", "claude-code"}
        assert keys == expected


# ── TestNoApiKeyProviders ────────────────────────────────────────────────────


class TestNoApiKeyProviders:
    """Tests that local providers don't require a key in the flow."""

    def test_no_key_providers_set(self) -> None:
        """_KEY_REQUIRED_PROVIDERS contains exactly openai, anthropic, openrouter."""
        assert {"openai", "anthropic", "openrouter"} == KEY_REQUIRED_PROVIDERS

    def test_ollama_not_in_key_required(self) -> None:
        assert "ollama" not in KEY_REQUIRED_PROVIDERS

    def test_kimi_code_not_in_key_required(self) -> None:
        assert "kimi-code" not in KEY_REQUIRED_PROVIDERS

    def test_claude_code_not_in_key_required(self) -> None:
        assert "claude-code" not in KEY_REQUIRED_PROVIDERS


# ── TestApiKeyModal ──────────────────────────────────────────────────────────


class TestApiKeyModal:
    """Tests for ApiKeyModal._submit() dismiss behaviour."""

    async def test_modal_submit_with_key(self) -> None:
        """_submit() dismisses with the stripped key value."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            # Push the modal manually
            dismissed_values: list[str | None] = []

            def _capture(value: str | None) -> None:
                dismissed_values.append(value)

            await pilot.app.push_screen(ApiKeyModal("openai"), _capture)
            await pilot.pause()

            # The modal is now the active screen — query via it
            modal = pilot.app.screen
            modal_input = modal.query_one("#modal-key-input", Input)
            modal_input.value = "  sk-test-key  "
            await pilot.pause()

            # Trigger _submit via the OK button
            await pilot.click("#modal-ok")
            await pilot.pause()

            assert dismissed_values == ["sk-test-key"]

    async def test_modal_submit_empty_key_dismisses_none(self) -> None:
        """_submit() with blank input dismisses with None."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            dismissed_values: list[str | None] = []

            def _capture(value: str | None) -> None:
                dismissed_values.append(value)

            await pilot.app.push_screen(ApiKeyModal("anthropic"), _capture)
            await pilot.pause()

            modal = pilot.app.screen
            modal_input = modal.query_one("#modal-key-input", Input)
            modal_input.value = ""
            await pilot.pause()

            await pilot.click("#modal-ok")
            await pilot.pause()

            assert dismissed_values == [None]

    async def test_modal_submit_whitespace_key_dismisses_none(self) -> None:
        """_submit() with whitespace-only input dismisses with None."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            dismissed_values: list[str | None] = []

            def _capture(value: str | None) -> None:
                dismissed_values.append(value)

            await pilot.app.push_screen(ApiKeyModal("openrouter"), _capture)
            await pilot.pause()

            modal = pilot.app.screen
            modal_input = modal.query_one("#modal-key-input", Input)
            modal_input.value = "   "
            await pilot.pause()

            await pilot.click("#modal-ok")
            await pilot.pause()

            assert dismissed_values == [None]


# ── TestProviderScreenState ──────────────────────────────────────────────────


class TestProviderScreenState:
    """Tests for ProviderScreen._go_next() logic."""

    async def test_valid_state_pushes_brief_screen(self) -> None:
        """When state has valid provider and inputs are filled, _go_next pushes 'brief' screen."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = pilot.app.screen
            assert isinstance(screen, ProviderScreen)

            # Set a non-key-requiring provider (index 3 = ollama)
            ol = screen.query_one(OptionList)
            ol.highlighted = 3
            pilot.app.state["api_key"] = None

            # Ensure rounds has a valid value
            rounds_input = screen.query_one("#rounds-input", Input)
            rounds_input.value = "3"

            screen._go_next()
            await pilot.pause()

            # Should have navigated to brief screen
            assert pilot.app.state.get("provider") == "ollama"
            assert pilot.app.state.get("rounds") == 3

    async def test_invalid_rounds_shows_notification(self) -> None:
        """Non-integer rounds triggers self.notify(...) and does not push 'brief' screen."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = pilot.app.screen
            assert isinstance(screen, ProviderScreen)

            ol = screen.query_one(OptionList)
            ol.highlighted = 3  # ollama — no API key required

            rounds_input = screen.query_one("#rounds-input", Input)
            rounds_input.value = "abc"

            initial_stack_depth = len(pilot.app.screen_stack)

            # Patch notify to capture calls
            notifications: list[str] = []

            def mock_notify(msg: str, **kwargs: object) -> None:
                notifications.append(msg)

            screen.notify = mock_notify  # type: ignore[method-assign]
            screen._go_next()
            await pilot.pause()

            # Stack should not have grown (no new screen pushed)
            assert len(pilot.app.screen_stack) == initial_stack_depth
            assert len(notifications) == 1
            assert "1 and 20" in notifications[0]

    async def test_rounds_out_of_range_shows_notification(self) -> None:
        """rounds=0 or rounds=21 triggers notification."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = pilot.app.screen
            assert isinstance(screen, ProviderScreen)

            rounds_input = screen.query_one("#rounds-input", Input)

            notifications: list[str] = []

            def mock_notify(msg: str, **kwargs: object) -> None:
                notifications.append(msg)

            screen.notify = mock_notify  # type: ignore[method-assign]

            # Test rounds=0
            rounds_input.value = "0"
            screen._go_next()
            await pilot.pause()
            assert len(notifications) == 1

            # Test rounds=21
            rounds_input.value = "21"
            screen._go_next()
            await pilot.pause()
            assert len(notifications) == 2

    async def test_valid_rounds_stored_as_int(self) -> None:
        """String '5' in rounds-input stores as int 5 in state."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = pilot.app.screen
            assert isinstance(screen, ProviderScreen)

            ol = screen.query_one(OptionList)
            ol.highlighted = 3  # ollama — no key required
            pilot.app.state["api_key"] = None

            rounds_input = screen.query_one("#rounds-input", Input)
            rounds_input.value = "5"

            screen._go_next()
            await pilot.pause()

            assert pilot.app.state.get("rounds") == 5
            assert isinstance(pilot.app.state.get("rounds"), int)

    async def test_empty_model_stored_as_none(self) -> None:
        """Blank model-input stores None in state['model']."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = pilot.app.screen
            assert isinstance(screen, ProviderScreen)

            ol = screen.query_one(OptionList)
            ol.highlighted = 3  # ollama
            pilot.app.state["api_key"] = None

            model_input = screen.query_one("#model-input", Input)
            model_input.value = ""

            rounds_input = screen.query_one("#rounds-input", Input)
            rounds_input.value = "3"

            screen._go_next()
            await pilot.pause()

            assert pilot.app.state.get("model") is None

    async def test_empty_output_falls_back_to_default(self) -> None:
        """Blank output-input stores './output' in state['output']."""
        app = CouncilMenuApp(start_screen="provider")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = pilot.app.screen
            assert isinstance(screen, ProviderScreen)

            ol = screen.query_one(OptionList)
            ol.highlighted = 3  # ollama
            pilot.app.state["api_key"] = None

            rounds_input = screen.query_one("#rounds-input", Input)
            rounds_input.value = "3"

            output_input = screen.query_one("#output-input", Input)
            output_input.value = ""

            screen._go_next()
            await pilot.pause()

            assert pilot.app.state.get("output") == "./output"


# ── TestPromptForArgs ────────────────────────────────────────────────────────


class TestPromptForArgs:
    """Tests for the prompt_for_args public entry point."""

    def test_prompt_for_args_exits_zero_when_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When app.run() returns None, prompt_for_args calls sys.exit(0)."""
        mock_app = MagicMock()
        mock_app.run.return_value = None

        with patch("council.interactive.CouncilMenuApp", return_value=mock_app):
            with patch("council.interactive._is_onboarding_done", return_value=True):
                with pytest.raises(SystemExit) as exc_info:
                    prompt_for_args()

        assert exc_info.value.code == 0

    def test_prompt_for_args_returns_namespace(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When app.run() returns a Namespace, prompt_for_args returns it."""
        ns = argparse.Namespace(provider="ollama", rounds=3)
        mock_app = MagicMock()
        mock_app.run.return_value = ns

        with patch("council.interactive.CouncilMenuApp", return_value=mock_app):
            with patch("council.interactive._is_onboarding_done", return_value=True):
                result = prompt_for_args()

        assert result is ns
        assert result.provider == "ollama"
