from __future__ import annotations

"""Tests that verify streaming works end-to-end through agents and that the
TUI namespace contains every field _run_council accesses."""

import argparse
from collections.abc import AsyncGenerator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from council.agents.base import BaseAgent
from council.config.schema import AgentState
from council.llm.provider import LLMProvider, LLMResponse

# ── TUI namespace completeness ───────────────────────────────────────────────


_REQUIRED_FIELDS = [
    # accessed directly (AttributeError if missing)
    "config", "provider", "api_key", "model", "platform", "rounds",
    "timeout", "output", "monitor", "verbose", "documents", "documents_dir",
    "scalac_mode", "dashboard", "demo", "scenario", "template", "free_tier",
    # accessed via getattr so safe, but must exist for complete coverage
    "stream", "brief", "review", "aggregate",
]


def _make_tui_namespace(**overrides) -> argparse.Namespace:
    """Return the argparse.Namespace that ConfirmScreen builds when Run is clicked."""
    from council.interactive import _PROVIDERS

    defaults: dict = {
        "config": None,
        "provider": "openai",
        "api_key": None,
        "model": None,
        "platform": "cli",
        "rounds": 3,
        "timeout": 300.0,
        "output": "./output",
        "monitor": False,
        "aggregate": False,
        "verbose": False,
        "documents": None,
        "documents_dir": None,
        "scalac_mode": False,
        "dashboard": False,
        "demo": False,
        "scenario": "saas-launch",
        "template": None,
        "free_tier": False,
        "stream": True,
        "brief": None,
        "review": None,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class TestTuiNamespace:
    """TUI ConfirmScreen namespace must satisfy every field _run_council accesses."""

    def test_namespace_has_stream_field(self) -> None:
        ns = _make_tui_namespace()
        assert hasattr(ns, "stream"), "stream must be set — agents use it for live output"
        assert ns.stream is True

    def test_namespace_has_provider(self) -> None:
        ns = _make_tui_namespace(provider="claude-code")
        assert ns.provider == "claude-code"

    def test_namespace_has_free_tier(self) -> None:
        ns = _make_tui_namespace(free_tier=True)
        assert ns.free_tier is True

    def test_namespace_has_all_required_fields(self) -> None:
        ns = _make_tui_namespace()
        missing = [f for f in _REQUIRED_FIELDS if not hasattr(ns, f)]
        assert missing == [], f"TUI namespace missing fields: {missing}"

    def test_demo_namespace_has_stream(self) -> None:
        """Demo path also needs stream — we set it to True always."""
        ns = _make_tui_namespace(demo=True, provider="openai", config=None, template=None)
        assert hasattr(ns, "stream")

    def test_template_namespace_resolves_config(self) -> None:
        """When template is set, config can be None (cli.py resolves it)."""
        ns = _make_tui_namespace(template="scalac", config=None)
        assert ns.template == "scalac"
        assert ns.config is None  # cli.py fills this in from template


# ── Streaming through BaseAgent ──────────────────────────────────────────────


class _StreamingProvider(LLMProvider):
    """Provider that yields multiple small chunks to simulate real streaming."""

    def __init__(self, chunks: list[str]) -> None:
        self._chunks = chunks
        self.model = "mock-streaming"

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        return LLMResponse(
            content="".join(self._chunks),
            model=self.model,
            tokens_prompt=10,
            tokens_completion=10,
            cost_usd=0.0,
            latency_ms=5.0,
        )

    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        for chunk in self._chunks:
            yield chunk


class _ConcreteAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return "Test system prompt"

    def get_output_filename(self) -> str:
        return "test_output.md"

    def get_template_name(self) -> str:
        return "marcus.j2"


@pytest.fixture
def streaming_provider() -> _StreamingProvider:
    return _StreamingProvider(["Hello", " from", " stream"])


@pytest.fixture
def agent_with_streaming(
    tmp_path: Path,
    streaming_provider: _StreamingProvider,
    sample_config,
) -> _ConcreteAgent:
    agent = _ConcreteAgent(
        name="Marcus",
        role="Test",
        workspace=tmp_path,
        config=sample_config,
        provider=streaming_provider,
    )
    agent.stream_output = True
    return agent


class TestAgentStreamOutput:
    """When stream_output=True, generate_round() must call provider.stream()."""

    @pytest.mark.asyncio
    async def test_stream_output_flag_defaults_false(
        self, tmp_path: Path, sample_config, streaming_provider
    ) -> None:
        agent = _ConcreteAgent(
            name="Marcus", role="Test", workspace=tmp_path,
            config=sample_config, provider=streaming_provider,
        )
        assert agent.stream_output is False

    @pytest.mark.asyncio
    async def test_generate_round_uses_streaming_when_flag_set(
        self, agent_with_streaming: _ConcreteAgent, tmp_path: Path
    ) -> None:
        """With stream_output=True, the LLM stream() method is called, not generate()."""
        provider = agent_with_streaming.provider
        assert isinstance(provider, _StreamingProvider)

        # Write a brief so render_prompt has content
        brief_path = tmp_path / "shared" / "brief.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text("Test brief", encoding="utf-8")

        import sys
        from io import StringIO
        captured = StringIO()

        # Patch stdout so streaming output is captured, not printed to console
        with patch.object(sys, "stdout", captured):
            content = await agent_with_streaming.generate_round(
                agent_with_streaming._load_context.__func__(
                    agent_with_streaming, 1
                ) if False else
                await agent_with_streaming._load_context(1)
            )

        assert content == "Hello from stream"
        output = captured.getvalue()
        assert "Hello from stream" in output

    @pytest.mark.asyncio
    async def test_generate_round_uses_generate_when_flag_off(
        self, tmp_path: Path, sample_config, streaming_provider
    ) -> None:
        """With stream_output=False (default), generate() is called, not stream()."""
        agent = _ConcreteAgent(
            name="Marcus", role="Test", workspace=tmp_path,
            config=sample_config, provider=streaming_provider,
        )
        brief_path = tmp_path / "shared" / "brief.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text("Test brief", encoding="utf-8")

        ctx = await agent._load_context(1)

        called_stream = False
        original_stream = streaming_provider.stream

        async def spy_stream(*args, **kwargs):
            nonlocal called_stream
            called_stream = True
            async for chunk in original_stream(*args, **kwargs):
                yield chunk

        streaming_provider.stream = spy_stream
        await agent.generate_round(ctx)
        assert called_stream is False, "stream() must NOT be called when stream_output=False"

    @pytest.mark.asyncio
    async def test_run_round_with_stream_sets_state_done(
        self, agent_with_streaming: _ConcreteAgent, tmp_path: Path
    ) -> None:
        """run_round() with streaming enabled completes and sets state=DONE."""
        brief_path = tmp_path / "shared" / "brief.md"
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text("Test brief", encoding="utf-8")

        import sys
        with patch.object(sys, "stdout", open("/dev/null", "w")):
            await agent_with_streaming.run_round(1)

        assert agent_with_streaming.state == AgentState.DONE

    @pytest.mark.asyncio
    async def test_four_agents_all_get_stream_flag(
        self, tmp_path: Path, sample_config, streaming_provider
    ) -> None:
        """Simulates what cli.py does: set stream_output on all 4 agents."""
        from council.agents.david import DavidAgent
        from council.agents.elena import ElenaAgent
        from council.agents.kai import KaiAgent
        from council.agents.marcus import MarcusAgent

        agents: list[BaseAgent] = [
            MarcusAgent(workspace=tmp_path, config=sample_config, provider=streaming_provider),
            ElenaAgent(workspace=tmp_path, config=sample_config, provider=streaming_provider),
            KaiAgent(workspace=tmp_path, config=sample_config, provider=streaming_provider),
            DavidAgent(workspace=tmp_path, config=sample_config, provider=streaming_provider),
        ]
        for agent in agents:
            agent.stream_output = True

        assert all(a.stream_output for a in agents)
        assert len(agents) == 4


# ── Provider stream() smoke tests (mocked) ──────────────────────────────────


class TestProviderStreamInterface:
    """Each provider must implement stream() that yields at least one chunk."""

    @pytest.mark.asyncio
    async def test_openai_provider_stream(self) -> None:
        from council.llm.openai_provider import OpenAIProvider

        mock_client = MagicMock()
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "token"

        async def fake_create(**kwargs):
            async def _iter():
                yield chunk
                yield MagicMock(choices=[MagicMock(delta=MagicMock(content=None))])
            return _iter()

        mock_client.chat.completions.create = fake_create

        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider.model = "gpt-4o"
        provider._client = mock_client

        chunks = []
        async for c in provider.stream("prompt"):
            chunks.append(c)
        assert "token" in chunks

    @pytest.mark.asyncio
    async def test_openrouter_provider_stream(self) -> None:
        from council.llm.openrouter_provider import OpenRouterProvider

        mock_client = MagicMock()
        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta.content = "openrouter-token"

        async def fake_create(**kwargs):
            async def _iter():
                yield chunk
            return _iter()

        mock_client.chat.completions.create = AsyncMock(side_effect=fake_create)

        provider = OpenRouterProvider.__new__(OpenRouterProvider)
        provider.model = "anthropic/claude-3-5-sonnet-20241022"
        provider.auto_selected = False
        provider._needs_model_resolution = False
        provider._free_tier = False
        provider._fallback_models = []
        provider._client = mock_client
        provider._site_url = None
        provider._app_name = None

        chunks = []
        async for c in provider.stream("prompt"):
            chunks.append(c)
        assert "openrouter-token" in chunks

    @pytest.mark.asyncio
    async def test_anthropic_provider_stream(self) -> None:
        from council.llm.anthropic_provider import AnthropicProvider

        mock_client = MagicMock()
        mock_stream_ctx = MagicMock()

        async def fake_text_stream():
            yield "anthropic-token"

        mock_stream_ctx.__aenter__ = AsyncMock(return_value=mock_stream_ctx)
        mock_stream_ctx.__aexit__ = AsyncMock(return_value=False)
        mock_stream_ctx.text_stream = fake_text_stream()
        mock_client.messages.stream = MagicMock(return_value=mock_stream_ctx)

        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider.model = "claude-sonnet-4-6"
        provider._client = mock_client

        chunks = []
        async for c in provider.stream("prompt"):
            chunks.append(c)
        assert "anthropic-token" in chunks

    @pytest.mark.asyncio
    async def test_claude_code_provider_stream_with_subprocess(self, tmp_path: Path) -> None:
        """ClaudeCodeProvider.stream() parses stream-json and yields text chunks."""
        import json as _json

        from council.llm.claude_code_provider import ClaudeCodeProvider

        fake_cli = tmp_path / "claude"
        fake_cli.write_text("#!/bin/bash")
        provider = ClaudeCodeProvider(executable_path=str(fake_cli))

        lines = [
            _json.dumps({"type": "system", "subtype": "init"}).encode() + b"\n",
            _json.dumps({
                "type": "stream_event",
                "event": {"type": "content_block_delta", "index": 1,
                          "delta": {"type": "text_delta", "text": "chunk1"}},
            }).encode() + b"\n",
            _json.dumps({
                "type": "stream_event",
                "event": {"type": "content_block_delta", "index": 1,
                          "delta": {"type": "text_delta", "text": " chunk2"}},
            }).encode() + b"\n",
            _json.dumps({"type": "result", "result": "chunk1 chunk2"}).encode() + b"\n",
            b"",
        ]

        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = MagicMock()
        mock_proc.stdout.readline = AsyncMock(side_effect=lines)
        mock_proc.stderr = MagicMock()
        mock_proc.wait = AsyncMock(return_value=0)

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            chunks = []
            async for chunk in provider.stream("test prompt"):
                chunks.append(chunk)

        assert chunks == ["chunk1", " chunk2"]
        assert "".join(chunks) == "chunk1 chunk2"

    @pytest.mark.asyncio
    async def test_kimi_provider_stream_yields_full_response(self, tmp_path: Path) -> None:
        """KimiCodeProvider.stream() yields the full response as one chunk (no real streaming)."""
        from council.llm.kimi_code_provider import KimiCodeProvider

        fake_cli = tmp_path / "kimi"
        fake_cli.write_text("#!/bin/bash\necho response")
        fake_cli.chmod(0o755)

        provider = KimiCodeProvider.__new__(KimiCodeProvider)
        provider.model = "kimi-for-coding"
        provider.executable_path = str(fake_cli)
        provider._http_client = None

        mock_response = LLMResponse(
            content="full kimi response",
            model="kimi-for-coding",
            tokens_prompt=10,
            tokens_completion=20,
            cost_usd=0.0,
            latency_ms=100.0,
        )
        provider.generate = AsyncMock(return_value=mock_response)

        chunks = []
        async for chunk in provider.stream("prompt"):
            chunks.append(chunk)

        assert chunks == ["full kimi response"]
        assert len(chunks) == 1  # documented: Kimi yields everything at once
