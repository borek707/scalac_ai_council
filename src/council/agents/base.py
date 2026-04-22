from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from jinja2 import Environment, FileSystemLoader, Template

if TYPE_CHECKING:
    from council.config.documents import AgentContext, Document
    from council.config.schema import AgentState, CompanyConfig, LLMProvider, RoundContext

logger: logging.Logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """DRY abstract base for all marketing council agents.

    Each agent specialises in one domain (offers, funnels, copy, ABM)
    and produces structured markdown output across debate rounds.
    Concrete agents override three abstract hooks; everything else
    (file I/O, LLM invocation, round lifecycle) is handled here.
    """

    def __init__(
        self,
        name: str,
        role: str,
        workspace: Path,
        config: CompanyConfig,
        provider: LLMProvider,
        documents: Optional[List[Document]] = None,
    ) -> None:
        self.name: str = name
        self.role: str = role
        self.workspace: Path = workspace
        self.config: CompanyConfig = config
        self.provider: LLMProvider = provider
        self.documents: List[Document] = documents or []

        self.discussion_dir: Path = self.workspace / "shared" / "discussion"
        self.output_dir: Path = self.workspace / "output"
        self.brief_path: Path = self.workspace / "shared" / "brief.md"

        self.state: AgentState  # set by orchestrator via import below
        from council.config.schema import AgentState as _AgentState

        self.state = _AgentState.PENDING

        # Jinja2 environment for agent-specific templates
        template_dir: Path = Path(__file__).parent / "templates"
        self._jinja: Environment = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        self._ensure_dirs()

    # ── File I/O helpers ──────────────────────────────────────────────────

    def _ensure_dirs(self) -> None:
        """Create required workspace directories if missing."""
        self.discussion_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def read_discussion(self) -> str:
        """Read the full shared discussion log.

        Aggregates all existing round files in round order.
        Returns empty string if nothing has been written yet.
        """
        if not self.discussion_dir.exists():
            return ""

        lines: list[str] = []
        for round_file in sorted(self.discussion_dir.glob("round_*.md")):
            try:
                lines.append(round_file.read_text(encoding="utf-8"))
            except OSError:
                continue
        return "\n\n".join(lines)

    def read_brief(self) -> str:
        """Read the marketing brief file.

        Returns empty string if brief has not been written yet.
        """
        if not self.brief_path.exists():
            return ""
        return self.brief_path.read_text(encoding="utf-8")

    def write_round(self, round_num: int, content: str) -> Path:
        """Write agent output for a specific round.

        File naming convention: ``{name}_round_{round_num}.md``
        inside the shared discussion directory.
        """
        filename: str = f"{self.name.lower()}_round_{round_num}.md"
        path: Path = self.discussion_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info("%s wrote round %d → %s", self.name, round_num, path)
        return path

    def write_final(self, content: str, filename: str) -> Path:
        """Write final consolidated output to the output directory.

        Parameters
        ----------
        content: Markdown content to persist.
        filename: Target file name (e.g. ``marcus_offer.md``).

        Returns
        -------
        Path to the written file.
        """
        path: Path = self.output_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info("%s wrote final → %s", self.name, path)
        return path

    # ── Prompt generation (Jinja2) ────────────────────────────────────────

    def _load_template(self) -> Template:
        """Load the Jinja2 template declared by :meth:`get_template_name`."""
        return self._jinja.get_template(self.get_template_name())

    def render_prompt(self, ctx: RoundContext) -> str:
        """Render the agent prompt from its Jinja2 template.

        The template receives a ``company`` variable built from
        :attr:`config`, a ``ctx`` variable with full round context,
        and ``documents`` with any loaded markdown files.
        """
        template: Template = self._load_template()
        company_dict: dict[str, object] = self.config.model_dump()
        ctx_dict: dict[str, object] = {
            "round_num": ctx.round_num,
            "brief": ctx.brief,
            "discussion_history": ctx.discussion_history,
            "battlecards": ctx.battlecards,
            "content_plan": ctx.content_plan,
            "target_accounts": ctx.target_accounts,
        }
        # Build document context
        doc_fragment: str = ""
        if self.documents:
            from council.config.documents import AgentContext
            agent_ctx = AgentContext(company=self.config, documents=self.documents)
            doc_fragment = agent_ctx.to_prompt_fragment()
        return template.render(
            company=company_dict,
            ctx=ctx_dict,
            agent_name=self.name,
            agent_role=self.role,
            documents=doc_fragment,
        )

    # ── LLM-powered generation ────────────────────────────────────────────

    async def generate_round(self, ctx: RoundContext) -> str:
        """Generate round content via LLM using the agent's template.

        Override for custom behaviour (e.g. multi-shot prompting,
        structured JSON output, etc.).
        """
        prompt: str = self.render_prompt(ctx)
        system_prompt: str = self.get_system_prompt()
        response = await self.provider.generate(
            prompt=prompt,
            system=system_prompt,
            temperature=0.7,
            max_tokens=4000,
        )
        return response.content

    async def _load_context(self, round_num: int) -> RoundContext:
        """Assemble the :class:`RoundContext` for *round_num*.

        Reads brief and discussion history from disk; enriches with
        optional artifacts (battlecards, content_plan, target_accounts)
        when they exist in the workspace.
        """
        from council.config.schema import RoundContext as _RoundContext

        brief: str = self.read_brief()
        history: str = self.read_discussion()

        battlecards: str = self._read_optional_artifact("battlecards.md")
        content_plan: str = self._read_optional_artifact("content_plan.md")
        target_accounts: str = self._read_optional_artifact("target_accounts.md")

        return _RoundContext(
            round_num=round_num,
            brief=brief,
            discussion_history=history,
            company_config=self.config,
            battlecards=battlecards,
            content_plan=content_plan,
            target_accounts=target_accounts,
        )

    def _read_optional_artifact(self, filename: str) -> str:
        """Read an optional shared artifact; return empty string if absent."""
        path: Path = self.workspace / "shared" / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    # ── Round lifecycle ───────────────────────────────────────────────────

    async def run_round(self, round_num: int) -> Path:
        """Execute a full round: load context → generate → write.

        Updates :attr:`state` for observability.
        """
        from council.config.schema import AgentState as _AgentState

        self.state = _AgentState.WRITING
        try:
            ctx: RoundContext = await self._load_context(round_num)
            content: str = await self.generate_round(ctx)
            path: Path = self.write_round(round_num, content)
            self.state = _AgentState.DONE
            return path
        except Exception:
            self.state = _AgentState.ERROR
            raise

    async def run_final(self) -> Path:
        """Generate and persist the agent's final consolidated output.

        Loads full discussion history, uses the agent's template
        (usually a "final synthesis" section) to produce one
        canonical artifact.
        """
        ctx: RoundContext = await self._load_context(round_num=0)
        # Build a synthetic final prompt by appending a synthesis directive
        final_prompt: str = self.render_prompt(ctx)
        final_prompt += (
            "\n\n--- FINAL SYNTHESIS ---\n"
            "Based on the full discussion history above, produce your FINAL consolidated output.\n"
            "This should be a complete, polished markdown document ready for the client.\n"
            "Do not reference rounds or discussion — write as a single authoritative deliverable.\n"
        )
        system_prompt: str = self.get_system_prompt()
        response = await self.provider.generate(
            prompt=final_prompt,
            system=system_prompt,
            temperature=0.5,  # lower temp for final polish
            max_tokens=6000,
        )
        return self.write_final(response.content, self.get_output_filename())

    # ── Abstract hooks for concrete agents ────────────────────────────────

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt that defines the agent's identity,
        expertise, and behavioural constraints."""
        ...

    @abstractmethod
    def get_output_filename(self) -> str:
        """Return the file name for the agent's final output
        (e.g. ``marcus_offer.md``)."""
        ...

    @abstractmethod
    def get_template_name(self) -> str:
        """Return the Jinja2 template file name for this agent
        (e.g. ``marcus.j2``)."""
        ...
