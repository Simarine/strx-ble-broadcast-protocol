# STRx BLE Broadcast Protocol

How the Simarine STRx radar tank level meter announces itself over Bluetooth Low Energy and
broadcasts the tank level, so a host can read it without connecting.

- [STRx-ble-advertising.md](STRx-ble-advertising.md), the specification: discovery, packet
  layouts, broadcast modes, AES-CCM protection, display name.
- [examples/python](examples/python), a scanner that parses and decrypts the broadcast, and
  offline tests of the parser.

## Layout

```text
LICENSE                   MIT license
STRx-ble-advertising.md   specification, version in the title
docs/img/                 app screenshots used by the specification
scripts/export-html.py    renders the specification to one self-contained HTML file
.github/workflows/        release on a pushed version tag, with the HTML export attached
examples/python/          reference parser and scanner
```

## Versioning

The version in the specification title is the version of this document. It is independent of the
firmware protocol version the device advertises in `PROTOCOL_VERSION_MAJOR/MINOR`, which also moves
when only the connected protocol changes. The major number changes on incompatible layout changes,
the minor on backward-compatible additions, the patch on editorial changes.

Every content change bumps the version. Tagging the commit `vX.Y.Z`, equal to the title, publishes a
GitHub release with the rendered HTML attached; the workflow refuses a tag that differs from the title.

## Export

```bash
python scripts/export-html.py
```

Writes `STRx-ble-advertising.html` with the screenshots embedded. The output is not committed.

## Contributing

Issues and pull requests are welcome for the examples and for errors in the specification.
Protocol changes are made by Simarine together with the firmware.

## License

MIT, see [LICENSE](LICENSE). The specification, the examples and the scripts are all covered.
