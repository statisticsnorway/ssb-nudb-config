from nudb_config.config import settings

print(settings.paths)
print(settings["paths"])

print(settings.paths.local_daplalab)
print(settings.paths["local_daplalab"])

print(settings.paths.local_daplalab.katalog)
print(settings.paths.local_daplalab["katalog"])
