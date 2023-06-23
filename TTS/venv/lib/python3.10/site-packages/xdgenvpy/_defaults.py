"""
Helper module that defines the default XDG Base Directory values.

This is designed to minimize system specific logic, effectively allowing for
Linux CI systems, like the Gitlab runners, to test as much code coverage as
possible.  This should help maximize the possibility that the Gitlab CI will
identify bugs rather than the AppVeyor environments.  The AppVeyor CI
environment is configured to test MacOS and Windows systems.
"""

from collections import defaultdict
from ntpath import pathsep as pathsep_nt
from os import getenv
from os import pathsep
from pathlib import Path
from platform import system
from posixpath import pathsep as pathsep_posix

# Determine the user's name.  If it cannot be determined through the environment
# variable, then default to something/anything.  This is standard practice for
# Unix systems, and Windows systems usually do the same.
_USER_NAME = getenv('USERNAME', 'xdgenvpy')

# Attempt to determine the user's ID number.  Not that the getuid() is a Unix
# only method.  So on Windows, default the ID number to just the user's name.
try:
    # pylint: disable=ungrouped-imports
    from os import getuid

    _USER_ID = getuid()
except ImportError:
    _USER_ID = _USER_NAME


def __unsupported_system():
    """
    :raises RuntimeError with a message identifying the unsupported system.
    """
    system_type = system()
    raise RuntimeError(f'Unknown platform: {system_type}')


# Mapping between system type and a path prefix when paths are relative.
_PREFIX_PATHS = defaultdict(__unsupported_system)
if not _PREFIX_PATHS:
    _PREFIX_PATHS.update({
        'Linux': Path('~').expanduser(),
        'Darwin': Path('~').expanduser(),
        'Windows': Path(getenv('APPDATA',
                               f'C:\\Users\\{_USER_NAME}\\AppData\\Roaming')),
    })

# Mapping between system type and multiple directory path separators.
_PATH_SEPARATORS = defaultdict(__unsupported_system)
if not _PATH_SEPARATORS:
    _PATH_SEPARATORS.update({
        'Linux': pathsep_posix,
        'Darwin': pathsep_posix,
        'Windows': pathsep_nt,
    })


def _get_system_default(linux, mac, windows, multiple_dirs, system_type):
    """
    Depending on the system type, this method will take the system specified
    directories, split them up based on the system's path separator, and finally
    return an immutable sequence of paths.

    :param str linux: The Linux default value.
    :param str mac: The Mac OS default value.
    :param str windows: The Windows default value.
    :param bool multiple_dirs: Flag indicating if normalization should process
        the default value as a path separated list of multiple directories.
    :param str system_type: The system type as reported by :meth:`os.system()`.

    :rtype: tuple
    :returns: A sequence of directories based on the system type.
    """
    dirs = defaultdict(__unsupported_system)
    dirs.update({
        'Linux': linux,
        'Darwin': mac,
        'Windows': windows,
    })
    dirs = dirs.get(system_type)

    if multiple_dirs:
        path_sep = _PATH_SEPARATORS[system_type]
        dirs = dirs.split(path_sep)

    if isinstance(dirs, str):
        dirs = tuple([dirs])

    return tuple(dirs)


def _normalize(linux, mac, windows, multiple_dirs):
    """
    Given the defaults for Linux, Mac OS, and Windows based systems, this
    function determines which system specific default value to use, normalize
    the paths with path prefixes, and lastly it will potentially combine
    multiple directories into a single string.

    :param str linux: The Linux default value.
    :param str mac: The Mac OS default value.
    :param str windows: The Windows default value.
    :param bool multiple_dirs: Flag indicating if normalization should process
        the default value as a path separated list of multiple directories.

    :rtype: str
    :returns: A string containing a normalized default value for the current
        system.
    """
    system_type = system()
    prefix_path = _PREFIX_PATHS[system_type]
    dirs = _get_system_default(linux, mac, windows, multiple_dirs, system_type)
    dirs = [prefix_path.joinpath(d).as_posix() for d in dirs]
    normalized = str(_PATH_SEPARATORS[system_type]).join(dirs)
    return normalized


def system_path_separator():
    """ :returns: The platform specific path separator. """
    return pathsep


def XDG_DATA_HOME():
    """
    :rtype: str
    :returns: The spec defined value for the :code:`XDG_DATA_HOME` variable.
    """
    return _normalize(linux='.local/share',
                      mac='.local/share',
                      windows='local/share',
                      multiple_dirs=False)


def XDG_CONFIG_HOME():
    """
    :rtype: str
    :returns: The spec defined value for the :code:`XDG_CONFIG_HOME` variable.
    """
    return _normalize(linux='.config',
                      mac='.config',
                      windows='config',
                      multiple_dirs=False)


def XDG_CACHE_HOME():
    """
    :rtype: str
    :returns: The spec defined value for the :code:`XDG_CACHE_HOME` variable.
    """
    return _normalize(linux='.cache',
                      mac='.cache',
                      windows='cache',
                      multiple_dirs=False)


def XDG_RUNTIME_DIR():
    """
    :rtype: str
    :returns: The spec defined value for the :code:`XDG_RUNTIME_DIR` variable.
    """
    return _normalize(linux=f'/run/user/{_USER_ID}',
                      mac=f'/tmp/run/user/{_USER_ID}',
                      windows=f'run/user/{_USER_NAME}',
                      multiple_dirs=False)


def XDG_DATA_DIRS():
    """
    :rtype: str
    :returns: The spec defined value for the :code:`XDG_DATA_DIRS` variable.
    """
    return _normalize(linux='/usr/local/share:/usr/share',
                      mac='/usr/local/share:/usr/share',
                      windows='usr/share/',
                      multiple_dirs=True)


def XDG_CONFIG_DIRS():
    """
    :rtype: str
    :returns: The spec defined value for the :code:`XDG_CONFIG_DIRS` variable.
    """
    return _normalize(linux='/etc/xdg',
                      mac='/etc/xdg',
                      windows='etc/xdg',
                      multiple_dirs=True)
