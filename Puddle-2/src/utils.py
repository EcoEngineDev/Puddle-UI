"""Utility helpers for Puddle 2."""

from __future__ import annotations

import logging

LOG = logging.getLogger(__name__)


def ensure_singleton(instance_name: str) -> None:
    """Placeholder singleton helper to be expanded as features grow."""
    LOG.debug("ensure_singleton called for %s (implementation pending)", instance_name)
