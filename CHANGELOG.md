# Changelog

## [2.0.0](https://github.com/Garulf/flow-cider/compare/v1.0.1...v2.0.0) (2026-11-17)


### ⚠ BREAKING CHANGES

* the plugin now runs on Flow Launcher's python_v2 runtime and needs Flow Launcher 1.17.0 or newer.

### Features

* port the plugin to pyflowlauncher on the python_v2 runtime ([69458cf](https://github.com/Garulf/flow-cider/commit/69458cffc677ae2e6d09d14da5ccd71cda2110d9))


### Bug Fixes

* list results when a search finds only songs or only albums ([23e960e](https://github.com/Garulf/flow-cider/commit/23e960e69acab5c2b33c61386ee8b29e97da6b57))
* make the :type filter match songs and albums ([a5b59f8](https://github.com/Garulf/flow-cider/commit/a5b59f84961f3b06d935b0a362f1d354662a7803))
* offer Dislike for songs that are not loved ([a2c67e6](https://github.com/Garulf/flow-cider/commit/a2c67e6e87ed8207b9f53fcd8bfe2f614127aaa7))
* show an error for unknown search options instead of exiting ([2a3d26f](https://github.com/Garulf/flow-cider/commit/2a3d26f80157512a89e1ca866d891fc9b10d1e96))
* stop waiting when Cider does not answer ([43703e9](https://github.com/Garulf/flow-cider/commit/43703e9eb74e3d9f230d88b634b2e7a539a531ca))
