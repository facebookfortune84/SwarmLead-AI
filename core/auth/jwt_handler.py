"""
JWT token handling - Core auth module.

Re-exports decode_token from interfaces.api.auth.jwt_handler
to maintain clean dependency boundaries.
"""

from interfaces.api.auth.jwt_handler import decode_token, verify_token

__all__ = ["decode_token", "verify_token"]