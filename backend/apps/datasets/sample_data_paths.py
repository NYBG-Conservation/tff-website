import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_sample_data_root() -> Path | None:
    candidates: list[Path] = []
    env_dir = os.environ.get("TFF_SAMPLE_DATA_DIR", "").strip()
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.extend((_REPO_ROOT / "src/lib/data/tff-sample-data", Path("/app/sample-data")))
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None
