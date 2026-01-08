"""
SpineHUB Git Manager Module

Intelligent Git versioning with auto-commit, branch management, and PR creation.
Usage: python git_manager.py [command] [options]
"""

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


class GitManager:
    """Intelligent Git operations for SpineHUB projects."""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.git_dir = self.repo_path / ".git"

        if not self.git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

    def run_git(self, *args, capture: bool = True) -> subprocess.CompletedProcess:
        """Run a git command."""
        cmd = ["git"] + list(args)
        return subprocess.run(
            cmd,
            cwd=self.repo_path,
            capture_output=capture,
            text=True,
        )

    # =========================================
    # STATUS & INFO
    # =========================================

    def get_status(self) -> dict:
        """Get comprehensive git status."""
        status = {
            "branch": self.get_current_branch(),
            "remote": self.get_remote_url(),
            "clean": self.is_clean(),
            "staged": [],
            "unstaged": [],
            "untracked": [],
            "ahead": 0,
            "behind": 0,
        }

        # Get file status
        result = self.run_git("status", "--porcelain")
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                status_code = line[:2]
                filename = line[3:]

                if status_code[0] in "MADRC":
                    status["staged"].append(filename)
                if status_code[1] in "MD":
                    status["unstaged"].append(filename)
                if status_code == "??":
                    status["untracked"].append(filename)

        # Get ahead/behind
        result = self.run_git("rev-list", "--count", "--left-right", "@{u}...HEAD")
        if result.returncode == 0:
            parts = result.stdout.strip().split("\t")
            if len(parts) == 2:
                status["behind"] = int(parts[0])
                status["ahead"] = int(parts[1])

        return status

    def get_current_branch(self) -> str:
        """Get current branch name."""
        result = self.run_git("rev-parse", "--abbrev-ref", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else "unknown"

    def get_remote_url(self) -> str:
        """Get remote URL."""
        result = self.run_git("remote", "get-url", "origin")
        return result.stdout.strip() if result.returncode == 0 else ""

    def is_clean(self) -> bool:
        """Check if working directory is clean."""
        result = self.run_git("status", "--porcelain")
        return result.returncode == 0 and not result.stdout.strip()

    def get_last_commits(self, count: int = 5) -> list:
        """Get last N commits."""
        result = self.run_git("log", f"-{count}", "--oneline", "--format=%h|%s|%an|%ar")
        commits = []
        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                        })
        return commits

    # =========================================
    # COMMIT OPERATIONS
    # =========================================

    def add_all(self) -> bool:
        """Stage all changes."""
        result = self.run_git("add", "-A")
        return result.returncode == 0

    def commit(self, message: str) -> dict:
        """Create a commit."""
        result = self.run_git("commit", "-m", message)

        if result.returncode == 0:
            # Get the commit hash
            hash_result = self.run_git("rev-parse", "--short", "HEAD")
            return {
                "success": True,
                "hash": hash_result.stdout.strip(),
                "message": message,
            }
        else:
            return {
                "success": False,
                "error": result.stderr.strip() or result.stdout.strip(),
            }

    def auto_commit(self, prefix: str = "update") -> dict:
        """
        Create an intelligent auto-commit with contextual message.

        Analyzes changes and generates appropriate commit message.
        """
        status = self.get_status()

        if status["clean"]:
            return {"success": False, "error": "Nothing to commit"}

        # Stage all changes
        self.add_all()

        # Analyze changes for message
        message = self._generate_commit_message(prefix, status)

        return self.commit(message)

    def _generate_commit_message(self, prefix: str, status: dict) -> str:
        """Generate intelligent commit message based on changes."""
        all_files = status["staged"] + status["unstaged"] + status["untracked"]

        # Categorize changes
        categories = {
            "docs": [],
            "config": [],
            "src": [],
            "test": [],
            "other": [],
        }

        for f in all_files:
            f_lower = f.lower()
            if f_lower.endswith((".md", ".txt", ".rst")):
                categories["docs"].append(f)
            elif f_lower.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env")):
                categories["config"].append(f)
            elif "test" in f_lower:
                categories["test"].append(f)
            elif f_lower.endswith((".py", ".ts", ".js", ".tsx", ".jsx")):
                categories["src"].append(f)
            else:
                categories["other"].append(f)

        # Build message
        parts = []

        if categories["docs"]:
            parts.append(f"docs({len(categories['docs'])} files)")
        if categories["config"]:
            parts.append(f"config({len(categories['config'])} files)")
        if categories["src"]:
            parts.append(f"code({len(categories['src'])} files)")
        if categories["test"]:
            parts.append(f"test({len(categories['test'])} files)")

        if parts:
            detail = ", ".join(parts)
            message = f"{prefix}: {detail}"
        else:
            message = f"{prefix}: {len(all_files)} file(s) changed"

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message += f" [{timestamp}]"

        return message

    def consolidar_commit(self, summary: str = None) -> dict:
        """
        Create a consolidation commit (end of session).

        Format: consolidar: [summary] [YYYY-MM-DD HH:MM]
        """
        status = self.get_status()

        if status["clean"]:
            return {"success": False, "error": "Nothing to commit"}

        self.add_all()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        if summary:
            message = f"consolidar: {summary} [{timestamp}]"
        else:
            # Generate summary from changes
            total_files = len(status["staged"]) + len(status["unstaged"]) + len(status["untracked"])
            message = f"consolidar: session update ({total_files} files) [{timestamp}]"

        return self.commit(message)

    # =========================================
    # PUSH/PULL OPERATIONS
    # =========================================

    def push(self, force: bool = False, set_upstream: bool = False) -> dict:
        """Push to remote."""
        args = ["push"]

        if set_upstream:
            branch = self.get_current_branch()
            args.extend(["-u", "origin", branch])
        elif force:
            args.append("--force-with-lease")

        result = self.run_git(*args)

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
        }

    def pull(self, rebase: bool = False) -> dict:
        """Pull from remote."""
        args = ["pull"]
        if rebase:
            args.append("--rebase")

        result = self.run_git(*args)

        return {
            "success": result.returncode == 0,
            "output": result.stdout.strip() or result.stderr.strip(),
        }

    # =========================================
    # BRANCH OPERATIONS
    # =========================================

    def create_branch(self, name: str, checkout: bool = True) -> dict:
        """Create a new branch."""
        if checkout:
            result = self.run_git("checkout", "-b", name)
        else:
            result = self.run_git("branch", name)

        return {
            "success": result.returncode == 0,
            "branch": name,
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }

    def checkout(self, branch: str) -> dict:
        """Checkout a branch."""
        result = self.run_git("checkout", branch)

        return {
            "success": result.returncode == 0,
            "branch": branch,
            "error": result.stderr.strip() if result.returncode != 0 else None,
        }

    def list_branches(self) -> list:
        """List all branches."""
        result = self.run_git("branch", "-a", "--format=%(refname:short)")
        if result.returncode == 0:
            return [b.strip() for b in result.stdout.strip().split("\n") if b.strip()]
        return []

    # =========================================
    # PR OPERATIONS (via gh CLI)
    # =========================================

    def create_pr(self, title: str, body: str, base: str = "main", draft: bool = False) -> dict:
        """Create a pull request using gh CLI."""
        args = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]

        if draft:
            args.append("--draft")

        result = subprocess.run(args, cwd=self.repo_path, capture_output=True, text=True)

        if result.returncode == 0:
            # Extract PR URL from output
            url = result.stdout.strip()
            return {"success": True, "url": url}
        else:
            return {"success": False, "error": result.stderr.strip()}

    def list_prs(self, state: str = "open") -> list:
        """List pull requests."""
        result = subprocess.run(
            ["gh", "pr", "list", "--state", state, "--json", "number,title,state,url"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        return []

    # =========================================
    # UTILITY METHODS
    # =========================================

    def get_diff_stats(self) -> dict:
        """Get diff statistics."""
        result = self.run_git("diff", "--stat")
        stats = {"files": 0, "insertions": 0, "deletions": 0}

        if result.returncode == 0 and result.stdout:
            # Parse last line for summary
            lines = result.stdout.strip().split("\n")
            if lines:
                last_line = lines[-1]
                # Parse: "X files changed, Y insertions(+), Z deletions(-)"
                match = re.search(r"(\d+) files? changed", last_line)
                if match:
                    stats["files"] = int(match.group(1))
                match = re.search(r"(\d+) insertions?", last_line)
                if match:
                    stats["insertions"] = int(match.group(1))
                match = re.search(r"(\d+) deletions?", last_line)
                if match:
                    stats["deletions"] = int(match.group(1))

        return stats

    def format_status_report(self) -> str:
        """Format a human-readable status report."""
        status = self.get_status()
        commits = self.get_last_commits(3)

        lines = [
            f"Branch: {status['branch']}",
            f"Remote: {status['remote'] or 'not set'}",
            f"Status: {'clean' if status['clean'] else 'dirty'}",
        ]

        if status["ahead"] or status["behind"]:
            lines.append(f"Sync: {status['ahead']} ahead, {status['behind']} behind")

        if status["staged"]:
            lines.append(f"Staged: {len(status['staged'])} file(s)")
        if status["unstaged"]:
            lines.append(f"Unstaged: {len(status['unstaged'])} file(s)")
        if status["untracked"]:
            lines.append(f"Untracked: {len(status['untracked'])} file(s)")

        if commits:
            lines.append("\nRecent commits:")
            for c in commits[:3]:
                lines.append(f"  {c['hash']} {c['message'][:50]}")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="SpineHUB Git Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Status command
    subparsers.add_parser("status", help="Show git status")

    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Create a commit")
    commit_parser.add_argument("--message", "-m", help="Commit message")
    commit_parser.add_argument("--auto", "-a", action="store_true", help="Auto-generate message")
    commit_parser.add_argument("--prefix", "-p", default="update", help="Message prefix for auto")

    # Consolidar command
    consolidar_parser = subparsers.add_parser("consolidar", help="Create consolidation commit")
    consolidar_parser.add_argument("--summary", "-s", help="Session summary")

    # Push command
    push_parser = subparsers.add_parser("push", help="Push to remote")
    push_parser.add_argument("--force", "-f", action="store_true", help="Force push")
    push_parser.add_argument("--upstream", "-u", action="store_true", help="Set upstream")

    # Pull command
    pull_parser = subparsers.add_parser("pull", help="Pull from remote")
    pull_parser.add_argument("--rebase", "-r", action="store_true", help="Pull with rebase")

    # Branch command
    branch_parser = subparsers.add_parser("branch", help="Branch operations")
    branch_parser.add_argument("name", nargs="?", help="Branch name")
    branch_parser.add_argument("--list", "-l", action="store_true", help="List branches")
    branch_parser.add_argument("--checkout", "-c", action="store_true", help="Checkout branch")

    # PR command
    pr_parser = subparsers.add_parser("pr", help="Pull request operations")
    pr_parser.add_argument("--create", action="store_true", help="Create PR")
    pr_parser.add_argument("--title", "-t", help="PR title")
    pr_parser.add_argument("--body", "-b", help="PR body")
    pr_parser.add_argument("--list", "-l", action="store_true", help="List PRs")

    args = parser.parse_args()

    try:
        gm = GitManager()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    if args.command == "status":
        print(gm.format_status_report())

    elif args.command == "commit":
        if args.auto:
            result = gm.auto_commit(prefix=args.prefix)
        elif args.message:
            gm.add_all()
            result = gm.commit(args.message)
        else:
            print("Error: Provide --message or use --auto")
            return 1

        if result["success"]:
            print(f"[OK] Commit {result['hash']}: {result['message']}")
        else:
            print(f"[ERROR] {result['error']}")

    elif args.command == "consolidar":
        result = gm.consolidar_commit(summary=args.summary)
        if result["success"]:
            print(f"[OK] Consolidation commit: {result['hash']}")
        else:
            print(f"[ERROR] {result['error']}")

    elif args.command == "push":
        result = gm.push(force=args.force, set_upstream=args.upstream)
        if result["success"]:
            print("[OK] Pushed successfully")
        else:
            print(f"[ERROR] {result['output']}")

    elif args.command == "pull":
        result = gm.pull(rebase=args.rebase)
        print(result["output"])

    elif args.command == "branch":
        if args.list:
            for b in gm.list_branches():
                print(f"  {b}")
        elif args.name:
            if args.checkout:
                result = gm.checkout(args.name)
            else:
                result = gm.create_branch(args.name)

            if result["success"]:
                print(f"[OK] Branch: {result['branch']}")
            else:
                print(f"[ERROR] {result['error']}")

    elif args.command == "pr":
        if args.list:
            prs = gm.list_prs()
            for pr in prs:
                print(f"  #{pr['number']} {pr['title']} ({pr['state']})")
        elif args.create:
            if not args.title:
                print("Error: --title required")
                return 1
            result = gm.create_pr(args.title, args.body or "")
            if result["success"]:
                print(f"[OK] PR created: {result['url']}")
            else:
                print(f"[ERROR] {result['error']}")

    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    exit(main())
