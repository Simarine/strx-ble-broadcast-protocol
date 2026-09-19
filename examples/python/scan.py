#!/usr/bin/env python3
"""
Scan for STRx devices and print their broadcast tank level.

    python scan.py                        list devices seen in 5 seconds
    python scan.py -a AA:BB:CC:DD:EE:FF   follow one device
    python scan.py -a ... -k <32 hex>     with the key from the app, to read
                                          the level in the Security modes

Requires bleak and cryptography.
"""

import argparse
import asyncio
from typing import Optional

from bleak import BleakScanner

import strx_broadcast as strx

SCAN_TIME_S = 5.0


class Device:
    """What is known about one STRx device across scan callbacks."""

    def __init__(self, address: str) -> None:
        self.address = address
        self.scan_response: Optional[strx.ScanResponse] = None
        self.advertisement: Optional[strx.Advertisement] = None
        self.guard = strx.CounterGuard()

    def update(self, service_data: dict) -> None:
        """Take in the payloads of one callback, either packet may be missing."""
        payload = service_data.get(strx.SCAN_RESPONSE_UUID)
        if payload is not None:
            self.scan_response = strx.parse_scan_response(payload)
        payload = service_data.get(strx.ADVERTISING_UUID)
        if payload is not None:
            self.advertisement = strx.parse_advertisement(payload)

    @property
    def name(self) -> str:
        """Display name, or the address before a scan response arrived."""
        return self.scan_response.display_name if self.scan_response else self.address

    def describe(self, key: Optional[bytes]) -> str:
        """One line with the mode, tank description and level."""
        rsp, adv = self.scan_response, self.advertisement
        if rsp is None:
            return f"{self.name}: waiting for scan response"

        parts = [f"{self.name} v{rsp.protocol_major}.{rsp.protocol_minor}",
                 strx.BEACON_MODE_NAMES.get(rsp.beacon_mode, f"mode 0x{rsp.beacon_mode:02x}")]
        if rsp.tank_type_name is not None:
            parts.append(rsp.tank_type_name)
        if rsp.tank_volume_total is not None:
            parts.append(f"{rsp.tank_volume_total} l total")

        if adv is None:
            parts.append("no advertising packet")
            return ", ".join(parts)

        level, reason = strx.read_level(rsp, adv, key)
        if level is None:
            parts.append(reason)
        else:
            text = f"level {level / 10:.1f} %"
            if rsp.tank_volume_total is not None:
                text += f" = {level / 1000 * rsp.tank_volume_total:.1f} l"
            parts.append(text)
        return ", ".join(parts)


async def list_devices(key: Optional[bytes]) -> None:
    """Scan for SCAN_TIME_S and print every STRx device once."""
    devices: dict[str, Device] = {}

    def on_detection(ble_device, advertisement_data) -> None:
        service_data = advertisement_data.service_data
        if strx.ADVERTISING_UUID not in service_data and strx.SCAN_RESPONSE_UUID not in service_data:
            return
        device = devices.setdefault(ble_device.address, Device(ble_device.address))
        device.update(service_data)

    print(f"Scanning {SCAN_TIME_S:.0f} s for STRx devices...")
    async with BleakScanner(detection_callback=on_detection):
        await asyncio.sleep(SCAN_TIME_S)

    if not devices:
        print("No STRx device found")
    for device in devices.values():
        print(f"{device.address}  {device.describe(key)}")


async def follow_device(address: str, key: Optional[bytes]) -> None:
    """Print every new message of one device until interrupted."""
    device = Device(address.upper())

    def on_detection(ble_device, advertisement_data) -> None:
        if ble_device.address.upper() != device.address:
            return
        device.update(advertisement_data.service_data)
        rsp, adv = device.scan_response, device.advertisement
        if rsp is None or adv is None:
            return
        verdict = device.guard.check(rsp.boot_counter, adv.message_counter)
        if verdict == strx.CounterGuard.REPEAT:
            return
        flag = "  REPLAY, rejected" if verdict == strx.CounterGuard.REPLAY else ""
        print(f"#{adv.message_counter:<8} {device.describe(key)}{flag}")

    print(f"Following {device.address}, Ctrl-C to stop")
    async with BleakScanner(detection_callback=on_detection):
        while True:
            await asyncio.sleep(1)


def main() -> None:
    """Parse the command line and run the scanner."""
    parser = argparse.ArgumentParser(description="Read the STRx BLE broadcast")
    parser.add_argument("-a", "--address", help="follow this device address")
    parser.add_argument("-k", "--key", help="encryption key from the app, 32 hex digits")
    args = parser.parse_args()

    key = strx.key_from_hex(args.key) if args.key else None
    try:
        if args.address:
            asyncio.run(follow_device(args.address, key))
        else:
            asyncio.run(list_devices(key))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
