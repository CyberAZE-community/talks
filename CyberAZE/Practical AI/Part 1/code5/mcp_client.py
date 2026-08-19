import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from openai import AsyncOpenAI


MCP_URL = "http://localhost:8000/mcp"


async def main() -> None:
    openai = AsyncOpenAI()

    # Connect to the MCP server over Streamable HTTP.
    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream,
        _get_session_id,
    ):
        async with ClientSession(read_stream, write_stream) as mcp:
            await mcp.initialize()

            # Discover tools exposed by the MCP server.
            mcp_tools = (await mcp.list_tools()).tools

            # Convert MCP tool definitions to OpenAI function tools.
            openai_tools = [
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                    # MCP schemas are not always OpenAI strict-mode compatible.
                    "strict": False,
                }
                for tool in mcp_tools
            ]

            input_items = [
                {
                    "role": "user",
                    "content": "Use the available tools to answer my request.",
                }
            ]

            while True:
                response = await openai.responses.create(
                    model="gpt-5.6",
                    input=input_items,
                    tools=openai_tools,
                )

                # Preserve the model output for the next request.
                input_items.extend(response.output)

                tool_calls = [
                    item
                    for item in response.output
                    if item.type == "function_call"
                ]

                if not tool_calls:
                    print(response.output_text)
                    return

                for call in tool_calls:
                    arguments = json.loads(call.arguments)

                    # Execute the requested function through MCP over HTTP.
                    result = await mcp.call_tool(
                        name=call.name,
                        arguments=arguments,
                    )

                    # Return the MCP result to the OpenAI model.
                    input_items.append(
                        {
                            "type": "function_call_output",
                            "call_id": call.call_id,
                            "output": result.model_dump_json(by_alias=True),
                        }
                    )


if __name__ == "__main__":
    asyncio.run(main())