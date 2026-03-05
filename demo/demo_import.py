from nudb_config.config import settings

print(settings.paths)
print(settings["paths"])

print(settings.paths.daplalab_mounted)
print(settings.paths["daplalab_mounted"])

print(settings.paths.daplalab_mounted.katalog)
print(settings.paths.daplalab_mounted["katalog"])
