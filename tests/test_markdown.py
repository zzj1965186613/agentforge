"""Tests for agentforge.utils.markdown — parse_frontmatter and render_variables."""

from __future__ import annotations

from agentforge.utils.markdown import parse_frontmatter, render_variables

# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    """Tests for parse_frontmatter()."""

    def test_basic_frontmatter(self):
        content = "---\nname: test\nversion: 1.0\n---\n\nHello world"
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "test"
        assert meta["version"] == 1.0  # YAML parses 1.0 as float
        assert body.strip() == "Hello world"

    def test_no_frontmatter_returns_full_content(self):
        content = "Just some markdown\n\n## Header"
        meta, body = parse_frontmatter(content)
        assert meta == {}
        assert body == content

    def test_frontmatter_with_lists(self):
        content = "---\ntags: [a, b, c]\n---\n\nBody here"
        meta, body = parse_frontmatter(content)
        assert meta["tags"] == ["a", "b", "c"]

    def test_frontmatter_empty_body(self):
        content = "---\nname: empty\n---\n"
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "empty"
        # body is what comes after the frontmatter separator (may be empty)
        assert body.strip() == ""

    def test_frontmatter_with_empty_yaml(self):
        content = "---\n---\n\nBody"
        meta, body = parse_frontmatter(content)
        # YAML between --- lines is empty, so metadata should be empty dict
        assert isinstance(meta, dict)

    def test_frontmatter_multiline_body(self):
        content = "---\nname: x\n---\n\nLine 1\nLine 2\nLine 3"
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "x"
        assert "Line 1" in body
        assert "Line 3" in body

    def test_frontmatter_with_colons_in_body(self):
        content = "---\nname: test\n---\n\nKey: Value\nAnother: thing"
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "test"
        assert "Key: Value" in body

    def test_frontmatter_with_complex_values(self):
        content = "---\nname: complex\nnested:\n  key: value\n---\n\nBody"
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "complex"
        assert meta["nested"]["key"] == "value"

    def test_frontmatter_bad_yaml_returns_empty(self):
        # Malformed YAML between separators
        content = "---\n: invalid: yaml: [[[\n---\n\nBody"
        meta, body = parse_frontmatter(content)
        assert isinstance(meta, dict)
        # body should still be extracted
        assert "Body" in body

    def test_frontmatter_with_quoted_strings(self):
        content = '---\nname: "quoted name"\n---\n\nBody'
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "quoted name"

    def test_frontmatter_whitespace_handling(self):
        content = "---  \nname: test  \n---  \n\nBody"
        meta, body = parse_frontmatter(content)
        assert meta["name"] == "test"


# ---------------------------------------------------------------------------
# render_variables
# ---------------------------------------------------------------------------


class TestRenderVariables:
    """Tests for render_variables()."""

    def test_simple_substitution(self):
        content = "Hello {{NAME}}, welcome to {{PLACE}}."
        result = render_variables(content, {"NAME": "World", "PLACE": "Earth"})
        assert result == "Hello World, welcome to Earth."

    def test_no_variables(self):
        content = "No variables here."
        result = render_variables(content, {"FOO": "bar"})
        assert result == "No variables here."

    def test_unrecognized_placeholders_left_intact(self):
        content = "Keep {{UNKNOWN}} and {{ALSO_UNKNOWN}}."
        result = render_variables(content, {"KNOWN": "yes"})
        assert result == "Keep {{UNKNOWN}} and {{ALSO_UNKNOWN}}."

    def test_empty_variables_dict(self):
        content = "{{X}} stays"
        result = render_variables(content, {})
        assert result == "{{X}} stays"

    def test_whitespace_in_placeholders(self):
        content = "Value: {{ NAME }}"
        result = render_variables(content, {"NAME": "test"})
        assert result == "Value: test"

    def test_multiple_occurrences(self):
        content = "{{A}} and {{A}} again"
        result = render_variables(content, {"A": "X"})
        assert result == "X and X again"

    def test_empty_replacement(self):
        content = "Before{{X}}After"
        result = render_variables(content, {"X": ""})
        assert result == "BeforeAfter"

    def test_special_characters_in_replacement(self):
        content = "Pattern: {{REGEX}}"
        result = render_variables(content, {"REGEX": r"\d+ [a-z]"})
        assert r"\d+ [a-z]" in result

    def test_multiline_content(self):
        content = "Line1 {{VAR}}\nLine2 {{VAR}}"
        result = render_variables(content, {"VAR": "REPLACED"})
        assert result == "Line1 REPLACED\nLine2 REPLACED"

    def test_case_sensitive(self):
        content = "{{name}} vs {{NAME}}"
        result = render_variables(content, {"name": "lower", "NAME": "UPPER"})
        assert result == "lower vs UPPER"

    def test_numeric_placeholder_names(self):
        content = "Item {{ITEM1}} and {{ITEM2}}"
        result = render_variables(content, {"ITEM1": "first", "ITEM2": "second"})
        assert result == "Item first and second"
