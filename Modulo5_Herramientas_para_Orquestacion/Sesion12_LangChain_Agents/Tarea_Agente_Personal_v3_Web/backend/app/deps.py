"""Punto unico de acceso al modulo de v2 ya importado (ver config.py)."""

from app.config import v2mod


def get_v2():
    return v2mod
