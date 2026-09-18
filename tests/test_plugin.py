# Copyright (c) 2025-2026 Intel Corporation

import pytest

# Importing the whole module to be able to access modifications
# to internal module variables (such as _g_zelib).
import intel_variant_provider.ze as ze
from intel_variant_provider.devices import _GtGmdIDs
from intel_variant_provider.plugin import IntelVariantPlugin, VariantFeatureConfig
from intel_variant_provider.ze import *


@pytest.fixture
def plugin() -> IntelVariantPlugin:
    return IntelVariantPlugin()

@pytest.fixture(autouse=True)
def clear_cache():
    IntelVariantPlugin.generate_all_gt_gmdids.cache_clear()


def test_get_all_configs(plugin):
    configs = plugin.get_all_configs()
    assert len(configs) == 1
    assert configs[0].name == "gt_gmdid"
    assert configs[0].values == list(_GtGmdIDs.keys())


class TestGetSupportedConfigs:
    zelib_orig = None
    zelib_cache_orig = ( dict() )
    cdll_name = "intel_variant_provider.ze.CDLL"

    def setup_method(self, method):
        self.zelib_orig = ze.g_zelib
        self.zelib_cache_orig = ze.g_zelib_cache
        ze.g_zelib = None
        ze.g_zelib_cache = ( dict() )

    def teardown_method(self, method):
        ze.g_zelib = self.zelib_orig
        ze.g_zelib_cache = self.zelib_cache_orig

    def test_no_L0_library(self, plugin, mocker):
        mocker.patch(self.cdll_name, side_effect=OSError("No such file"))
        with pytest.warns(UserWarning):
            assert not plugin.get_supported_configs()

    def test_force_existing_gt_gmdid(self, plugin, monkeypatch):
        monkeypatch.setenv("INTEL_VARIANT_PROVIDER_FORCE_GT_GMDID", "12.60.7")
        assert plugin.get_supported_configs() == [
            VariantFeatureConfig(name="gt_gmdid", values=["12.60.7"], multi_value=True)
        ]

    def test_force_invalid_gt_gmdid(self, plugin, monkeypatch):
        monkeypatch.setenv("INTEL_VARIANT_PROVIDER_FORCE_GT_GMDID", "12.99.99")
        with pytest.warns(UserWarning):
            assert not plugin.get_supported_configs()

