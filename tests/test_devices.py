# Copyright (c) 2025 Intel Corporation

import re

import pytest

from intel_variant_provider.devices import *
from intel_variant_provider.devices import _GmdIDs

pattern = re.compile("^[a-z0-9_.]+$")

def test_pattern():
    """Sanity test for the pattern"""
    assert pattern.fullmatch("abc")
    assert pattern.fullmatch("abc_1")
    assert pattern.fullmatch("abc.1")
    assert not pattern.fullmatch("abc-1")
    assert not pattern.fullmatch("ABC")

def to_devip_version(gmdid: str):
    """Converts human readable GMDID into Level Zero Device IP Version value"""
    parts = [int(x) for x in gmdid.split('.')]
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

def test_GmdIDs():
    """Test internal GMDIDs table"""
    for key, value in _GmdIDs.items():
        assert pattern.fullmatch(key)
        _ = to_devip_version(key)
        assert value
        assert "devices" in value
        for d in value["devices"]:
            assert isinstance(d, str)
            assert d != ""
        if "base_gmdid" in value:
            assert isinstance(value["base_gmdid"], str)
            base_gmdid = value["base_gmdid"]
            assert base_gmdid in _GmdIDs
            assert "base_name" not in value
        elif "base_name" in value:
            assert isinstance(value["base_name"], str)
            assert value["base_name"] != ""
            assert pattern.fullmatch(value["base_name"])

def test_GMDID_not_in_table():
    """Test GMDID handling of the GMDID not in the internal table"""
    gmdid = GMDID(0x12341234)
    str_gmdid = str(gmdid)
    # sanity check that we did not hit table entry
    assert str_gmdid not in _GmdIDs
    # any GMDID should match the pattern
    assert pattern.fullmatch(str_gmdid)
    assert str_gmdid == "72.208.52"
    # should not have base GMDID as it's not in table
    assert not gmdid.get_base_gmdid()
    # all compatible GMDIDs should just have single entry of GMDID itself
    all_gmdids = gmdid.get_all_compatible_gmdids()
    assert len(all_gmdids) == 1
    assert all_gmdids[0] == str_gmdid

def test_GMDID_in_table():
    for key, value in _GmdIDs.items():
        gmdid = GMDID(to_devip_version(key))
        str_gmdid = str(gmdid)
        base_gmdid = gmdid.get_base_gmdid()
        all_gmdids = gmdid.get_all_compatible_gmdids()
        assert str_gmdid == key
        if "base_gmdid" in value:
            assert len(all_gmdids) == 2
            assert all_gmdids[0] == str_gmdid
            assert all_gmdids[1] == value["base_gmdid"]
            assert base_gmdid == value["base_gmdid"]
        else:
            assert len(all_gmdids) == 1
            assert all_gmdids[0] == str_gmdid
            assert base_gmdid == ""
