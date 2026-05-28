from __future__ import annotations

import pytest

from council.config.documents import _smart_truncate


class TestSmartTruncate:
    """Tests for the _smart_truncate markdown-aware truncation helper (#6)."""

    def test_short_text_unchanged(self) -> None:
        """Text shorter than the limit is returned without modification."""
        text = "Hello world"
        result = _smart_truncate(text, 100)
        assert result == text

    def test_text_exactly_at_limit(self) -> None:
        """Text whose length equals the limit is returned without modification."""
        text = "Exactly twenty chars"
        assert len(text) == 20
        result = _smart_truncate(text, 20)
        assert result == text

    def test_truncates_at_word_boundary(self) -> None:
        """Long text is cut at a word boundary, not mid-word."""
        # "alpha beta gamma delta epsilon"
        #  01234 56789 01234 5678901234567
        # Limit = 13 puts cursor in the middle of "gamma" (chars 11-15).
        text = "alpha beta gamma delta epsilon"
        result = _smart_truncate(text, 13)
        # Strip the truncation marker to inspect the kept body
        body = result.replace("[... content truncated ...]", "").strip()
        # Every token in the kept body must be a complete word from the original
        words_in_body = body.split()
        original_words = text.split()
        for word in words_in_body:
            assert word in original_words, (
                f"Truncated body contains unexpected fragment: {word!r}"
            )
        # The last token of the body must be a complete word (not a partial fragment).
        # A fragment would be a string that is a strict prefix of a word in the original.
        last_token = words_in_body[-1] if words_in_body else ""
        assert any(
            last_token == w for w in original_words
        ), f"Last token {last_token!r} is not a complete word from the original text"

    def test_adds_truncation_marker(self) -> None:
        """Truncated text must contain the truncation indicator."""
        text = " ".join(["word"] * 200)
        result = _smart_truncate(text, 50)
        assert "[... content truncated ...]" in result

    def test_does_not_cut_inside_code_fence(self) -> None:
        """If the truncation point falls inside a code fence, cut before the fence."""
        preamble = "This is some preamble text before the code block. " * 2
        fence_block = "```python\nprint('hello')\nx = 1 + 2\n```"
        text = preamble + fence_block
        # Set the limit so it falls inside the fence block
        fence_start = text.index("```python")
        limit = fence_start + 5  # clearly inside the opening fence

        result = _smart_truncate(text, limit)
        # The result must not contain any part of the code fence
        assert "```" not in result, (
            "Result must not contain backticks — truncation should occur before the fence"
        )
        assert "[... content truncated ...]" in result
