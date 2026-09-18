# Copyright (c) 2025 Intel Corporation

from __future__ import annotations

import os
import platform
import warnings
from dataclasses import dataclass
from functools import cache

from intel_variant_provider.devices import *
from intel_variant_provider.ze import *

VariantNamespace = str
VariantFeatureName = str
VariantFeatureValue = str


@dataclass(frozen=True)
class VariantFeatureConfig:
    name: str

    # Acceptable values in priority order
    values: list[str]
    multi_value: bool = False


def getAllUniqueGmdids():
    pci_vendor_id_intel = 0x8086
    gmdids = []
    try:
        desc = c_ze_init_driver_type_desc_t()
        desc.flags = ZE_INIT_DRIVER_TYPE_FLAG_GPU
        drivers = zeInitDrivers(desc)

        for driver in drivers:
            devices = zeDeviceGet(driver)
            for device in devices:
                devip_version = c_ze_device_ip_version_ext_t()
                props = zeDeviceGetProperties(device, [devip_version])
                if props.vendorId == pci_vendor_id_intel:
                    gmdid = GMDID(devip_version.ipVersion)
                    for compat_gmdid in gmdid.get_all_compatible_gmdids():
                        # We must return list of unique GMDIDs as a requirement
                        # of variantlib.
                        if compat_gmdid not in gmdids:
                            gmdids.append(compat_gmdid)
    except Exception as e:
        warnings.warn(f"Intel driver stack not installed or malfunctions: {e}", UserWarning, stacklevel=1)
    return gmdids


class IntelVariantPlugin:
    namespace = "intel"
    dynamic = False

    @classmethod
    @cache
    def generate_all_gmdids(cls) -> list[str] | None:
        if platform.system() not in ["Linux", "Windows"]:
            warnings.warn(f"Unsupported OS: {platform.system()}", UserWarning, stacklevel=1)
            return []

        forced_gmdid = os.getenv("INTEL_VARIANT_PROVIDER_FORCE_GMDID")
        if forced_gmdid:
            unique_gmdids = [forced_gmdid]
        else:
            unique_gmdids = getAllUniqueGmdids()

        gmdids = []
        known_gmdids = get_all_known_gmdids()
        for gmdid in unique_gmdids:
            # Filter out devices which GMDIDs are not explicitly
            # known to plugin. This gives consistency with the
            # check in validate_property().
            if gmdid not in known_gmdids:
                warnings.warn(f"Intel device with {gmdid} GMDID is filtered out as not known to plugin)")
            else:
                gmdids.append(gmdid)

        if not gmdids:
            warnings.warn("No Intel GPU detected", UserWarning, stacklevel=1)
        return gmdids

    @classmethod
    def get_supported_configs(cls) -> list[VariantFeatureConfig]:
        keyconfigs: list[VariantFeatureConfig] = []

        if gmdids := cls.generate_all_gmdids():
            keyconfigs.append(
                VariantFeatureConfig(
                    name="gmdid",
                    values=gmdids,
                    multi_value=True,
                    )
                )

        return keyconfigs

    @classmethod
    def get_all_configs(cls) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="gmdid",
                values=get_all_known_gmdids(),
                multi_value=True,
            ),
        ]

if __name__ == "__main__":
    plugin = IntelVariantPlugin()
    print(plugin.get_supported_configs())
