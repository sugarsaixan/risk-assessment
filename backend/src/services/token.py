"""Service for generating and hashing assessment tokens."""

import hashlib
import secrets


class TokenService:
    """Service for generating secure tokens and their hashes.

    Tokens are used for public assessment URLs. We store only the hash
    in the database for security.
    """

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token.

        Args:
            length: Number of random bytes (default 32 = 256 bits).

        Returns:
            URL-safe base64 encoded token (43 characters for 32 bytes).
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        """Create SHA-256 hash of a token.

        Args:
            token: The plain text token.

        Returns:
            Hexadecimal SHA-256 hash (64 characters).
        """
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def generate_token_pair() -> tuple[str, str]:
        """Generate a token and its hash.

        Returns:
            Tuple of (plain_token, token_hash).
            - Store token_hash in database
            - Return plain_token to admin for URL generation
        """
        token = TokenService.generate_token()
        token_hash = TokenService.hash_token(token)
        return token, token_hash

    @staticmethod
    def verify_token(token: str, token_hash: str) -> bool:
        """Verify a token against its stored hash.

        Args:
            token: The plain text token to verify.
            token_hash: The stored hash to compare against.

        Returns:
            True if the token matches the hash.
        """
        return secrets.compare_digest(
            TokenService.hash_token(token),
            token_hash,
        )
