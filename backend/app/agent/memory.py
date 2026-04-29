"""Session context window management for the agent."""
from typing import Any


MAX_CONTEXT_MESSAGES = 20  # Keep the last 20 messages in context
def convert_to_gemini_content(messages: list[dict[str, str]]) -> list[dict[str, Any]]:
    """
    Convert message history to Gemini Content format for the new google-genai SDK.
    
    Args:
        messages: List of messages with 'role' and 'content' keys
    
    Returns:
        List of content dictionaries for chat history
    """
    chat_history = []
    for msg in messages[-MAX_CONTEXT_MESSAGES:]:  # Only keep recent messages
        role = msg["role"]
        # Gemini expects "user" or "model" as roles
        gemini_role = "user" if role == "user" else "model"
        chat_history.append(
            {
                "role": gemini_role,
                "parts": [{"text": msg["content"]}],
            }
        )
    return chat_history


def truncate_context(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Keep only the most recent messages to stay within token limits.
    
    Args:
        messages: Full message history
    
    Returns:
        Truncated message list
    """
    if len(messages) > MAX_CONTEXT_MESSAGES:
        # Keep system message + recent messages
        return messages[-MAX_CONTEXT_MESSAGES:]
    return messages


def summarize_long_messages(messages: list[dict[str, str]]) -> str:
    """
    Create a summary of old messages to preserve context while reducing tokens.
    This is called when truncating would lose important information.
    
    Args:
        messages: Full message history
    
    Returns:
        A summary string of earlier messages
    """
    old_messages = messages[:-MAX_CONTEXT_MESSAGES]
    if not old_messages:
        return ""
    
    summary = "Earlier in the conversation:\n"
    for msg in old_messages[-5:]:  # Use last 5 old messages for summary
        summary += f"- {msg['role']}: {msg['content'][:100]}...\n"
    
    return summary
