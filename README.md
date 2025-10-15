# Nudb_Config

[![PyPI](https://img.shields.io/pypi/v/nudb_config.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/nudb_config.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/nudb_config)][pypi status]
[![License](https://img.shields.io/pypi/l/nudb_config)][license]

[![Documentation](https://github.com/statisticsnorway/nudb_config/actions/workflows/docs.yml/badge.svg)][documentation]
[![Tests](https://github.com/statisticsnorway/nudb_config/actions/workflows/tests.yml/badge.svg)][tests]
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_nudb_config&metric=coverage)][sonarcov]
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=statisticsnorway_nudb_config&metric=alert_status)][sonarquality]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)][poetry]

[pypi status]: https://pypi.org/project/nudb_config/
[documentation]: https://statisticsnorway.github.io/nudb_config
[tests]: https://github.com/statisticsnorway/nudb_config/actions?workflow=Tests
[sonarcov]: https://sonarcloud.io/summary/overall?id=statisticsnorway_nudb_config
[sonarquality]: https://sonarcloud.io/summary/overall?id=statisticsnorway_nudb_config
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[poetry]: https://python-poetry.org/


## Installation
You can install _Nudb_Config_ via [pip] from [PyPI]:

```console
poetry add ssb-nudb-config
```


## Usage
The most important object in the package are the "settings":
```python
from nudb_config import settings

print(nudb_config.paths)
```


Please see the [Reference Guide] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Nudb_Config_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [Statistics Norway]'s [SSB PyPI Template].

[statistics norway]: https://www.ssb.no/en
[pypi]: https://pypi.org/
[ssb pypi template]: https://github.com/statisticsnorway/ssb-pypitemplate
[file an issue]: https://github.com/statisticsnorway/nudb_config/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/statisticsnorway/nudb_config/blob/main/LICENSE
[contributor guide]: https://github.com/statisticsnorway/nudb_config/blob/main/CONTRIBUTING.md
[reference guide]: https://statisticsnorway.github.io/nudb_config/reference.html
