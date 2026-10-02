# Copyright (c) 2025 Intel Corporation

import ctypes

# Intel GT GMDID identifiers are device hardware identifiers used by Intel GPUs to
# track and identify the specific architecture versions of its subcomponents such
# as Graphics (GT GMDID) and Media (Media GMDID). GT GMDIDs provide a way to
# differentiate compute capabilities of Intel GPUs.
#
# Programmatically GT GMDIDs can be queried using Intel device driver APIs. With
# Level Zero C++ API this can be done with `ZE_extension_device_ip_version`:
#
# * https://oneapi-src.github.io/level-zero-spec/level-zero/latest/core/EXT_DeviceIpVersion.html#ze-extension-device-ip-version
#
# The "Device IP Version" (IP here stands for Intellectual Property) is used by
# Intel driver APIs to abstract the concept of the version by which GPU
# architectures can be identified. "Device IP Version" is defined by specific
# driver implementation. For Intel GPUs it resolves to GT GMDID values.
#
# With command line tools GT GMDIDs of Intel GPUs can be queried from the
# platfom acronym names with the `ocloc`. For example:
#
#   $ ocloc ids bmg
#   Matched ids:
#   20.1.0
#
# GT GMDIDs can further be directly passed to the `ocloc` AOT compiler:
#
#   $ ocloc compiler -device 20.1.0 ...


# Dictionary keys are GT GMDIDs of the Intel devices known to this plugin.
#
# Dictionary values provide the following information for each GT GMDID:
# * `devices` - list of device acronym names corresponding to the given GT GMDID.
#   These acronyms can be used in `ocloc` compiler interchangable with GT GMDIDs to
#   identify devices to compiler for.
# * `compat` - GT GMDID of the base platform. Device code built for the base
#   platform can be executed on all the platforms inherited from the base platform.
# * `compat_name` - acronym name assigned to GT GMDID of the base platform. This name
#   can be used in `ocloc` compiler to build code for the base platform.
_intel_devips = {
    "35.11.0": {
        "devices": ["cri"],
    },
    "35.10.4": {
        "devices": ["nvl-p"],
    },
    "30.5.4": {
        "devices": ["nvl-u", "nvl-h"],
        "compat": "30.0.4",
    },
    "30.4.4": {
        "devices": ["nvl-s", "nvl-hx", "nvl-ul"],
        "compat": "30.0.4",
    },
    "30.3.1": {
        "devices": ["wcl"],
        "compat": "30.0.4",
    },
    "30.1.0": {
        "devices": ["ptl-u"],
        "compat": "30.0.4",
    },
    "30.0.4": {
        "devices": ["ptl-h"],
        "compat_name": "ptl",
    },
    "20.4.4": {
        "devices": ["lnl-m"],
        "compat": "20.1.0",
    },
    "20.2.0": {
        "devices": ["bmg-g31"],
        "compat": "20.1.0"
    },
    "20.1.0": {
        "devices": ["bmg-g21"],
        "compat_name": "bmg",
    },
    "12.74.4": {
        "devices": ["arl-h"]
    },
    "12.71.4": {
        "devices": ["mtl-h"],
        "compat": "12.70.4",
    },
    "12.70.4": {
        "devices": ["mtl-u", "arl-u", "arl-s"],
        "compat_name": "mtl",
    },
    "12.60.7": {
        "devices": ["pvc"],
    },
    "12.57.0": {
        "devices": ["acm-g12", "dg2-g12"],
        "compat": "12.55.8",
    },
    "12.56.5": {
        "devices": ["acm-g11", "dg2-g11", "ats-m75"],
        "compat": "12.55.8",
    },
    "12.55.8": {
        "devices": ["acm-g10", "dg2-g10", "ats-m150"],
        "compat_name": "dg2",
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

def get_all_known_ips() -> list[str]:
    return list(_intel_devips.keys())

# The better way would be to inherit from ctypes.Union and use bit fields.
# Unfortunately python ctypes has a bug handling bit fields...
class IntelDeviceIp:
    # See: https://github.com/intel/compute-runtime/blob/25.27.34303.6/shared/source/helpers/hw_ip_version.h
    ip_version = 0
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
        self.ip_version = devip_version
        self.revision = devip_version & 0x3F  # 6 bits value
        self.release = (devip_version >> 14) & 0xFF
        self.architecture = devip_version >> 22

    def __str__(self)-> str:
        return f"{self.architecture}.{self.release}.{self.revision}"

    # Returns GT GMDID of the base platform if available, empty string otherwise.
    def get_compat(self) -> str:
        ip = str(self)
        if ip in _intel_devips:
            if "compat" in _intel_devips[ip]:
                return _intel_devips[ip]["compat"]
        return ""

    # Returns list of all compatible GT GMDIDs. Device code built for the
    # compatible GT GMDID can be executed on the device represented by
    # this GT GMDID.
    def get_all_compat_ips(self) -> list[str]:
        ips = [ str(self) ]
        compat = self.get_compat()
        if compat:
            ips += [compat]
        return ips
