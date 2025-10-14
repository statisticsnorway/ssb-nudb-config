from nudb_config.config import settings

settings.paths.local_daplalab.delt_utdanning

import importlib.resources as impres
from pathlib import Path

Path(str(impres.files("nudb_config")))

type(impres.files("nudb_config"))
