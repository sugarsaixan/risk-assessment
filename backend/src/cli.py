"""CLI commands for the risk assessment system."""

import argparse
import asyncio
import secrets
import sys

from src.core.auth import hash_api_key
from src.core.database import get_session_context
from src.models.api_key import ApiKey


async def create_api_key(name: str) -> tuple[str, str]:
    """Create a new API key and store it in the database.

    Args:
        name: Descriptive name for the API key.

    Returns:
        Tuple of (plain_key, key_id).
    """
    # Generate a secure random key
    plain_key = secrets.token_urlsafe(32)

    # Hash the key for storage
    key_hash = hash_api_key(plain_key)

    # Store in database
    async with get_session_context() as session:
        api_key = ApiKey(
            key_hash=key_hash,
            name=name,
        )
        session.add(api_key)
        await session.flush()
        key_id = str(api_key.id)

    return plain_key, key_id


async def list_api_keys() -> list[dict]:
    """List all API keys (without the actual keys).

    Returns:
        List of API key info dictionaries.
    """
    from sqlalchemy import select

    async with get_session_context() as session:
        result = await session.execute(
            select(ApiKey).order_by(ApiKey.created_at.desc())
        )
        keys = result.scalars().all()

        return [
            {
                "id": str(key.id),
                "name": key.name,
                "is_active": key.is_active,
                "created_at": key.created_at.isoformat(),
                "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None,
            }
            for key in keys
        ]


async def deactivate_api_key(key_id: str) -> bool:
    """Deactivate an API key.

    Args:
        key_id: The UUID of the key to deactivate.

    Returns:
        True if key was found and deactivated.
    """
    import uuid

    from sqlalchemy import select

    async with get_session_context() as session:
        result = await session.execute(
            select(ApiKey).where(ApiKey.id == uuid.UUID(key_id))
        )
        key = result.scalar_one_or_none()

        if key is None:
            return False

        key.is_active = False
        return True


def cmd_create_key(args: argparse.Namespace) -> None:
    """Handle create-key command."""
    plain_key, key_id = asyncio.run(create_api_key(args.name))
    print(f"API Key created successfully!")
    print(f"ID: {key_id}")
    print(f"Name: {args.name}")
    print(f"Key: {plain_key}")
    print()
    print("IMPORTANT: Save this key securely. It cannot be retrieved later.")


def cmd_list_keys(args: argparse.Namespace) -> None:
    """Handle list-keys command."""
    keys = asyncio.run(list_api_keys())

    if not keys:
        print("No API keys found.")
        return

    print(f"{'ID':<36} {'Name':<20} {'Active':<8} {'Created':<20} {'Last Used':<20}")
    print("-" * 110)
    for key in keys:
        print(
            f"{key['id']:<36} "
            f"{key['name']:<20} "
            f"{'Yes' if key['is_active'] else 'No':<8} "
            f"{key['created_at'][:19]:<20} "
            f"{(key['last_used_at'] or 'Never')[:19]:<20}"
        )


def cmd_deactivate_key(args: argparse.Namespace) -> None:
    """Handle deactivate-key command."""
    success = asyncio.run(deactivate_api_key(args.id))

    if success:
        print(f"API key {args.id} has been deactivated.")
    else:
        print(f"API key {args.id} not found.")
        sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="risk-assessment",
        description="Risk Assessment Survey System CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create-key command
    create_parser = subparsers.add_parser(
        "create-key",
        help="Create a new API key",
    )
    create_parser.add_argument(
        "name",
        help="Descriptive name for the API key",
    )
    create_parser.set_defaults(func=cmd_create_key)

    # list-keys command
    list_parser = subparsers.add_parser(
        "list-keys",
        help="List all API keys",
    )
    list_parser.set_defaults(func=cmd_list_keys)

    # deactivate-key command
    deactivate_parser = subparsers.add_parser(
        "deactivate-key",
        help="Deactivate an API key",
    )
    deactivate_parser.add_argument(
        "id",
        help="UUID of the API key to deactivate",
    )
    deactivate_parser.set_defaults(func=cmd_deactivate_key)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
