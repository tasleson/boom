# Copyright (C) 2017 Red Hat, Inc., Bryn M. Reeves <bmr@redhat.com>
#
# boom/__init__.py - Boom package initialisation
#
# This file is part of the boom project.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
from os.path import exists as path_exists, isabs, join as path_join
import logging

__version__ = "0.1"

#: The location of the system ``/boot`` directory.
DEFAULT_BOOT_PATH = "/boot"
__boot_root = DEFAULT_BOOT_PATH

#: The default path for Boom configuration files.
_DEFAULT_BOOM_DIR = "boom"

#: The root directory for Boom configuration files.
DEFAULT_BOOM_PATH = path_join(DEFAULT_BOOT_PATH, _DEFAULT_BOOM_DIR)
__boom_root = DEFAULT_BOOM_PATH

#: Kernel version string, in ``uname -r`` format.
FMT_VERSION = "version"
#: LVM2 root logical volume in ``vg/lv`` format.
FMT_LVM_ROOT_LV = "lvm_root_lv"
#: BTRFS subvolume specification.
FMT_BTRFS_SUBVOLUME = "btrfs_subvolume"
#: BTRFS subvolume ID specification.
FMT_BTRFS_SUBVOL_ID = "btrfs_subvol_id"
#: BTRFS subvolume path specification.
FMT_BTRFS_SUBVOL_PATH = "btrfs_subvol_path"
#: Root device path.
FMT_ROOT_DEVICE = "root_device"
#: Root device options.
FMT_ROOT_OPTS = "root_opts"

#: List of all possible format keys.
FORMAT_KEYS = [
    FMT_VERSION,
    FMT_LVM_ROOT_LV,
    FMT_BTRFS_SUBVOL_ID, FMT_BTRFS_SUBVOL_PATH,
    FMT_BTRFS_SUBVOLUME,
    FMT_ROOT_DEVICE, FMT_ROOT_OPTS
]

_MACHINE_ID = "/etc/machine-id"

BOOM_LOG_DEBUG = logging.DEBUG
BOOM_LOG_INFO = logging.INFO
BOOM_LOG_WARN = logging.WARNING
BOOM_LOG_ERROR = logging.ERROR

_log_levels = (
    BOOM_LOG_DEBUG,
    BOOM_LOG_INFO,
    BOOM_LOG_WARN,
    BOOM_LOG_ERROR
)

_log = logging.getLogger(__name__)

_log_debug = _log.debug
_log_info = _log.info
_log_warn = _log.warning
_log_error = _log.error

# Boom debugging levels
BOOM_DEBUG_PROFILE = 1
BOOM_DEBUG_ENTRY = 2
BOOM_DEBUG_REPORT = 4
BOOM_DEBUG_COMMAND = 8
BOOM_DEBUG_ALL = (BOOM_DEBUG_PROFILE |
                  BOOM_DEBUG_ENTRY |
                  BOOM_DEBUG_REPORT |
                  BOOM_DEBUG_COMMAND)

__debug_mask = 0

def get_debug_mask():
    return __debug_mask


def set_debug_mask(mask):
    global __debug_mask
    if mask < 0 or mask > BOOM_DEBUG_ALL:
        raise ValueError("Invalid boom debug mask: %d" % mask)
    __debug_mask = mask


def get_boot_path():
    """get_boot_path() -> str

        Return the currently configured boot file system path.
        :returns: the path to the /boot file system.
        :returntype: str
    """
    return __boot_root

def get_boom_path():
    """get_boom_path() -> str

        Return the currently configured boom configuration path.
        :returns: the path to the BOOT/boom directory.
        :returntype: str
    """
    return __boom_root

def set_boot_path(boot_path):
    """set_boot_root(boot_path) -> None

        Set the location of the boot file system to ``boot_path``.
        The path defaults to the '/boot/' mount directory in the root
        file system: this may be overridden by calling this function
        with a different path.

        Calling ``set_boom_root_path()`` will re-set the value returned
        by ``get_boom_path()`` to the default boom configuration sub-
        directory within the new boot file system. The location of the
        boom configuration path may be configured separately by calling
        ``set_boom_root_path()`` after setting the boot path.

        :param boot_path: the path to the 'boom/' directory containing
                          boom profiles and configuration.
        :returns: ``None``
        :raises: ValueError if ``boot_path`` does not exist.
    """
    global __boot_root, __boom_root
    if not isabs(boot_path):
        raise ValueError("boot_path must be an absolute path: %s" % boot_path)

    if not path_exists(boot_path):
        raise ValueError("Path '%s' does not exist" % boot_path)

    __boot_root = boot_path
    _log_debug("Set boot path to: %s" % __boot_root)
    __boom_root = path_join(boot_path, _DEFAULT_BOOM_DIR)
    _log_debug("Set boom path to: %s" % __boom_root)


def set_boom_path(root_path):
    """set_boom_root_path(root_path) -> None

        Set the location of the boom configuration path stored in
        ``__boom_root`` to ``root_path``. ``__boom_root`` defaults to the
        'boom/' sub-directory in the boot file system specified by
        ``__boot_root``: this may be overridden by calling this function
        with a different path.

        Paths must be set before importing any other boom API module:
        changes are not automatically propagated to sub-modules.

        :param root_path: the path to the 'boom/' directory containing
                          boom profiles and configuration.
        :returns: ``None``
        :raises: ValueError if ``root_path`` does not exist.
    """
    global __boot_root, __boom_root
    if isabs(root_path) and not path_exists(root_path):
        raise ValueError("Root path %s does not exist" % root_path)
    elif not path_exists(path_join(__boot_root, root_path)):
        raise ValueError("Root path %s does not exist" % root_path)

    if not isabs(root_path):
        root_path = path_join(__boot_root, root_path)

    if not path_exists(path_join(root_path, "profiles")):
        raise ValueError("Root path is not a boom configuration path.")

    _log_debug("Set boom path to: %s" % _DEFAULT_BOOM_DIR)
    __boom_root = root_path


def _parse_btrfs_subvol(subvol):
    """_parse_btrfs_subvol(subvol) -> str

        Parse a BTRFS subvolume specification into either a subvolume
        path string, or a string containing a subvolume identifier.

        :param subvol: The subvolume parameter to parse
        :returns: A string containing the subvolume path or ID
        :returntype: ``str``
        :raises: ValueError if no valid subvolume was found
    """
    if not subvol:
        return None

    subvol_id = None
    try:
        subvol_id = int(subvol)
        subvol = str(subvol_id)
    except ValueError:
        if not subvol.startswith('/'):
            raise ValueError("Unrecognised BTRFS subvolume: %s" % subvol)
    return subvol


#
# Selection criteria class
#

class Selection(object):
    """Selection()
        Selection criteria for boom BootEntry, OsProfile and BootParams.

        Selection criteria specified as a simple boolean AND of all
        criteria with a non-None value.
    """

    # BootEntry fields
    boot_id = None
    title = None
    version = None
    machine_id = None
    linux = None
    initrd = None
    efi = None
    options = None
    devicetree = None

    # BootParams fields
    root_device = None
    lvm_root_lv = None
    btrfs_subvol_path = None
    btrfs_subvol_id = None

    # OsProfile fields
    os_id = None
    os_name = None
    os_short_name = None
    os_version = None
    os_version_id = None
    os_uname_pattern = None
    os_kernel_pattern = None
    os_initramfs_pattern = None
    os_root_opts_lvm2 = None
    os_root_opts_btrfs = None
    os_options = None

    entry_attrs = [
        "boot_id", "title", "version", "machine_id", "linux", "initrd", "efi",
        "options", "devicetree"
    ]

    params_attrs = [
        "root_device", "lvm_root_lv", "btrfs_subvol_path", "btrfs_subvol_id"
    ]

    profile_attrs = [
        "os_id", "os_name", "os_short_name", "os_version", "os_version_id",
        "os_uname_pattern", "os_kernel_pattern", "os_initramfs_pattern",
        "os_root_opts_lvm2", "os_root_opts_btrfs", "os_options"
    ]

    def __str__(self):
        all_attrs = self.entry_attrs + self.params_attrs + self.profile_attrs
        attrs = [attr for attr in all_attrs if self.__attr_has_value(attr)]
        strval = ""
        tail = ", "
        for attr in attrs:
            strval += "%s='%s'%s" % (attr, getattr(self, attr), tail)
        return strval.rstrip(tail)

    def __repr__(self):
        return "Selection(" + str(self) + ")"

    def __init__(self, boot_id=None, title=title, version=version,
                 machine_id=None, linux=None, initrd=None,
                 efi=None, root_device=None, lvm_root_lv=None,
                 btrfs_subvol_path=None, btrfs_subvol_id=None,
                 os_id=None, os_name=None, os_short_name=None,
                 os_version=None, os_version_id=None, os_options=None,
                 os_uname_pattern=None, kernel_pattern=None,
                 initramfs_pattern=None):
        """__init__(self, boot_id, title=title, version=version,
                    machine_id, linux, initrd, efi,
                    root_device, lvm_root_lv, btrfs_subvol_path,
                    btrfs_subvol_id, os_id, os_name, os_short_name,
                    os_version, os_version_id, os_options) -> Selection

            Initialise a new Selection object with the specified selection
            criteria.
        """
        self.boot_id = boot_id
        self.title = title
        self.version = version
        self.machine_id = machine_id
        self.linux = linux
        self.initrd = initrd
        self.efi = efi
        self.root_device = root_device
        self.lvm_root_lv = lvm_root_lv
        self.btrfs_subvol_path = btrfs_subvol_path
        self.btrfs_subvol_id = btrfs_subvol_id
        self.os_id = os_id
        self.os_name = os_name
        self.os_short_name = os_short_name
        self.os_version = os_version
        self.os_version_id = os_version_id
        self.os_options = os_options
        self.os_uname_pattern = os_uname_pattern
        self.os_kernel_pattern = kernel_pattern
        self.os_initramfs_pattern = initramfs_pattern

    @classmethod
    def from_cmd_args(cls, args):
        """from_cmd_args(args) -> Selection

            Construct a new ``Selection`` object from the command line
            arguments in ``cmd_args``.
        """
        subvol = _parse_btrfs_subvol(args.btrfs_subvolume)
        if subvol and subvol.startswith('/'):
            btrfs_subvol_path = subvol
            btrfs_subvol_id = None
        elif subvol:
            btrfs_subvol_id = subvol
            btrfs_subvol_path = None
        else:
            btrfs_subvol_id = btrfs_subvol_path = None

        s = Selection(boot_id=args.boot_id, title=args.title,
                      version=args.version, machine_id=args.machine_id,
                      linux=args.linux, initrd=args.initrd, efi=args.efi,
                      root_device=args.root_device,
                      lvm_root_lv=args.rootlv,
                      btrfs_subvol_path=btrfs_subvol_path,
                      btrfs_subvol_id=btrfs_subvol_id,
                      os_id=args.profile, os_name=args.name,
                      os_short_name=args.short_name,
                      os_version=args.os_version,
                      os_options=args.os_options,
                      os_uname_pattern=args.uname_pattern)

        _log_debug("Initialised %s from arguments" % repr(s))
        return s

    def __attr_has_value(self, attr):
        return hasattr(self, attr) and getattr(self, attr) is not None

    def check_valid_selection(self, entry=False, params=False, profile=False):
        """check_valid_selection(entry, params, profile) -> None

            Check this ``Selection`` object to ensure it contains only
            criteria that are valid for the specified object type(s).

            Returns ``None`` if the object passes the check, or raise
            ``ValueError`` if invalid criteria exist.

            :param entry: ``Selection`` may include BootEntry data
            :param params: ``Selection`` may include BootParams data
            :param profile: ``Selection`` may include OsProfile data
            :returns: ``None`` on success
            :returntype: ``NoneType``
            :raises: ``ValueError`` if excluded criteria are present
        """

        all_attrs = self.entry_attrs + self.params_attrs + self.profile_attrs
        valid_attrs = []
        invalid_attrs = []

        if entry:
            valid_attrs += self.entry_attrs
        if entry or params:
            valid_attrs += self.params_attrs
        if profile:
            valid_attrs += self.profile_attrs

        for attr in all_attrs:
            if self.__attr_has_value(attr) and attr not in valid_attrs:
                invalid_attrs.append(attr)

        if invalid_attrs:
            invalid = ", ".join(invalid_attrs)
            raise ValueError("Invalid criteria for selection type: %s" %
                             invalid)

    def is_null(self):
        all_attrs = self.entry_attrs + self.params_attrs + self.profile_attrs
        attrs = [attr for attr in all_attrs if self.__attr_has_value(attr)]
        return not any(attrs)

#
# Generic routines for parsing name-value pairs.
#

def _blank_or_comment(line):
    """_blank_or_comment(line) -> bool

        Test whether the ``line`` argument is either blank, or a
        whole-line comment.

        :param line: the line of text to be checked.
        :returns: ``True`` if the line is blank or a comment,
                  and ``False`` otherwise.
        :returntype: bool
    """
    return not line.strip() or line.lstrip().startswith('#')


def _parse_name_value(nvp, separator="="):
    """_parse_name_value(nvp) -> (name, value)
        Parse a ``name='value'`` style string into its component parts,
        stripping quotes from the value if necessary, and return the
        result as a (name, value) tuple.

        :param nvp: A name value pair optionally with an in-line
                    comment.
        :param separator: The separator character used in this name
                          value pair, or ``None`` to splir on white
                          space.
        :returns: A ``(name, value)`` tuple.
        :returntype: (string, string) tuple.
    """
    val_err = ValueError("Malformed name/value pair: %s" % nvp)
    try:
        # Only strip newlines: values may contain embedded
        # whitespace anywhere within the string.
        name, value = nvp.rstrip('\n').split(separator, 1)
    except:
        raise val_err

    # Value cannot start with '='
    if value.startswith('='):
        raise val_err

    invalid_name_chars = [
        '!', '+', '~', '#', '@', '"', "'", '$', '%', '^', '&', '*',
        '(', ')', '{', '}', '?', '<', '>', '/', '\\', '[', ']', ',',
        '|', '=', "'", ':', ';'
    ]
    if any([v for v in invalid_name_chars if v in name]):
        raise ValueError("Invalid characters in name: %s" % name)

    # FIXME: support preservation of in-line comments for profiles
    # (BLS currently only allows whole line comments).
    if "#" in value:
        value, comment = value.split("#", 1)

    name = name.strip()
    value = value.lstrip()
    if value.startswith('"') or value.startswith("'"):
        value = value[1:-1]
    return (name, value)

def _key_regex_from_format(fmt, capture=False):
    """_key_regex_from_format(self, fmt) -> str

        Generate a regular expression to match formatted instances
        of format string ``fmt``. The expression is constructed by
        replacing all format keys with the pattern ".*".

        If the ``capture`` argument is True, capture groups will
        be inserted around each replaced substitution.

        :param fmt: The format string to build an expression from.
        :returns: A regular expression matching instances of
                  ``fmt``.
        :returntype: str
    """
    key_format = "%%{%s}"
    regex_all = "(\S*)" if capture else "\S*"

    def _make_key_regex(spaces=0):
        regex = r'(' if capture else r''
        regex += r'\S*'
        while spaces:
            regex += r' ?\S*'
            spaces -= 1
        regex += r')' if capture else r''
        return regex

    if not fmt:
        return ""

    _key_spaces = {
        FMT_VERSION: 0,
        FMT_LVM_ROOT_LV: 0,
        FMT_BTRFS_SUBVOL_ID: 0,
        FMT_BTRFS_SUBVOL_PATH: 0,
        FMT_BTRFS_SUBVOLUME: 0,
        FMT_ROOT_DEVICE: 0,
        FMT_ROOT_OPTS: 1
    }

    for key in FORMAT_KEYS:
        if key in fmt:
            regex = _make_key_regex(spaces=_key_spaces[key])
            key = key_format % key
            fmt = fmt.replace(key, regex)

    # Ignore whitespace variations
    out_fmt = ""
    for word in fmt.split():
        out_fmt += word + "\s*"

    return out_fmt


def _find_minimum_sha_prefix(shas, min_prefix):
    """_find_minimum_sha_prefix(shas) -> int

        Find the minimum unique prefix for the set of SHA IDs in the set
        ``shas``.

        :param shas: A set of SHA IDs
        :returns: The minimum unique prefix length for the set
        :returntype: int
    """
    shas = list(shas)
    shas.sort()
    for sha in shas:
        if shas.index(sha) == len(shas) - 1:
            continue
        def _next_sha(shas, sha):
            return shas[shas.index(sha) + 1]
        while sha[:min_prefix] == _next_sha(shas, sha)[:min_prefix]:
            min_prefix += 1
    return min_prefix


def _get_machine_id():
    with open(_MACHINE_ID, "r") as f:
        try:
            machine_id = f.read().strip()
        except Exception as e:
            _log_error("Could not read machine-id from '%s': %s" %
                       (_MACHINE_ID, e))
            machine_id = None
    return machine_id


__all__ = [
    # boom module constants
    'DEFAULT_BOOT_PATH', 'DEFAULT_BOOM_PATH',

    # Profile format keys
    'FMT_VERSION',
    'FMT_LVM_ROOT_LV',
    'FMT_BTRFS_SUBVOLUME',
    'FMT_BTRFS_SUBVOL_ID',
    'FMT_BTRFS_SUBVOL_PATH',
    'FMT_ROOT_DEVICE',
    'FMT_ROOT_OPTS',
    'FORMAT_KEYS',

    # API Classes
    'Selection',

    # Path configuration
    'get_boot_path',
    'get_boom_path',
    'set_boot_path',
    'set_boom_path',

    # Debug logging
    'get_debug_mask',
    'set_debug_mask',
    'BOOM_DEBUG_PROFILE',
    'BOOM_DEBUG_ENTRY',
    'BOOM_DEBUG_REPORT',
    'BOOM_DEBUG_COMMAND',
    'BOOM_DEBUG_ALL',

    # Utility routines
    '_blank_or_comment',
    '_parse_name_value',
    '_key_regex_from_format',
    '_find_minimum_sha_prefix',
    '_get_machine_id'
]

# vim: set et ts=4 sw=4 :
