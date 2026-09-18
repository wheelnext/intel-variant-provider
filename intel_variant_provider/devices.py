# Copyright (c) 2025 Intel Corporation

from __future__ import annotations

import ctypes

# Intel GMDID identifiers are device hardware identifiers used by Intel GPUs to
# track and identify the specific architecture versions. GMDIDs provide a way to
# differentiate compute capabilities of Intel GPUs.
#
# Programmatically GMDIDs can be queried using Intel device driver APIs. With
# Level Zero C++ API this can be done with `ZE_extension_device_ip_version`:
#
# * https://oneapi-src.github.io/level-zero-spec/level-zero/latest/core/EXT_DeviceIpVersion.html#ze-extension-device-ip-version
#
# The "Device IP Version" is an unfortunate misleading name (do not confuse with,
# for example, network IP addresses) used by Level Zero library and Intel drivers
# to abstract the concept of the version by which GPU architectures can be
# identified. In general "Device IP Version" is implementation-defined. For Intel
# GPUs it resolves to GMDID values.
#
# On a command line tools level GMDIDs of Intel GPUs can be queried from the
# platfom acronym names with the `ocloc` tool. For example:
#
#   $ ocloc ids bmg
#   Matched ids:
#   20.1.0
#
# GMDIDs can further be directly passed to the `ocloc` AOT compiler:
#
#   $ ocloc compiler -device 20.1.0 ...


# Dictionary keys are GMDIDs of the Intel devices known to this plugin.
#
# Dictionary values provide the following information for each GMDID:
# * `devices` - list of device acronym names corresponding to the given GMDID.
#   These acronyms can be used in `ocloc` compiler interchangable with GMDIDs to
#   identify devices to compiler for.
# * `base_gmdid` - GMDID of the base platform. Device code built for the base
#   platform can be executed on all the platforms inherited from the base platform.
# * `base_name` - acronym name assigned to GMDID of the base platform. This name
#   can be used in `ocloc` compiler to build code for the base platform.
_GmdIDs = {
    "35.11.0": {
        "devices": ["cri"],
    },
    "35.10.4": {
        "devices": ["nvl-p"],
    },
    "30.5.4": {
        "devices": ["nvl-u", "nvl-h"],
        "base_gmdid": "30.0.4",
    },
    "30.4.4": {
        "devices": ["nvl-s", "nvl-hx", "nvl-ul"],
        "base_gmdid": "30.0.4",
    },
    "30.3.1": {
        "devices": ["wcl"],
        "base_gmdid": "30.0.4",
    },
    "30.1.0": {
        "devices": ["ptl-u"],
        "base_gmdid": "30.0.4",
    },
    "30.0.4": {
        "devices": ["ptl-h"],
        "base_name": "ptl",
    },
    "20.4.4": {
        "devices": ["lnl-m"],
        "base_gmdid": "20.1.0",
    },
    "20.2.0": {
        "devices": ["bmg-g31"],
        "base_gmdid": "20.1.0"
    },
    "20.1.0": {
        "devices": ["bmg-g21"],
        "base_name": "bmg",
    },
    "12.74.4": {
        "devices": ["arl-h"]
    },
    "12.71.4": {
        "devices": ["mtl-h"],
        "base_gmdid": "12.70.4",
    },
    "12.70.4": {
        "devices": ["mtl-u", "arl-u", "arl-s"],
        "base_name": "mtl",
    },
    "12.60.7": {
        "devices": ["pvc"],
    },
    "12.57.0": {
        "devices": ["acm-g12", "dg2-g12"],
        "base_gmdid": "12.55.8",
    },
    "12.56.5": {
        "devices": ["acm-g11", "dg2-g11", "ats-m75"],
        "base_gmdid": "12.55.8",
    },
    "12.55.8": {
        "devices": ["acm-g10", "dg2-g10", "ats-m150"],
        "base_name": "dg2",
    },
    "12.10.0": {
        "devices": ["dg1"],
    },
    "12.4.0": {
        "devices": ["adl-n"],
    },
    "12.3.0": {
        "devices": ["adl-p", "rpl-p"],
    },
    "12.2.0": {
        "devices": ["adl-s", "rpl-s"],
    },
    "12.1.0": {
        "devices": ["rkl"],
    },
    "12.0.0": {
        "devices": ["tgllp", "tgl"],
    },
}


def get_all_known_gmdids() -> list[str]:
    return list(_GmdIDs.keys())


# The better way would be to inherit from ctypes.Union and use bit fields.
# Unfortunately python ctypes has a bug handling bit fields...
class GMDID:
    """Class represents Intel GMDID values

    Args:
        devip_version (ctypes.c_uint32): Device IP Version to initialize GMDID from
    """

    revision = 0
    release = 0
    architecture = 0

    def __init__(self, devip_version: ctypes.c_uint32) -> None:
        # For the definition of Device IP Version, see:
        #   * https://github.com/intel/compute-runtime/blob/25.27.34303.6/shared/source/helpers/hw_ip_version.h
        #
        # struct
        # {
        #    uint32_t revision : 6;
        #    uint32_t reserved : 8;
        #    uint32_t release : 8;
        #    uint32_t architecture : 10;
        # };
        self.revision = devip_version & 0x3F  # 6 bits value
        self.release = (devip_version >> 14) & 0xFF
        self.architecture = devip_version >> 22

    def __str__(self) -> str:
        return f"{self.architecture}.{self.release}.{self.revision}"

    def get_base_gmdid(self) -> str:
        """Returns GMDID of the base platform if available, empty string
        otherwise.
        """
        gmdid = str(self)
        if gmdid in _GmdIDs:
            if "base_gmdid" in _GmdIDs[gmdid]:
                return _GmdIDs[gmdid]["base_gmdid"]
        return ""

    def get_all_compatible_gmdids(self) -> list[str]:
        """Returns list of all compatible GMDIDs.

        Device code built for the compatible GMDID can be executed on
        the device represented by this GMDID.
        """
        gmdids = [ str(self) ]
        base_gmdid = self.get_base_gmdid()
        if base_gmdid:
            gmdids += [base_gmdid]
        return gmdids
