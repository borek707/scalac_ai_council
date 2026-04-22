from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Single loaded document (markdown, text, etc.) for agent context.

    Attributes:
        name: Human-readable name (filename without extension).
        path: Absolute path to the source file.
        content: Raw text content.
        doc_type: Category — ``brief``, ``case_study``, ``research``,
            ``competitor_intel``, ``strategy``, or ``generic``.
    """

    name: str
    path: Path
    content: str
    doc_type: str = "generic"


class DocumentLoader:
    """Load markdown/text documents into agent context.

    Scans a directory (or list of files) and returns a list of
    :class:`Document` objects that agents can inject into their prompts.

    Usage::

        loader = DocumentLoader()
        docs = loader.load_directory("./docs/")          # all .md/.txt
        docs = loader.load_files(["brief.md", "cs1.md"]) # specific files
        docs = loader.load_scalac_bundle()               # built-in Scalac

    Agents access documents via :meth:`BaseAgent.read_documents`.
    """

    SUPPORTED_EXTENSIONS: frozenset[str] = frozenset({".md", ".txt", ".rst"})

    def __init__(self, max_size_bytes: int = 500_000) -> None:
        self.max_size_bytes = max_size_bytes

    # ── Public API ──────────────────────────────────────────────────────────

    def load_directory(
        self,
        directory: Path | str,
        doc_type: str = "generic",
    ) -> List[Document]:
        """Load every supported file inside *directory* (recursive)."""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            logger.warning("Document directory not found: %s", dir_path)
            return []

        documents: List[Document] = []
        for ext in self.SUPPORTED_EXTENSIONS:
            for file_path in dir_path.rglob(f"*{ext}"):
                doc = self._load_file(file_path, doc_type)
                if doc:
                    documents.append(doc)

        logger.info(
            "Loaded %d documents from %s", len(documents), dir_path
        )
        return documents

    def load_files(
        self,
        files: List[Path | str],
        doc_type: str = "generic",
    ) -> List[Document]:
        """Load an explicit list of file paths."""
        documents: List[Document] = []
        for f in files:
            doc = self._load_file(Path(f), doc_type)
            if doc:
                documents.append(doc)
        return documents

    def load_scalac_bundle(self) -> List[Document]:
        """Return the built-in Scalac knowledge bundle.

        This is a curated set of documents that give the council
        deep context about Scalac — enough to produce authentic,
        Scalac-specific marketing output without any hardcoding
        in the agent source code.

        To use, pass ``--company scalac`` or set
        ``SCALAC_MODE=true``.
        """
        from council.config.loader import ConfigLoader

        bundle_dir = (
            Path(__file__).parent.parent.parent.parent
            / "templates" / "companies" / "scalac_data"
        )
        if bundle_dir.is_dir():
            return self.load_directory(bundle_dir, doc_type="scalac")

        # Fallback: inline minimal Scalac context
        logger.info("Scalac data dir not found — using inline bundle")
        return self._inline_scalac_bundle()

    # ── Internal helpers ────────────────────────────────────────────────────

    def _load_file(
        self,
        file_path: Path,
        doc_type: str,
    ) -> Optional[Document]:
        """Load a single file, skipping oversized or unreadable ones."""
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return None

        try:
            size = file_path.stat().st_size
            if size > self.max_size_bytes:
                logger.warning(
                    "Skipping oversized file %s (%d bytes > %d limit)",
                    file_path, size, self.max_size_bytes,
                )
                return None

            content = file_path.read_text(encoding="utf-8")
            return Document(
                name=file_path.stem,
                path=file_path,
                content=content,
                doc_type=doc_type,
            )
        except OSError as exc:
            logger.warning("Cannot read %s: %s", file_path, exc)
            return None

    @staticmethod
    def _inline_scalac_bundle() -> List[Document]:
        """Minimal inline Scalac context when data directory is absent.

        This is **not** hardcoding in agent source — it is data loaded
        at runtime via the same Document abstraction used for any
        other company.
        """
        scalac_brief = Document(
            name="scalac_brief",
            path=Path("inline://scalac_brief.md"),
            doc_type="brief",
            content=(
                "# Scalac Brief\n\n"
                "Scalac is a software development company specialising in "
                "Scala, blockchain, data engineering and AI/ML.\n\n"
                "**Services:**\n"
                "- Team Extension (dedicated Scala/Blockchain teams)\n"
                "- Project-based (MVP, full product)\n"
                "- Consulting (architecture, audits, workshops)\n\n"
                "**Key differentiators:**\n"
                "- Largest Scala team in Europe (150+ engineers)\n"
                "- Blockchain expertise (Substrate, EVM, smart contracts)\n"
                "- Machine Learning & Data Engineering\n"
                "- Functional programming pedigree\n\n"
                "**Target segments:**\n"
                "- CTOs at Series A-C startups scaling engineering\n"
                "- Enterprises adopting blockchain (DeFi, NFT, supply chain)\n"
                "- Companies building data-intensive products\n"
                "- Teams needing FP/Scala expertise (30% of market)\n\n"
                "**Pricing model:**\n"
                "- Team Extension: ~EUR 6-8K/engineer/month\n"
                "- Project: fixed scope + time & materials\n"
                "- Consulting: daily rate EUR 1.5-2K\n\n"
                "**Competitors:**\n"
                "- VirtusLab (Scala, Poland)\n"
                "- SoftwareMill (Scala/Scala Poland)\n"
                "- EPAM (general outsourcing)\n"
                "- BairesDev (LatAm general)\n\n"
                "**Case studies:**\n"
                "- SwissBorg: blockchain exchange (30+ engineers, 3 years)\n"
                "- Colossus: NFT marketplace (20 engineers, 18 months)\n"
                "- Iterators: ML platform for logistics (15 engineers, 2 years)\n"
                "- Billie: BNPL fintech Scala migration (10 engineers, 12 months)\n"
            ),
        )
        scalac_cs_swissborg = Document(
            name="case_study_swissborg",
            path=Path("inline://case_study_swissborg.md"),
            doc_type="case_study",
            content=(
                "# Case Study: SwissBorg\n\n"
                "**Client:** SwissBorg (block wealth management platform)\n"
                "**Challenge:** Build a secure, high-throughput crypto exchange "
                "supporting 100K+ concurrent users.\n"
                "**Solution:** Dedicated team of 30+ Scala/Blockchain engineers. "
                "Built microservices architecture with Akka, Kafka, PostgreSQL. "
                "Smart contracts in Solidity + Substrate runtime.\n"
                "**Results:**\n"
                "- 99.99% uptime during peak trading volumes\n"
                "- Sub-100ms order execution\n"
                "- $4.5B+ assets under management\n"
                "- 3-year ongoing partnership\n"
            ),
        )
        return [scalac_brief, scalac_cs_swissborg]


@dataclass
class AgentContext:
    """Enriched context combining CompanyConfig + loaded documents.

    This is what agents actually consume — it merges the structured
    JSON config with unstructured markdown documents (briefs, case
    studies, research) into a single coherent context string.
    """

    company: "CompanyConfig"
    documents: List[Document] = field(default_factory=list)

    def to_prompt_fragment(self, doc_types: Optional[List[str]] = None) -> str:
        """Build a markdown prompt fragment from all (or filtered) documents.

        Args:
            doc_types: If given, only include documents whose
                ``doc_type`` is in this list.

        Returns:
            A single markdown string with all documents formatted
            as clearly delimited sections.
        """
        docs = self.documents
        if doc_types:
            docs = [d for d in docs if d.doc_type in doc_types]

        if not docs:
            return ""

        lines: List[str] = ["\n## Additional Context Documents\n"]
        for doc in docs:
            lines.append(f"\n### {doc.name} ({doc.doc_type})\n")
            lines.append(doc.content)
            lines.append("\n---\n")

        return "\n".join(lines)
