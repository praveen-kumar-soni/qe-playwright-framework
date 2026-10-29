from pathlib import Path
from typing import Union


def ensure_dir(path: Union[str, Path]) -> Path:
    """Create ``path`` (and any missing parents) if it doesn't already exist.

    Returns the resolved ``Path`` so call sites can chain into it, e.g.:
        trace_path = ensure_dir("test-output") / f"{name}_trace.zip"
    """
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
