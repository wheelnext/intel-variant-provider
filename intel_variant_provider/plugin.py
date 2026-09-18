# Copyright (c) 2025-2026 Intel Corporation

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


def getAllUniqueGtGmdids():
    pci_vendor_id_intel = 0x8086
    gt_gmdids = []
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
                    gt_gmdid = GtGMDID(devip_version.ipVersion)
                    for compat_gt_gmdid in gt_gmdid.get_all_compatible_gt_gmdids():
                        # We must return list of unique GT GMDIDs as a requirement
                        # of variantlib.
                        if compat_gt_gmdid not in gt_gmdids:
                            gt_gmdids.append(compat_gt_gmdid)
    except Exception as e:
        warnings.warn(f"Intel driver stack not installed or malfunctions: {e}", UserWarning, stacklevel=1)
    return gt_gmdids


class IntelVariantPlugin:
    namespace = "intel"
    dynamic = False

    @classmethod
    @cache
    def generate_all_gt_gmdids(cls) -> list[str] | None:
        if platform.system() not in ["Linux", "Windows"]:
            warnings.warn(f"Unsupported OS: {platform.system()}", UserWarning, stacklevel=1)
            return []

        forced_gt_gmdid = os.getenv("INTEL_VARIANT_PROVIDER_FORCE_GT_GMDID")
        if forced_gt_gmdid:
            unique_gt_gmdids = [forced_gt_gmdid]
        else:
            unique_gt_gmdids = getAllUniqueGtGmdids()

        gt_gmdids = []
        known_gt_gmdids = get_all_known_gt_gmdids()
        for gt_gmdid in unique_gt_gmdids:
            # Filter out devices which GT GMDIDs are not explicitly
            # known to plugin. This gives consistency with the
            # check in validate_property().
            if gt_gmdid not in known_gt_gmdids:
                warnings.warn(f"Intel device with {gt_gmdid} GT GMDID is filtered out as not known to plugin)")
            else:
                gt_gmdids.append(gt_gmdid)

        if not gt_gmdids:
            warnings.warn("No Intel GPU detected", UserWarning, stacklevel=1)
        return gt_gmdids

    @classmethod
    def get_supported_configs(cls) -> list[VariantFeatureConfig]:
        keyconfigs: list[VariantFeatureConfig] = []

        if gt_gmdids := cls.generate_all_gt_gmdids():
            keyconfigs.append(
                VariantFeatureConfig(
                    name="gt_gmdid",
                    values=gt_gmdids,
                    multi_value=True,
                    )
                )

        return keyconfigs

    @classmethod
    def get_all_configs(cls) -> list[VariantFeatureConfig]:
        return [
            VariantFeatureConfig(
                name="gt_gmdid",
                values=get_all_known_gt_gmdids(),
                multi_value=True,
            ),
        ]

if __name__ == "__main__":
    plugin = IntelVariantPlugin()
    print(plugin.get_supported_configs())
