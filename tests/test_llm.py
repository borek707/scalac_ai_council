from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council.llm.anthropic_provider import AnthropicProvider
from council.llm.cost_tracker import CostTracker
from council.llm.ollama_provider import OllamaProvider
from council.llm.provider import LLMResponse
from council.llm.retry import retry_with_backoff


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_defaults(self) -> None:
        resp = LLMResponse(content="hello", model="gpt-4")
        assert resp.content == "hello"
        assert resp.model == "gpt-4"
        assert resp.tokens_prompt == 0
        assert resp.tokens_completion == 0
        assert resp.cost_usd == 0.0
        assert resp.latency_ms == 0.0

    def test_full_values(self) -> None:
        resp = LLMResponse(
            content="test",
            model="claude-3",
            tokens_prompt=100,
            tokens_completion=50,
            cost_usd=0.002,
            latency_ms=150.0,
        )
        assert resp.tokens_prompt == 100
        assert resp.tokens_completion == 50
        assert resp.cost_usd == 0.002
        assert resp.latency_ms == 150.0


class TestMockLLMProvider:
    """Tests for MockLLMProvider fixture."""

    @pytest.mark.asyncio
    async def test_generate(self, mock_provider: Any) -> None:
        response = await mock_provider.generate("test prompt")
        assert "Mock response" in response.content
        assert response.model == "mock-model"
        assert response.tokens_completion == 100
        assert response.cost_usd > 0

    @pytest.mark.asyncio
    async def test_generate_tracks_calls(self, mock_provider: Any) -> None:
        await mock_provider.generate("prompt 1")
        await mock_provider.generate("prompt 2")
        assert len(mock_provider.calls) == 2
        assert mock_provider.calls[0]["prompt"] == "prompt 1"
        assert mock_provider.calls[1]["prompt"] == "prompt 2"

    @pytest.mark.asyncio
    async def test_generate_increments_cost(self, mock_provider: Any) -> None:
        resp1 = await mock_provider.generate("p1")
        resp2 = await mock_provider.generate("p2")
        assert resp1.cost_usd < resp2.cost_usd

    @pytest.mark.asyncio
    async def test_stream(self, mock_provider: Any) -> None:
        chunks: list[str] = []
        async for chunk in mock_provider.stream("test"):
            chunks.append(chunk)
        assert chunks == ["Mock response"]

    @pytest.mark.asyncio
    async def test_failing_provider(self, failing_provider: Any) -> None:
        with pytest.raises(RuntimeError):
            await failing_provider.generate("test")

    @pytest.mark.asyncio
    async def test_provider_with_delay(self) -> None:
        from tests.conftest import MockLLMProvider

        provider = MockLLMProvider(response_text="delayed", delay=0.1)
        start = asyncio.get_event_loop().time()
        resp = await provider.generate("test")
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed >= 0.09
        assert resp.content == "delayed (call #1)"

    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_provider: Any) -> None:
        await mock_provider.generate("test", system="You are a helpful assistant.")
        assert mock_provider.calls[0]["system"] == "You are a helpful assistant."

    @pytest.mark.asyncio
    async def test_generate_with_custom_model(self, mock_provider: Any) -> None:
        resp = await mock_provider.generate("test", model="custom-model")
        assert resp.model == "custom-model"

    @pytest.mark.asyncio
    async def test_generate_with_params(self, mock_provider: Any) -> None:
        await mock_provider.generate("test", temperature=0.5, max_tokens=500)
        assert mock_provider.calls[0]["temperature"] == 0.5
        assert mock_provider.calls[0]["max_tokens"] == 500


class TestCostTracker:
    """Tests for CostTracker."""

    def test_add_entry(self) -> None:
        tracker = CostTracker()
        resp = LLMResponse(content="test", model="gpt-4", cost_usd=0.002)
        tracker.add("marcus", 1, resp)
        assert tracker.get_total() == 0.002

    def test_add_multiple(self) -> None:
        tracker = CostTracker()
        tracker.add("marcus", 1, LLMResponse(content="a", model="m", cost_usd=0.001))
        tracker.add("elena", 1, LLMResponse(content="b", model="m", cost_usd=0.002))
        assert tracker.get_total() == 0.003

    def test_get_by_agent(self) -> None:
        tracker = CostTracker()
        tracker.add("marcus", 1, LLMResponse(content="a", model="m", cost_usd=0.005))
        tracker.add("marcus", 2, LLMResponse(content="b", model="m", cost_usd=0.003))
        tracker.add("elena", 1, LLMResponse(content="c", model="m", cost_usd=0.002))
        assert tracker.get_by_agent("marcus") == 0.008
        assert tracker.get_by_agent("elena") == 0.002
        assert tracker.get_by_agent("unknown") == 0.0

    def test_get_by_round(self) -> None:
        tracker = CostTracker()
        tracker.add("marcus", 1, LLMResponse(content="a", model="m", cost_usd=0.001))
        tracker.add("elena", 1, LLMResponse(content="b", model="m", cost_usd=0.002))
        tracker.add("marcus", 2, LLMResponse(content="c", model="m", cost_usd=0.003))
        assert tracker.get_by_round(1) == 0.003
        assert tracker.get_by_round(2) == 0.003

    def test_report(self) -> None:
        tracker = CostTracker()
        tracker.add("marcus", 1, LLMResponse(content="a", model="m", cost_usd=0.001))
        report = tracker.report()
        assert "Cost Report" in report
        assert "marcus" in report
        assert "$0.001000" in report

    def test_empty_tracker(self) -> None:
        tracker = CostTracker()
        assert tracker.get_total() == 0.0
        assert tracker.report() is not None
        assert tracker.get_entries() == []

    def test_get_entries(self) -> None:
        tracker = CostTracker()
        tracker.add("a", 1, LLMResponse(content="x", model="m", cost_usd=0.1))
        entries = tracker.get_entries()
        assert len(entries) == 1
        assert entries[0]["agent"] == "a"
        assert entries[0]["cost_usd"] == 0.1


class TestRetryWithBackoff:
    """Tests for retry_with_backoff decorator."""

    @pytest.mark.asyncio
    async def test_success_no_retry(self) -> None:
        call_count = 0

        @retry_with_backoff(max_retries=3, exceptions=(RuntimeError,))
        async def success_func() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = await success_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_then_success(self) -> None:
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01, exceptions=(RuntimeError,))
        async def flaky_func() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RuntimeError("fail")
            return "success"

        result = await flaky_func()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_exhausted(self) -> None:
        call_count = 0

        @retry_with_backoff(max_retries=2, base_delay=0.01, exceptions=(RuntimeError,))
        async def always_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise RuntimeError(f"fail #{call_count}")

        with pytest.raises(RuntimeError):
            await always_fail()
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_unexpected_exception(self) -> None:
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01, exceptions=(ValueError,))
        async def raise_runtime() -> str:
            nonlocal call_count
            call_count += 1
            raise RuntimeError("wrong type")

        with pytest.raises(RuntimeError):
            await raise_runtime()
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_specific_exception(self) -> None:
        call_count = 0

        @retry_with_backoff(max_retries=3, base_delay=0.01, exceptions=(ValueError,))
        async def raise_value() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("fail")
            return "success"

        result = await raise_value()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_delay_increases(self) -> None:
        delays: list[float] = []

        @retry_with_backoff(
            max_retries=2, base_delay=0.01, max_delay=1.0, exceptions=(RuntimeError,)
        )
        async def timing_fail() -> str:
            raise RuntimeError("fail")

        start = asyncio.get_event_loop().time()
        try:
            await timing_fail()
        except RuntimeError:
            pass
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed >= 0.01  # At least one delay

    def test_retry_config_defaults(self) -> None:
        from council.llm.retry import RetryConfig

        config = RetryConfig()
        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0

    def test_retry_config_custom(self) -> None:
        from council.llm.retry import RetryConfig

        config = RetryConfig(max_retries=5, base_delay=2.0, max_delay=30.0)
        assert config.max_retries == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0


class TestKimiCodeProvider:
    """Tests for KimiCodeProvider."""

    def test_clean_output_removes_session_trailer(self) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        raw = "Hello world\n\nTo resume this session: kimi -r abc-123"
        assert KimiCodeProvider._clean_output(raw) == "Hello world"

    def test_clean_output_no_trailer(self) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        assert KimiCodeProvider._clean_output("Just text") == "Just text"

    @pytest.fixture
    def fake_kimi(self, tmp_path: Path) -> Path:
        """Create a fake kimi executable for testing."""
        fake = tmp_path / "kimi"
        fake.write_text("#!/bin/bash\necho 'fake'", encoding="utf-8")
        fake.chmod(0o755)
        return fake

    def test_build_cmd_basic(self, fake_kimi: Path) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi))
        cmd = provider._build_cmd("Say hi")
        assert cmd[0] == str(fake_kimi)
        assert "--quiet" in cmd
        assert "--yolo" in cmd
        assert "--prompt" in cmd
        idx = cmd.index("--prompt")
        assert cmd[idx + 1] == "Say hi"

    def test_build_cmd_with_system(self, fake_kimi: Path) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi))
        cmd = provider._build_cmd("Say hi", system="Be polite")
        idx = cmd.index("--prompt")
        prompt = cmd[idx + 1]
        assert "[System Instruction]" in prompt
        assert "Be polite" in prompt
        assert "Say hi" in prompt

    def test_build_cmd_with_work_dir(self, fake_kimi: Path) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi), work_dir="/tmp")
        cmd = provider._build_cmd("test")
        assert "--work-dir" in cmd
        assert cmd[cmd.index("--work-dir") + 1] == "/tmp"

    @pytest.mark.asyncio
    async def test_generate_success(self, monkeypatch: Any, fake_kimi: Path) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi))

        class FakeProc:
            returncode = 0

            async def communicate(self) -> tuple[bytes, bytes]:
                return (
                    b"Hello from Kimi\n\nTo resume this session: kimi -r x",
                    b"",
                )

        async def fake_exec(*args: Any, **kwargs: Any) -> FakeProc:
            return FakeProc()

        monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)

        resp = await provider.generate("Say hi")
        assert resp.content == "Hello from Kimi"
        assert resp.model == "kimi-for-coding"

    @pytest.mark.asyncio
    async def test_generate_failure(self, monkeypatch: Any, fake_kimi: Path) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi))

        class FakeProc:
            returncode = 1

            async def communicate(self) -> tuple[bytes, bytes]:
                return (b"", b"CLI error")

        async def fake_exec(*args: Any, **kwargs: Any) -> FakeProc:
            return FakeProc()

        monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)

        with pytest.raises(RuntimeError, match="Kimi CLI failed"):
            await provider.generate("Say hi")

    @pytest.mark.asyncio
    async def test_stream_yields_content(self, monkeypatch: Any, fake_kimi: Path) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi))

        class FakeProc:
            returncode = 0

            async def communicate(self) -> tuple[bytes, bytes]:
                return (b"Streamed text\nTo resume this session: kimi -r y", b"")

        async def fake_exec(*args: Any, **kwargs: Any) -> FakeProc:
            return FakeProc()

        monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)

        chunks: list[str] = []
        async for chunk in provider.stream("Say hi"):
            chunks.append(chunk)
        assert chunks == ["Streamed text"]

    def test_missing_executable_raises(self, monkeypatch: Any) -> None:
        from council.llm.kimi_code_provider import KimiCodeProvider

        monkeypatch.setattr(KimiCodeProvider, "_detect_executable", staticmethod(lambda: None))
        monkeypatch.delenv("KIMI_CLI_PATH", raising=False)

        with pytest.raises(RuntimeError, match="Kimi Code CLI binary not found"):
            KimiCodeProvider()

    @pytest.mark.asyncio
    async def test_prompt_not_in_debug_log(
        self, monkeypatch: Any, fake_kimi: Any, caplog: pytest.LogCaptureFixture
    ) -> None:
        """The full prompt text must NOT appear in debug logs; <prompt:Nchars> MUST."""
        from council.llm.kimi_code_provider import KimiCodeProvider

        provider = KimiCodeProvider(executable_path=str(fake_kimi))
        long_prompt = "A" * 200  # distinct long prompt

        class FakeProc:
            returncode = 0

            async def communicate(self) -> tuple[bytes, bytes]:
                return (b"response text", b"")

        async def fake_exec(*args: Any, **kwargs: Any) -> FakeProc:
            return FakeProc()

        monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)

        with caplog.at_level(logging.DEBUG, logger="council.llm.kimi_code_provider"):
            await provider.generate(long_prompt)

        assert long_prompt not in caplog.text
        assert "<prompt:" in caplog.text


class TestOpenAIProvider:
    """Tests for OpenAIProvider — issues #2 and #20."""

    def test_missing_api_key_raises(self, monkeypatch: Any) -> None:
        """RuntimeError with 'OpenAI API key missing' when env var absent and no explicit key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        from council.llm.openai_provider import OpenAIProvider

        with pytest.raises(RuntimeError, match="OpenAI API key missing"):
            OpenAIProvider()

    def test_explicit_api_key_bypasses_env(self, monkeypatch: Any) -> None:
        """Explicit api_key='sk-test' skips env-var requirement — no RuntimeError raised."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with patch("council.llm.openai_provider.openai") as mock_openai:
            mock_openai.AsyncOpenAI.return_value = MagicMock()
            mock_openai.AuthenticationError = Exception
            mock_openai.PermissionDeniedError = Exception
            mock_openai.NotFoundError = Exception
            mock_openai.BadRequestError = Exception
            from council.llm.openai_provider import OpenAIProvider

            provider = OpenAIProvider(api_key="sk-test")
        assert provider.api_key == "sk-test"

    @pytest.mark.asyncio
    async def test_auth_error_not_retried(self, monkeypatch: Any) -> None:
        """openai.AuthenticationError must cause immediate failure after exactly 1 attempt."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-fake")

        import openai as real_openai

        call_count = 0

        async def raise_auth(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            # Build a minimal AuthenticationError compatible with the openai SDK
            response = MagicMock()
            response.status_code = 401
            response.headers = {}
            response.text = "Unauthorized"
            body = {"error": {"message": "Invalid API key", "type": "invalid_request_error"}}
            raise real_openai.AuthenticationError(
                message="Invalid API key",
                response=response,
                body=body,
            )

        with patch("council.llm.openai_provider.openai") as mock_openai:
            mock_openai.AuthenticationError = real_openai.AuthenticationError
            mock_openai.PermissionDeniedError = real_openai.PermissionDeniedError
            mock_openai.NotFoundError = real_openai.NotFoundError
            mock_openai.BadRequestError = real_openai.BadRequestError

            mock_client = MagicMock()
            mock_client.chat = MagicMock()
            mock_client.chat.completions = MagicMock()
            mock_client.chat.completions.create = raise_auth
            mock_openai.AsyncOpenAI.return_value = mock_client

            from council.llm.openai_provider import OpenAIProvider

            provider = OpenAIProvider(api_key="sk-fake")

        with pytest.raises(real_openai.AuthenticationError):
            await provider.generate("test prompt")

        assert call_count == 1, f"Expected 1 attempt, got {call_count}"


class TestOpenRouterProvider:
    """Tests for OpenRouterProvider."""

    def _make_provider(self, monkeypatch: Any, **kwargs: Any) -> Any:
        """Helper: set a fake API key then construct OpenRouterProvider.

        The openai.AsyncOpenAI client is patched out so no real network
        calls are made during construction.
        """
        from unittest.mock import MagicMock, patch

        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-abc")
        # Prevent the free-tier model fetch from hitting the network
        monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)

        with patch("council.llm.openai_provider.openai") as mock_openai:
            mock_openai.AsyncOpenAI.return_value = MagicMock()
            from council.llm.openrouter_provider import OpenRouterProvider

            return OpenRouterProvider(**kwargs)

    # 1. Happy-path initialisation with OPENROUTER_API_KEY set
    def test_init_with_env_api_key(self, monkeypatch: Any) -> None:
        provider = self._make_provider(monkeypatch)
        assert provider is not None
        assert provider.api_key == "test-key-abc"

    # 2. Correct default base URL
    def test_default_base_url(self, monkeypatch: Any) -> None:
        provider = self._make_provider(monkeypatch)
        assert provider.base_url == "https://openrouter.ai/api/v1"

    # 3. RuntimeError raised when OPENROUTER_API_KEY is missing and no api_key passed
    def test_missing_api_key_raises(self, monkeypatch: Any) -> None:
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        from council.llm.openrouter_provider import OpenRouterProvider

        with pytest.raises(RuntimeError, match="OpenRouter API key missing"):
            OpenRouterProvider()

    # 3b. OPENAI_API_KEY set but OPENROUTER_API_KEY absent — must not fall back (issue #16)
    def test_does_not_fall_back_to_openai_api_key(self, monkeypatch: Any) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-should-not-be-used")
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        from council.llm.openrouter_provider import OpenRouterProvider

        with pytest.raises(RuntimeError, match="OpenRouter API key missing"):
            OpenRouterProvider()

    # 3d. Explicit api_key argument bypasses env-var requirement
    def test_explicit_api_key_bypasses_env(self, monkeypatch: Any) -> None:
        from unittest.mock import MagicMock, patch

        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)

        with patch("council.llm.openai_provider.openai") as mock_openai:
            mock_openai.AsyncOpenAI.return_value = MagicMock()
            from council.llm.openrouter_provider import OpenRouterProvider

            provider = OpenRouterProvider(api_key="explicit-key")
        assert provider.api_key == "explicit-key"

    # 4. Correct inheritance from OpenAIProvider
    def test_inherits_from_openai_provider(self, monkeypatch: Any) -> None:
        from council.llm.openai_provider import OpenAIProvider

        provider = self._make_provider(monkeypatch)
        assert isinstance(provider, OpenAIProvider)

    # 5. model=None is forwarded as-is — issue #14 fix
    #    When free_tier=False and model is not passed (None), the provider
    #    assigns a default model name instead of keeping None.  The fix for
    #    issue #14 ensures that an *explicit* non-None, non-"default" model
    #    value is forwarded unchanged to super().__init__.
    def test_explicit_model_forwarded_unchanged(self, monkeypatch: Any) -> None:
        provider = self._make_provider(monkeypatch, model="openai/gpt-4o")
        assert provider.model == "openai/gpt-4o"

    def test_explicit_model_not_replaced_with_default(self, monkeypatch: Any) -> None:
        provider = self._make_provider(monkeypatch, model="meta-llama/llama-3-70b")
        # Must NOT be silently swapped for the built-in fallback
        assert provider.model == "meta-llama/llama-3-70b"
        assert provider.model != "anthropic/claude-3-5-sonnet-20241022"

    # 5b. model=None (omitted) results in the built-in default, not None
    def test_model_none_resolves_to_default(self, monkeypatch: Any) -> None:
        provider = self._make_provider(monkeypatch, model=None)
        # The constructor must not leave self.model as None
        assert provider.model is not None
        assert provider.model == "anthropic/claude-3-5-sonnet-20241022"

    # 5c. model="default" is treated the same as model=None
    def test_model_default_string_resolves_to_fallback(self, monkeypatch: Any) -> None:
        provider = self._make_provider(monkeypatch, model="default")
        assert provider.model == "anthropic/claude-3-5-sonnet-20241022"


class TestAnthropicProvider:
    """Tests for AnthropicProvider."""

    def test_missing_api_key_raises(self, monkeypatch: Any) -> None:
        """RuntimeError raised when key absent."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="Anthropic API key missing"):
            AnthropicProvider()

    def test_explicit_api_key_bypasses_env(self, monkeypatch: Any) -> None:
        """Explicit api_key takes precedence; ANTHROPIC_API_KEY env not needed."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        # AnthropicProvider creates an AsyncAnthropic client in __init__ — patch it
        with patch("council.llm.anthropic_provider.anthropic") as mock_anthropic:
            mock_anthropic.AsyncAnthropic.return_value = MagicMock()
            mock_anthropic.AuthenticationError = Exception
            mock_anthropic.PermissionDeniedError = Exception
            mock_anthropic.NotFoundError = Exception
            mock_anthropic.BadRequestError = Exception
            provider = AnthropicProvider(api_key="ant-test-key")
            assert provider.api_key == "ant-test-key"

    @pytest.mark.asyncio
    async def test_auth_error_not_retried(self, monkeypatch: Any) -> None:
        """AuthenticationError is not retried (non-retryable exception)."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "ant-fake")

        import anthropic as real_anthropic

        call_count = 0

        async def raise_auth(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            raise real_anthropic.AuthenticationError(
                message="Invalid API key",
                response=MagicMock(status_code=401, headers={}, text="Unauthorized"),
                body={"error": {"message": "Invalid API key"}},
            )

        with patch("council.llm.anthropic_provider.anthropic") as mock_anthropic:
            mock_anthropic.AuthenticationError = real_anthropic.AuthenticationError
            mock_anthropic.PermissionDeniedError = real_anthropic.PermissionDeniedError
            mock_anthropic.NotFoundError = real_anthropic.NotFoundError
            mock_anthropic.BadRequestError = real_anthropic.BadRequestError
            client = MagicMock()
            client.messages.create = raise_auth
            mock_anthropic.AsyncAnthropic.return_value = client
            provider = AnthropicProvider(api_key="bad-key")

        with pytest.raises(real_anthropic.AuthenticationError):
            await provider.generate(prompt="test")

        assert call_count == 1, f"Expected 1 attempt, got {call_count}"


class TestOllamaProvider:
    """Tests for OllamaProvider."""

    def test_missing_aiohttp_raises_import_error(self, monkeypatch: Any) -> None:
        """ImportError raised when aiohttp is not installed."""
        with patch("council.llm.ollama_provider.aiohttp", None):
            with pytest.raises(ImportError, match="aiohttp"):
                OllamaProvider()

    @pytest.mark.asyncio
    async def test_generate_returns_response(self) -> None:
        """generate() returns LLMResponse with content from Ollama API."""
        # Mock aiohttp.ClientSession using MagicMock for the sync context manager
        # and AsyncMock for the async one (session.post).
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "response": "Hello from Ollama",
                "eval_count": 10,
                "prompt_eval_count": 5,
            }
        )
        mock_response.raise_for_status = MagicMock()

        # session.post(...) is used as `async with session.post(...) as response:`
        # so post() must return a synchronous object with __aenter__/__aexit__
        post_ctx = MagicMock()
        post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        post_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post.return_value = post_ctx

        with patch("council.llm.ollama_provider.aiohttp") as mock_aiohttp:
            mock_aiohttp.ClientSession.return_value = mock_session
            provider = OllamaProvider()
            response = await provider.generate(prompt="test")
        assert response.content == "Hello from Ollama"
        assert response.tokens_completion == 10

    @pytest.mark.asyncio
    async def test_4xx_raises_deterministic_error(self) -> None:
        """HTTP 400/404 raises a non-retryable error immediately."""
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="model not found")

        post_ctx = MagicMock()
        post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
        post_ctx.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)
        mock_session.post.return_value = post_ctx

        with patch("council.llm.ollama_provider.aiohttp") as mock_aiohttp:
            mock_aiohttp.ClientSession.return_value = mock_session
            provider = OllamaProvider()
            with pytest.raises(Exception, match="[Oo]llama.*404|404.*[Oo]llama"):
                await provider.generate(prompt="test")
