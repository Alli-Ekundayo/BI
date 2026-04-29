"""Tests for agent orchestration."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agent.retry import execute_with_retry, format_error_for_llm


class TestRetryLogic:
    """Tests for query retry logic."""

    @pytest.mark.asyncio
    async def test_successful_query_on_first_attempt(self):
        """Test that successful queries return immediately."""
        connector = AsyncMock()
        connector.execute = AsyncMock(return_value=[{"id": 1, "name": "test"}])
        
        results, error = await execute_with_retry(
            connector, 
            "SELECT * FROM table", 
            "postgres"
        )
        
        assert results == [{"id": 1, "name": "test"}]
        assert error is None
        connector.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_failure_after_retries(self):
        """Test that queries fail after max retries."""
        connector = AsyncMock()
        connector.execute = AsyncMock(side_effect=ValueError("Invalid table"))
        
        results, error = await execute_with_retry(
            connector, 
            "SELECT * FROM invalid_table", 
            "postgres"
        )
        
        assert results is None
        assert error is not None
        assert "Invalid table" in error
        # Should retry up to MAX_RETRIES times
        assert connector.execute.call_count == 3

    @pytest.mark.asyncio
    async def test_error_formatting_for_llm(self):
        """Test that errors are formatted for LLM learning."""
        error = "Table 'invalid' does not exist"
        query = "SELECT * FROM invalid"
        
        formatted = format_error_for_llm(error, query, "postgres")
        
        assert "postgres" in formatted
        assert error in formatted
        assert query in formatted


class TestPromptBuilding:
    """Tests for system prompt building."""

    def test_prompt_includes_schema(self):
        """Test that the system prompt includes the schema."""
        from app.agent.prompt import build_system_prompt
        
        schema = {
            "users": [
                {"column": "id", "type": "integer"},
                {"column": "name", "type": "text"},
            ]
        }
        
        prompt = build_system_prompt(schema, "postgres")
        
        assert "users" in prompt
        assert "id" in prompt
        assert "name" in prompt


class TestMemoryManagement:
    """Tests for message history management."""

    def test_context_truncation(self):
        """Test that old messages are truncated to stay in token limits."""
        from app.agent.memory import truncate_context
        
        messages = [
            {"role": "user", "content": f"Message {i}"}
            for i in range(50)
        ]
        
        truncated = truncate_context(messages)
        
        # Should keep only recent messages
        assert len(truncated) <= 20
