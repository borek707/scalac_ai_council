from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from council.llm.cost_tracker import CostTracker
from council.llm.provider import LLMProvider, LLMResponse
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
        await mock_provider.generate(
            "test", temperature=0.5, max_tokens=500
        )
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

        @retry_with_backoff(max_retries=2, base_delay=0.01, max_delay=1.0, exceptions=(RuntimeError,))
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

        monkeypatch.setattr(
            KimiCodeProvider, "_detect_executable", staticmethod(lambda: None)
        )
        monkeypatch.delenv("KIMI_CLI_PATH", raising=False)

        with pytest.raises(RuntimeError, match="Kimi Code CLI binary not found"):
            KimiCodeProvider()
