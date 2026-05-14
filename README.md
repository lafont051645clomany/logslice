# logslice

A fast log file parser that extracts and filters time-range segments from large rotated log archives.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/youruser/logslice.git
cd logslice && pip install .
```

---

## Usage

### Command Line

```bash
# Extract log entries between two timestamps
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:30:00" /var/log/app/*.log.gz

# Output to a file
logslice --start "2024-01-15 08:00:00" --end "2024-01-15 09:30:00" /var/log/app/ -o output.log
```

### Python API

```python
from logslice import LogSlicer

slicer = LogSlicer(
    start="2024-01-15 08:00:00",
    end="2024-01-15 09:30:00"
)

for entry in slicer.parse("/var/log/app/"):
    print(entry)
```

---

## Features

- Handles rotated and compressed log archives (`.gz`, `.bz2`)
- Supports custom timestamp formats via `--format` flag
- Streams results without loading entire files into memory
- Works across multiple log files in chronological order

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

This project is licensed under the [MIT License](LICENSE).