# Copyright (c) 2025-2026 Intel Corporation

import re

import pytest

from intel_variant_provider.devices import *
from intel_variant_provider.devices import _GtGmdIDs

pattern = re.compile("^[a-z0-9_.]+$")

def test_pattern():
    """Sanity test for the pattern"""
    assert pattern.fullmatch("abc")
    assert pattern.fullmatch("abc_1")
    assert pattern.fullmatch("abc.1")
    assert not pattern.fullmatch("abc-1")
    assert not pattern.fullmatch("ABC")

def to_devip_version(gt_gmdid: str):
    """Converts human readable GT GMDID into Level Zero Device IP Version value"""
    parts = [int(x) for x in gt_gmdid.split('.')]
    assert len(parts) == 3
    (arch, release, revision) = parts
    assert (revision & ~0x3F) == 0
    assert (release & ~0xFF) == 0
    assert (arch & ~0xFF) == 0
    return (revision & 0x3F) | (release << 14) | (arch << 22)

def test_to_devip_version():
    assert to_devip_version("12.60.7") == 0x030f0007
    assert to_devip_version("12.55.8") == 0x030dc008
    bad_revision = 0x4F
    with pytest.raises(AssertionError):
        to_devip_version(f"0.0.{bad_revision}")
    with pytest.raises(AssertionError):
        to_devip_version("0.256.0")
    with pytest.raises(AssertionError):
        to_devip_version("256.0.0")
    with pytest.raises(AssertionError):
        to_devip_version("1.2.3.4")

def test_GtGmdIDs():
    """Test internal GT GMDIDs table"""
    for key, value in _GtGmdIDs.items():
        assert pattern.fullmatch(key)
        _ = to_devip_version(key)
        assert value
        assert "devices" in value
        for d in value["devices"]:
            assert isinstance(d, str)
            assert d != ""
        if "base_gt_gmdid" in value:
            assert isinstance(value["base_gt_gmdid"], str)
            base_gt_gmdid = value["base_gt_gmdid"]
            assert base_gt_gmdid in _GtGmdIDs
            assert "base_name" not in value
        elif "base_name" in value:
            assert isinstance(value["base_name"], str)
            assert value["base_name"] != ""
            assert pattern.fullmatch(value["base_name"])

def test_GtGMDID_not_in_table():
    """Test GT GMDID handling of the GT GMDID not in the internal table"""
    gt_gmdid = GtGMDID(0x12341234)
    str_gt_gmdid = str(gt_gmdid)
    # sanity check that we did not hit table entry
    assert str_gt_gmdid not in _GtGmdIDs
    # any GT GMDID should match the pattern
    assert pattern.fullmatch(str_gt_gmdid)
    assert str_gt_gmdid == "72.208.52"
    # should not have base GT GMDID as it's not in table
    assert not gt_gmdid.get_base_gt_gmdid()
    # all compatible GT GMDIDs should just have single entry of GT GMDID itself
    all_gt_gmdids = gt_gmdid.get_all_compatible_gt_gmdids()
    assert len(all_gt_gmdids) == 1
    assert all_gt_gmdids[0] == str_gt_gmdid

def test_GtGMDID_in_table():
    for key, value in _GtGmdIDs.items():
        gt_gmdid = GtGMDID(to_devip_version(key))
        str_gt_gmdid = str(gt_gmdid)
        base_gt_gmdid = gt_gmdid.get_base_gt_gmdid()
        all_gt_gmdids = gt_gmdid.get_all_compatible_gt_gmdids()
        assert str_gt_gmdid == key
        if "base_gt_gmdid" in value:
            assert len(all_gt_gmdids) == 2
            assert all_gt_gmdids[0] == str_gt_gmdid
            assert all_gt_gmdids[1] == value["base_gt_gmdid"]
            assert base_gt_gmdid == value["base_gt_gmdid"]
        else:
            assert len(all_gt_gmdids) == 1
            assert all_gt_gmdids[0] == str_gt_gmdid
            assert base_gt_gmdid == ""
