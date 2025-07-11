#!/usr/bin/env python3
"""
FastMCP Server for Adding Two Numbers

This script creates a FastMCP server that exposes an add_numbers tool
for integration with Anthropic's Claude via the Model Context Protocol.
"""

import fastmcp

def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers together.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        Sum of a and b
    """
    return a + b

# Create FastMCP server
app = fastmcp.FastMCP("Add Numbers Server")

# Register the add_numbers function as a tool
@app.tool()
def add_numbers_tool(a: int, b: int) -> str:
    """
    Add two numbers together.
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        A string describing the result of adding the two numbers
    """
    result = add_numbers(a, b)
    return f"The sum of {a} and {b} is {result}"

if __name__ == "__main__":
    app.run()
