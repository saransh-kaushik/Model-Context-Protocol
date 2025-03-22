from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from pydantic_ai import Agent
import asyncio
import pathlib
import json
import sys
import os
import platform

import mcp_tools

# Load environment variables from .env file
load_dotenv()


async def chat_loop(agent: Agent) -> None:
    """Run an interactive chat loop with the agent until the user enters 'q' to quit."""
    print("Starting chat with AI agent. Type 'q' to quit.")
    print("-" * 50)
    
    # Keep track of conversation history
    conversation_history = []
    
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        # Check if user wants to quit
        if user_input.lower() == 'q':
            print("Exiting chat. Goodbye!")
            break
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        try:
            # Format the conversation history for the agent
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
            
            # Run the agent with the prompt
            result = await agent.run(prompt)
            response = result.data
            
            # Add agent response to history
            conversation_history.append({"role": "assistant", "content": response})
            
            # Print the agent's response
            print(f"\nAI: {response}")
            
        except Exception as e:
            print(f"\nError: {str(e)}")


async def main() -> None:
    # Determine appropriate command for npx based on platform
    if platform.system() == "Windows":
        npx_cmd = "cmd.exe"
        npx_args = ["/c", "npx", "-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent)]
    else:
        npx_cmd = os.getenv("NPX_COMMAND", "npx")
        npx_args = ["-y", "@modelcontextprotocol/server-filesystem", str(pathlib.Path(__file__).parent)]
    
    server_params = StdioServerParameters(
        command=npx_cmd,
        args=npx_args,
    )
    
    print(f"Starting MCP server with command: {npx_cmd} {' '.join(npx_args)}")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            tools = await mcp_tools.mcp_tools(session)
            agent = Agent(model="google-gla:gemini-1.5-pro", tools=tools)
            
            # Start the interactive chat loop
            await chat_loop(agent)


if __name__ == "__main__":
    asyncio.run(main())