"""
Top‑level package for AFM topological data analysis tools.

This package exposes the core analysis classes (`AutocorrelationAnalyzer`,
`PersistenceAnalyzer`, `MinMaxAnalyzer`, `BottleneckAnalyzer`) as well as
the orchestration `AnalysisPipeline` and an API module with high level
functions.  The design separates heavy computations from plotting and
saving to make the library usable in CLI and server environments alike.

Usage
-----
You can use the analyzers directly:

```
from afm_tda_tools.analyzers import AutocorrelationAnalyzer

analyzer = AutocorrelationAnalyzer()
results = analyzer.compute(file_path, width_line=0.1)
# results is a pandas.DataFrame that can be sent to a client and plotted there
```

Or use the convenience API functions:

```
from afm_tda_tools.api import run_acf

acf_results = run_acf(["/path/to/file.csv"], width_line=0.1)
```

The command line interface remains available via `python -m afm_tda_tools`.
"""

from .pipeline import AnalysisPipeline  # noqa: F401
from .api import run_acf, run_persistence, run_minmax, run_bottleneck  # noqa: F401
from .analyzers.autocorrelation import AutocorrelationAnalyzer  # noqa: F401
from .analyzers.persistence import PersistenceAnalyzer  # noqa: F401
from .analyzers.min_max import MinMaxAnalyzer  # noqa: F401
from .analyzers.bottleneck import BottleneckAnalyzer  # noqa: F401