import os

from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useTitle: str = "Bench"
    useDocs: bool = False
    useVite: bool = False
    # The runner sets the worker count, so every stack gets the same cores.
    useWorkers: int = int(os.environ.get("BENCH_WORKERS", "1"))
