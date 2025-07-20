#!/usr/bin/env python3
"""
FastMCP Server for Git Operations

This script creates a FastMCP server that exposes various Git tools
for integration with Anthropic's Claude via the Model Context Protocol.
"""

import fastmcp
import subprocess
import os
from typing import Optional, List
import json

def run_git_command(repo_path: str, command: List[str]) -> dict:
    """
    Run a git command in the specified repository path.
    
    Args:
        repo_path: Path to the git repository
        command: Git command as a list of strings
        
    Returns:
        Dictionary with success status, output, and error information
    """
    try:
        # Change to the repository directory
        original_cwd = os.getcwd()
        if repo_path and os.path.exists(repo_path):
            os.chdir(repo_path)
        
        # Run the git command
        result = subprocess.run(
            ['git'] + command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Restore original directory
        os.chdir(original_cwd)
        
        return {
            'success': result.returncode == 0,
            'output': result.stdout.strip(),
            'error': result.stderr.strip(),
            'return_code': result.returncode
        }
    except subprocess.TimeoutExpired:
        os.chdir(original_cwd)
        return {
            'success': False,
            'output': '',
            'error': 'Command timed out after 30 seconds',
            'return_code': -1
        }
    except Exception as e:
        os.chdir(original_cwd)
        return {
            'success': False,
            'output': '',
            'error': str(e),
            'return_code': -1
        }

# Create FastMCP server
app = fastmcp.FastMCP("Git Server")

@app.tool()
def git_status(repo_path: str = ".") -> str:
    """
    Get the status of a Git repository.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
        
    Returns:
        Git status output as a string
    """
    result = run_git_command(repo_path, ['status'])
    if result['success']:
        return f"Git Status:\n{result['output']}"
    else:
        return f"Error getting git status: {result['error']}"

@app.tool()
def git_add(repo_path: str, files: str = ".") -> str:
    """
    Add files to the Git staging area.
    
    Args:
        repo_path: Path to the git repository
        files: Files to add (default: all files with ".")
        
    Returns:
        Result of the git add operation
    """
    result = run_git_command(repo_path, ['add', files])
    if result['success']:
        return f"Successfully added files: {files}"
    else:
        return f"Error adding files: {result['error']}"

@app.tool()
def git_commit(repo_path: str, message: str, author: Optional[str] = None) -> str:
    """
    Commit changes to the Git repository.
    
    Args:
        repo_path: Path to the git repository
        message: Commit message
        author: Optional author in format "Name <email>"
        
    Returns:
        Result of the git commit operation
    """
    command = ['commit', '-m', message]
    if author:
        command.extend(['--author', author])
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Successfully committed with message: '{message}'\n{result['output']}"
    else:
        return f"Error committing changes: {result['error']}"

@app.tool()
def git_push(repo_path: str, remote: str = "origin", branch: Optional[str] = None) -> str:
    """
    Push changes to a remote repository.
    
    Args:
        repo_path: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (optional, uses current branch if not specified)
        
    Returns:
        Result of the git push operation
    """
    command = ['push', remote]
    if branch:
        command.append(branch)
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Successfully pushed to {remote}" + (f"/{branch}" if branch else "") + f"\n{result['output']}"
    else:
        return f"Error pushing to remote: {result['error']}"

@app.tool()
def git_pull(repo_path: str, remote: str = "origin", branch: Optional[str] = None) -> str:
    """
    Pull changes from a remote repository.
    
    Args:
        repo_path: Path to the git repository
        remote: Remote name (default: origin)
        branch: Branch name (optional, uses current branch if not specified)
        
    Returns:
        Result of the git pull operation
    """
    command = ['pull', remote]
    if branch:
        command.append(branch)
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Successfully pulled from {remote}" + (f"/{branch}" if branch else "") + f"\n{result['output']}"
    else:
        return f"Error pulling from remote: {result['error']}"

@app.tool()
def git_log(repo_path: str, max_count: int = 10, oneline: bool = True) -> str:
    """
    Show the commit history.
    
    Args:
        repo_path: Path to the git repository
        max_count: Maximum number of commits to show (default: 10)
        oneline: Show commits in one line format (default: True)
        
    Returns:
        Git log output
    """
    command = ['log', f'--max-count={max_count}']
    if oneline:
        command.append('--oneline')
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Git Log (last {max_count} commits):\n{result['output']}"
    else:
        return f"Error getting git log: {result['error']}"

@app.tool()
def git_diff(repo_path: str, file_path: Optional[str] = None, staged: bool = False) -> str:
    """
    Show differences between commits, commit and working tree, etc.
    
    Args:
        repo_path: Path to the git repository
        file_path: Specific file to show diff for (optional)
        staged: Show staged changes (default: False)
        
    Returns:
        Git diff output
    """
    command = ['diff']
    if staged:
        command.append('--staged')
    if file_path:
        command.append(file_path)
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Git Diff:\n{result['output']}" if result['output'] else "No differences found"
    else:
        return f"Error getting git diff: {result['error']}"

@app.tool()
def git_branch(repo_path: str, list_branches: bool = True, branch_name: Optional[str] = None) -> str:
    """
    List, create, or delete branches.
    
    Args:
        repo_path: Path to the git repository
        list_branches: List all branches (default: True)
        branch_name: Name of branch to create (optional)
        
    Returns:
        Result of the git branch operation
    """
    if list_branches and not branch_name:
        command = ['branch', '-a']
    elif branch_name:
        command = ['branch', branch_name]
    else:
        command = ['branch']
    
    result = run_git_command(repo_path, command)
    if result['success']:
        if branch_name:
            return f"Successfully created branch: {branch_name}"
        else:
            return f"Git Branches:\n{result['output']}"
    else:
        return f"Error with git branch operation: {result['error']}"

@app.tool()
def git_checkout(repo_path: str, branch_or_commit: str, create_branch: bool = False) -> str:
    """
    Switch branches or restore working tree files.
    
    Args:
        repo_path: Path to the git repository
        branch_or_commit: Branch name or commit hash to checkout
        create_branch: Create a new branch (default: False)
        
    Returns:
        Result of the git checkout operation
    """
    command = ['checkout']
    if create_branch:
        command.append('-b')
    command.append(branch_or_commit)
    
    result = run_git_command(repo_path, command)
    if result['success']:
        action = "Created and switched to" if create_branch else "Switched to"
        return f"{action} branch/commit: {branch_or_commit}\n{result['output']}"
    else:
        return f"Error checking out {branch_or_commit}: {result['error']}"

@app.tool()
def git_merge(repo_path: str, branch: str, no_ff: bool = False) -> str:
    """
    Merge branches.
    
    Args:
        repo_path: Path to the git repository
        branch: Branch to merge into current branch
        no_ff: Create a merge commit even if fast-forward is possible (default: False)
        
    Returns:
        Result of the git merge operation
    """
    command = ['merge']
    if no_ff:
        command.append('--no-ff')
    command.append(branch)
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Successfully merged branch '{branch}'\n{result['output']}"
    else:
        return f"Error merging branch '{branch}': {result['error']}"

@app.tool()
def git_clone(url: str, destination: Optional[str] = None, branch: Optional[str] = None) -> str:
    """
    Clone a repository into a new directory.
    
    Args:
        url: Repository URL to clone
        destination: Directory name for the cloned repository (optional)
        branch: Specific branch to clone (optional)
        
    Returns:
        Result of the git clone operation
    """
    command = ['clone']
    if branch:
        command.extend(['-b', branch])
    command.append(url)
    if destination:
        command.append(destination)
    
    result = run_git_command(".", command)
    if result['success']:
        return f"Successfully cloned repository from {url}\n{result['output']}"
    else:
        return f"Error cloning repository: {result['error']}"

@app.tool()
def git_remote(repo_path: str, action: str = "list", name: Optional[str] = None, url: Optional[str] = None) -> str:
    """
    Manage remote repositories.
    
    Args:
        repo_path: Path to the git repository
        action: Action to perform (list, add, remove, set-url)
        name: Remote name (required for add, remove, set-url)
        url: Remote URL (required for add, set-url)
        
    Returns:
        Result of the git remote operation
    """
    if action == "list":
        command = ['remote', '-v']
    elif action == "add" and name and url:
        command = ['remote', 'add', name, url]
    elif action == "remove" and name:
        command = ['remote', 'remove', name]
    elif action == "set-url" and name and url:
        command = ['remote', 'set-url', name, url]
    else:
        return "Invalid remote operation. Use 'list', 'add', 'remove', or 'set-url'"
    
    result = run_git_command(repo_path, command)
    if result['success']:
        if action == "list":
            return f"Git Remotes:\n{result['output']}" if result['output'] else "No remotes configured"
        else:
            return f"Successfully performed remote {action} operation"
    else:
        return f"Error with git remote operation: {result['error']}"

@app.tool()
def git_init(repo_path: str, bare: bool = False) -> str:
    """
    Initialize a new Git repository.
    
    Args:
        repo_path: Path where to initialize the repository
        bare: Create a bare repository (default: False)
        
    Returns:
        Result of the git init operation
    """
    command = ['init']
    if bare:
        command.append('--bare')
    
    result = run_git_command(repo_path, command)
    if result['success']:
        repo_type = "bare " if bare else ""
        return f"Successfully initialized {repo_type}Git repository in {repo_path}\n{result['output']}"
    else:
        return f"Error initializing Git repository: {result['error']}"

@app.tool()
def git_stash(repo_path: str, action: str = "push", message: Optional[str] = None, stash_name: Optional[str] = None) -> str:
    """
    Stash changes in a dirty working directory.
    
    Args:
        repo_path: Path to the git repository
        action: Stash action (push, pop, list, apply, drop)
        message: Stash message (for push action)
        stash_name: Specific stash to apply/drop (e.g., "stash@{0}")
        
    Returns:
        Result of the git stash operation
    """
    command = ['stash']
    
    if action == "push":
        command.append('push')
        if message:
            command.extend(['-m', message])
    elif action == "pop":
        command.append('pop')
        if stash_name:
            command.append(stash_name)
    elif action == "list":
        command.append('list')
    elif action == "apply":
        command.append('apply')
        if stash_name:
            command.append(stash_name)
    elif action == "drop":
        command.append('drop')
        if stash_name:
            command.append(stash_name)
    else:
        return "Invalid stash action. Use 'push', 'pop', 'list', 'apply', or 'drop'"
    
    result = run_git_command(repo_path, command)
    if result['success']:
        return f"Git stash {action} completed successfully\n{result['output']}"
    else:
        return f"Error with git stash {action}: {result['error']}"

if __name__ == "__main__":
    # Run the server on SSE transport at localhost:8681
    app.run(transport="sse", host="localhost", port=8681)
