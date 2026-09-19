# STRx BLE Broadcast Protocol

How the Simarine STRx radar tank level meter announces itself over Bluetooth Low Energy and
broadcasts the tank level, so a host can read it without connecting.

- [STRx-ble-advertising.md](STRx-ble-advertising.md), the specification: discovery, packet
  layouts, broadcast modes, AES-CCM protection, display name.
- [examples/python](examples/python), a scanner that parses and decrypts the broadcast, and
  offline tests of the parser.

## Layout

```text
STRx-ble-advertising.md   specification, version in the title
docs/img/                 app screenshots used by the specification
scripts/export-html.py    renders the specification to one self-contained HTML file
examples/python/          reference parser and scanner
```

## Versioning

The version in the specification title is the protocol version of the firmware it describes.
The major number changes on incompatible layout changes, the minor on backward-compatible additions.
Tags of this repository follow the same version.

## Export

```bash
python scripts/export-html.py
```

Writes `STRx-ble-advertising.html` with the screenshots embedded. The output is not committed.

## Contributing

Issues and pull requests are welcome for the examples and for errors in the specification.
Protocol changes are made by Simarine together with the firmware.
