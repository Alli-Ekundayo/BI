import asyncio
import json
import logging
from typing import Any, Tuple

from google import genai
from google.genai import types

from app.config import settings
from app.agent.tools import BI_TOOLS
from app.agent.prompt import build_system_prompt
from app.agent.memory import convert_to_gemini_content
from app.agent.retry import execute_with_retry, format_error_for_llm

logger = logging.getLogger(__name__)

# Initialize the new Gemini Client
client = genai.Client(api_key=settings.google_api_key)

MAX_TOOL_CALLS = 15  # Max tool calls per query to prevent infinite loops


async def run_agent(
    message: str,
    schema: dict,
    connector: Any,
    datasource_type: str,
    session_messages: list[dict[str, str]] = None,
) -> Tuple[str, list[dict], str, str]:
    """
    Run the LLM agent with tool calling using the new google-genai SDK.
    """
    if session_messages is None:
        session_messages = []
    
    # Build system prompt with schema injection
    system_prompt = build_system_prompt(schema, datasource_type)
    
    # Initialize model settings
    model_name = settings.google_model_name
    logger.info(f"Using model: {model_name}")
    
    # Convert session history to Gemini format
    chat_history = convert_to_gemini_content(session_messages)
    
    # Start chat session
    # Note: tools are passed in the config, not in the model initialization
    chat = client.chats.create(
        model=model_name,
        history=chat_history,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[BI_TOOLS],
        )
    )
    
    tool_calls_made = 0
    generated_query = None
    results = []
    viz_type = "table"
    final_answer = ""
    
    # Send initial user message
    logger.info(f"User query: {message}")
    try:
        response = chat.send_message(message)
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "ResourceExhausted" in error_str:
            # Simple one-time retry
            logger.warning("Quota hit on initial message, retrying in 2 seconds...")
            await asyncio.sleep(2)
            try:
                response = chat.send_message(message)
            except Exception as retry_e:
                logger.error(f"Initial message retry failed: {retry_e}")
                return (
                    "The AI service is currently at its capacity or quota limit. Please wait a moment and try again.",
                    [],
                    "",
                    "table"
                )
        elif "ConnectError" in error_str or "Name or service not known" in error_str:
            return (
                "Unable to connect to the AI service. Please check your internet connection and try again.",
                [],
                "",
                "table"
            )
        elif "500" in error_str or "Internal error encountered" in error_str:
            logger.error(f"Internal error from AI service: {error_str}. This often happens if the selected model does not support native tool-calling.")
            return (
                "The AI service encountered an internal error. This may be due to the selected model's compatibility with tool-calling. Please try a Gemini model or try again in a few moments.",
                [],
                "",
                "table"
            )
        else:
            raise e
    
    # Tool-calling loop
    while tool_calls_made < MAX_TOOL_CALLS:
        # Check if model returned a function call
        fn_call = _extract_function_call(response)
        if not fn_call:
            # No function call - model returned final text answer
            final_answer = response.text
            logger.info(f"Agent final answer: {final_answer}")
            break
        
        fn_name, fn_args = fn_call
        logger.info(f"Tool call: {fn_name} with args: {fn_args}")
        
        # Dispatch the tool
        tool_result = await _dispatch_tool(
            fn_name, fn_args, connector, datasource_type, generated_query
        )
        
        # Extract values for return
        if fn_name == "generate_query":
            generated_query = fn_args.get("query")
        elif fn_name == "execute_query":
            if isinstance(tool_result, dict) and "error" in tool_result:
                # Error occurred
                error_msg = tool_result["error"]
                tool_result = {
                    "error": error_msg,
                    "retry_suggestion": format_error_for_llm(error_msg, generated_query, datasource_type),
                }
            else:
                results = tool_result.get("results", [])
        elif fn_name == "suggest_visualization":
            viz_type = fn_args.get("viz_type", "table")
        
        # Send tool result back to the LLM
        try:
            # Prepare a potentially truncated version of the result for the LLM
            # to avoid hitting quota/token limits with large datasets.
            # We still keep the full 'results' for the final return.
            llm_tool_result = tool_result
            if fn_name == "execute_query" and isinstance(tool_result, dict) and "results" in tool_result:
                full_results = tool_result["results"]
                if len(full_results) > 20:
                    llm_tool_result = {
                        "results": full_results[:20],
                        "total_row_count": len(full_results),
                        "note": "Only the first 20 rows are shown for analysis. The user has access to all results."
                    }

            # In the new SDK, we send the function response as part of the next message
            response = chat.send_message(
                types.Part.from_function_response(
                    name=fn_name,
                    response={"result": json.dumps(llm_tool_result, default=str)},
                )
            )
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "ResourceExhausted" in error_str:
                # Simple one-time retry for quota/rate limit errors
                logger.warning("Quota hit, retrying in 2 seconds...")
                await asyncio.sleep(2)
                try:
                    response = chat.send_message(
                        types.Part.from_function_response(
                            name=fn_name,
                            response={"result": json.dumps(llm_tool_result, default=str)},
                        )
                    )
                except Exception as retry_e:
                    logger.error(f"Retry failed: {retry_e}")
                    return (
                        "The AI service is currently at its capacity or quota limit. Please wait a moment and try again.",
                        results,
                        generated_query or "",
                        viz_type
                    )
            elif "ConnectError" in error_str or "Name or service not known" in error_str:
                return (
                    "Unable to connect to the AI service. Please check your internet connection and try again.",
                    results,
                    generated_query or "",
                    viz_type
                )
            elif "500" in error_str or "Internal error encountered" in error_str:
                return (
                    "The AI service encountered an internal error. Please try again in a few moments.",
                    results,
                    generated_query or "",
                    viz_type
                )
            else:
                raise e
        
        tool_calls_made += 1
    
    if tool_calls_made >= MAX_TOOL_CALLS:
        raise ValueError("Max tool calls exceeded - possible infinite loop")
    
    return final_answer, results, generated_query or "", viz_type


def _extract_function_call(response: Any) -> Tuple[str, dict] | None:
    """
    Extract function call from Gemini response.
    """
    if not response.candidates:
        return None
        
    for part in response.candidates[0].content.parts:
        if part.function_call:
            fn = part.function_call
            return fn.name, fn.args
    return None


async def _dispatch_tool(
    name: str, args: dict, connector: Any, datasource_type: str, generated_query: str = None
) -> dict[str, Any]:
    """
    Dispatch tool calls to appropriate implementations.
    """
    if name == "introspect_schema":
        schema = await connector.get_schema()
        return {"schema": schema}
    
    elif name == "generate_query":
        return {"query": args.get("query")}
    
    elif name == "execute_query":
        query = args.get("query")
        if not query:
            return {"error": "No query provided"}
        
        results, error = await execute_with_retry(connector, query, datasource_type)
        if error:
            return {"error": error, "were_retried": True}
        return {"results": results}
    
    elif name == "suggest_visualization":
        viz_type = args.get("viz_type", "table")
        if viz_type not in ["table", "bar", "line", "pie"]:
            viz_type = "table"
        
        return {
            "viz_type": viz_type,
            "x_key": args.get("x_key"),
            "y_key": args.get("y_key"),
        }
    
    else:
        raise ValueError(f"Unknown tool: {name}")
