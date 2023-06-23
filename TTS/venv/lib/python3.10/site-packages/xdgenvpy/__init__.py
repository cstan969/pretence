"""Init script for the xdgenvpy module."""

from xdgenvpy.xdgenv import XDG
from xdgenvpy.xdgenv import XDGPackage
from xdgenvpy.xdgenv import XDGPedanticPackage

# Limit namespace clobber when "import *" is used.
__all__ = (
    'XDG',
    'XDGPackage',
    'XDGPedanticPackage',
)
