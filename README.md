# Darling Swift

Attention: This repository uses Git LFS!

Files found here come from official Swift releases from Swift.org. They are downloaded and extracted using the `build.sh` script before committing.

The runtime libraries (libswiftCore, libswift_Concurrency, ...) come from the release in `version.txt`.
The SDK overlays (libswiftFoundation, libswiftAppKit, ...) left the toolchain after Swift 5.2, so they
are still the ones from Swift 5.2.2. The few libswiftCore symbols they need that newer runtimes no longer
export live in `libswiftCoreLegacy.dylib` (built from `legacy.c`), which `build.sh` makes libswiftCore
re-export with `add-reexport.py`.
