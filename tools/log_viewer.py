#!/usr/bin/env python3
# tools/log_viewer.py

"""
CLI tool for viewing conversation logs from the voice assistant database.

Usage:
    python tools/log_viewer.py                    # Show last 10 conversations
    python tools/log_viewer.py -n 50              # Show last 50 conversations
    python tools/log_viewer.py --search "weather" # Search for keyword
    python tools/log_viewer.py --since 2025-10-01 # Show conversations from date
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.insert(0, str(Path(__file__).parent.parent))

import config
from components import db_manager


def format_conversation(conv: dict) -> str:
    """
    Format a single conversation for display.

    Args:
        conv: Conversation dictionary from database

    Returns:
        Formatted string representation
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"ID: {conv['id']} | {conv['created_at']} | Status: {conv['status']}")
    lines.append("-" * 80)

    if conv['user_input']:
        lines.append(f"User: {conv['user_input']}")
    else:
        lines.append("User: [No input captured]")

    lines.append("")

    if conv['status'] == 'completed' and conv['assistant_response']:
        lines.append(f"Assistant: {conv['assistant_response']}")
    elif conv['status'] == 'failed':
        lines.append("Assistant: [Failed to generate response]")
        if conv['error_message']:
            lines.append(f"Error: {conv['error_message']}")
    else:
        lines.append("Assistant: [No response]")

    lines.append("")

    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="View conversation logs from the voice assistant database"
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=10,
        help="Maximum number of conversations to display (default: 10)"
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Search for keyword in user input or assistant response"
    )
    parser.add_argument(
        "--since",
        type=str,
        help="Show conversations from this date onwards (format: YYYY-MM-DD)"
    )

    args = parser.parse_args()

    # Check if logging is enabled
    if not config.LOGGING_ENABLED:
        print("Error: Conversation logging is disabled (LOGGING_ENABLED=False)", file=sys.stderr)
        print("Enable logging in your .env file or environment variables", file=sys.stderr)
        sys.exit(1)

    # Check if database file exists
    db_path = Path(config.LOGGING_DB_PATH)
    if not db_path.exists():
        print(f"Error: Database file not found at {config.LOGGING_DB_PATH}", file=sys.stderr)
        print("Run the voice assistant at least once to create the database", file=sys.stderr)
        sys.exit(1)

    # Query conversations
    try:
        conversations = db_manager.get_conversations(
            limit=args.limit,
            search=args.search,
            start_date=args.since
        )
    except Exception as e:
        print(f"Error: Failed to query conversations: {e}", file=sys.stderr)
        sys.exit(1)

    # Display results
    if not conversations:
        print("No conversations found.")
        if args.search:
            print(f"Try removing the search filter: --search '{args.search}'")
        if args.since:
            print(f"Try removing the date filter: --since '{args.since}'")
        sys.exit(0)

    print(f"\nShowing {len(conversations)} conversation(s):\n")

    for conv in conversations:
        print(format_conversation(conv))

    print("=" * 80)
    print(f"\nTotal: {len(conversations)} conversation(s)")


if __name__ == "__main__":
    main()
