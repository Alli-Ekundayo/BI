"""Tool definitions for the LLM agent."""

# Tool definitions using dictionary format compatible with the new google-genai SDK.

introspect_schema = {
    "name": "introspect_schema",
    "description": "Fetch the schema of the connected datasource — tables, collections, or column names depending on type.",
    "parameters": {
        "type": "OBJECT",
        "properties": {},
    },
}

generate_query = {
    "name": "generate_query",
    "description": "Generate the appropriate query (SQL, MongoDB aggregation, pandas filter) from the user's natural language request and the schema.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The generated query string (SQL, MongoDB aggregation pipeline, or pandas filter)",
            }
        },
        "required": ["query"],
    },
}

execute_query = {
    "name": "execute_query",
    "description": "Execute the generated query against the datasource and return the results.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "query": {
                "type": "STRING",
                "description": "The query to execute",
            }
        },
        "required": ["query"],
    },
}

suggest_visualization = {
    "name": "suggest_visualization",
    "description": "Based on the query results, suggest the best chart type: table, bar, line, or pie.",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "viz_type": {
                "type": "STRING",
                "enum": ["table", "bar", "line", "pie"],
                "description": "The recommended visualization type",
            },
            "x_key": {
                "type": "STRING",
                "description": "The field to use for X-axis (for charts)",
            },
            "y_key": {
                "type": "STRING",
                "description": "The field to use for Y-axis (for charts)",
            },
        },
        "required": ["viz_type"],
    },
}

# Bundled Tool object passed to Gemini
BI_TOOLS = {
    "function_declarations": [
        introspect_schema,
        generate_query,
        execute_query,
        suggest_visualization,
    ]
}
