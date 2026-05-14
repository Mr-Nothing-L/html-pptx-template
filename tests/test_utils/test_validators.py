"""Tests for validator utility functions."""

import pytest

from html_pptx_template.utils.validators import validate_url, sanitize_template_id


class TestValidateUrl:
    """Tests for validate_url function."""

    def test_valid_http_url(self):
        """Accept a valid HTTP URL and return it unchanged."""
        url = "http://example.com"
        assert validate_url(url) == url

    def test_valid_https_url(self):
        """Accept a valid HTTPS URL and return it unchanged."""
        url = "https://example.com"
        assert validate_url(url) == url

    def test_valid_url_with_path(self):
        """Accept a URL with a path."""
        url = "https://example.com/path/to/page"
        assert validate_url(url) == url

    def test_valid_url_with_query(self):
        """Accept a URL with query parameters."""
        url = "https://example.com?page=1"
        assert validate_url(url) == url

    def test_invalid_ftp_url(self):
        """Raise ValueError for non-http(s) protocol."""
        with pytest.raises(ValueError):
            validate_url("ftp://example.com")

    def test_invalid_no_protocol(self):
        """Raise ValueError for URL without protocol."""
        with pytest.raises(ValueError):
            validate_url("example.com")

    def test_invalid_empty_string(self):
        """Raise ValueError for empty string."""
        with pytest.raises(ValueError):
            validate_url("")

    def test_invalid_none(self):
        """Raise ValueError for None input."""
        with pytest.raises(ValueError):
            validate_url(None)


class TestSanitizeTemplateId:
    """Tests for sanitize_template_id function."""

    def test_lowercase(self):
        """Convert name to lowercase."""
        assert sanitize_template_id("MyTemplate") == "mytemplate"

    def test_spaces_to_hyphens(self):
        """Replace spaces with hyphens."""
        assert sanitize_template_id("my template") == "my-template"

    def test_multiple_spaces(self):
        """Collapse multiple spaces into a single hyphen."""
        assert sanitize_template_id("my   template") == "my-template"

    def test_remove_special_chars(self):
        """Remove special characters."""
        assert sanitize_template_id("my@template#1!") == "mytemplate1"

    def test_mixed_input(self):
        """Handle mixed case, spaces, and special characters."""
        assert sanitize_template_id("My Awesome Template!") == "my-awesome-template"

    def test_leading_trailing_spaces(self):
        """Trim leading and trailing spaces."""
        assert sanitize_template_id("  my template  ") == "my-template"

    def test_leading_trailing_hyphens_removed(self):
        """Remove leading and trailing hyphens after sanitization."""
        assert sanitize_template_id("!my template!") == "my-template"

    def test_empty_result_raises(self):
        """Raise ValueError if sanitization yields empty string."""
        with pytest.raises(ValueError):
            sanitize_template_id("!!!")
