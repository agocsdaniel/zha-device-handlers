"""Tests for Tuya Sensor quirks."""

import pytest
from zigpy.zcl import foundation
from zigpy.zcl.clusters.general import Basic

import zhaquirks
import zhaquirks.tuya
from zhaquirks.tuya.mcu import TuyaMCUCluster

zhaquirks.setup()


@pytest.mark.parametrize(
    "model,manuf,rh_scale,temp_scale",
    [
        ("_TZE200_bjawzodf", "TS0601", 10, 10),
        ("_TZE200_zl1kmjqx", "TS0601", 10, 10),
        ("_TZE200_a8sdabtg", "TS0601", 100, 10),  # Variant without screen, round
        ("_TZE200_qoy0ekbd", "TS0601", 100, 10),
        ("_TZE200_znbl8dj5", "TS0601", 100, 10),
        ("_TZE200_qyflbnbj", "TS0601", 100, 10),
        ("_TZE200_zppcgbdj", "TS0601", 100, 10),
    ],
)
async def test_handle_get_data(
    zigpy_device_from_v2_quirk, model, manuf, rh_scale, temp_scale
):
    """Test handle_get_data for multiple attributes - normal battery."""

    quirked = zigpy_device_from_v2_quirk(model, manuf)
    ep = quirked.endpoints[1]

    assert ep.basic is not None
    assert isinstance(ep.basic, Basic)

    assert ep.tuya_manufacturer is not None
    assert isinstance(ep.tuya_manufacturer, TuyaMCUCluster)

    message = b"\x09\xe0\x02\x0b\x33\x01\x02\x00\x04\x00\x00\x00\xfd\x02\x02\x00\x04\x00\x00\x00\x47\x04\x02\x00\x04\x00\x00\x00\x64"
    hdr, data = ep.tuya_manufacturer.deserialize(message)

    status = ep.tuya_manufacturer.handle_get_data(data.data)
    assert status == foundation.Status.SUCCESS

    assert (
        ep.temperature.get("measured_value")
        == data.data.datapoints[0].data.payload * temp_scale
    )

    assert (
        ep.humidity.get("measured_value")
        == data.data.datapoints[1].data.payload * rh_scale
    )

    assert (
        ep.power.get("battery_percentage_remaining")
        == data.data.datapoints[2].data.payload * 2
    )

    message = b"\x09\xe0\x02\x0b\x33\x01\x02\x00\x04\x00\x00\x00\xfd\x02\x02\x00\x04\x00\x00\x00\x47\xff\x02\x00\x04\x00\x00\x00\x64"
    hdr, data = ep.tuya_manufacturer.deserialize(message)

    status = ep.tuya_manufacturer.handle_get_data(data.data)
    assert status == foundation.Status.UNSUPPORTED_ATTRIBUTE


@pytest.mark.parametrize(
    "model,manuf,rh_scale,temp_scale",
    [
        ("_TZE200_yjjdcqsq", "TS0601", 100, 10),
        ("_TZE200_9yapgbuv", "TS0601", 100, 10),
        ("_TZE204_yjjdcqsq", "TS0601", 100, 10),
        ("_TZE200_utkemkbs", "TS0601", 100, 10),
        ("_TZE204_utkemkbs", "TS0601", 100, 10),
        ("_TZE204_yjjdcqsq", "TS0601", 100, 10),
        ("_TZE204_ksz749x8", "TS0601", 100, 10),
    ],
)
async def test_handle_get_data_enum_batt(
    zigpy_device_from_v2_quirk, model, manuf, rh_scale, temp_scale
):
    """Test handle_get_data for multiple attributes - enum battery."""

    quirked = zigpy_device_from_v2_quirk(model, manuf)
    ep = quirked.endpoints[1]

    assert ep.basic is not None
    assert isinstance(ep.basic, Basic)

    assert ep.tuya_manufacturer is not None
    assert isinstance(ep.tuya_manufacturer, TuyaMCUCluster)

    message = b"\x09\xe0\x02\x0b\x33\x01\x02\x00\x04\x00\x00\x00\xfd\x02\x02\x00\x04\x00\x00\x00\x47\x04\x02\x00\x04\x00\x00\x00\x01"
    hdr, data = ep.tuya_manufacturer.deserialize(message)

    status = ep.tuya_manufacturer.handle_get_data(data.data)

    assert status == foundation.Status.SUCCESS

    assert (
        ep.temperature.get("measured_value")
        == data.data.datapoints[0].data.payload * temp_scale
    )

    assert (
        ep.humidity.get("measured_value")
        == data.data.datapoints[1].data.payload * rh_scale
    )

    assert ep.power.get("battery_percentage_remaining") == 100

    message = b"\x09\xe0\x02\x0b\x33\x01\x02\x00\x04\x00\x00\x00\xfd\x02\x02\x00\x04\x00\x00\x00\x47\xff\x02\x00\x04\x00\x00\x00\x64"
    hdr, data = ep.tuya_manufacturer.deserialize(message)

    status = ep.tuya_manufacturer.handle_get_data(data.data)
    assert status == foundation.Status.UNSUPPORTED_ATTRIBUTE