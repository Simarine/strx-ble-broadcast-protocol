# Python example

Reads the STRx broadcast with [bleak](https://github.com/hbldh/bleak), decrypts the level with
[cryptography](https://cryptography.io).

```bash
pip install -r requirements.txt

python scan.py                                   # list STRx devices in range
python scan.py -a AA:BB:CC:DD:EE:FF              # follow one device
python scan.py -a AA:BB:CC:DD:EE:FF -k <32 hex>  # with the key from the app
```

| File                     | Content                                                          |
|--------------------------|------------------------------------------------------------------|
| `strx_broadcast.py`      | Parser, AES-CCM verification, counter guard, display name. No BLE |
| `scan.py`                | Scanner that prints devices and their level                      |
| `test_strx_broadcast.py` | Offline checks, `python -m unittest test_strx_broadcast`         |

`strx_broadcast.py` takes the two service data payloads as bytes, so it can be reused with any BLE
stack. It implements the v1.9 layout only.
