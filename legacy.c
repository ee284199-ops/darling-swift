/*
 * Symbols that libswiftCore used to export and the Swift 5.2.2 overlays still import, but newer
 * libswiftCore builds no longer have. libswiftCore re-exports this library (see build.sh).
 */

#include <stdint.h>

// The bit that marks Swift classes in an Objective-C class's data pointer. Swift 5.2 runtimes
// built to back-deploy chose it at startup: 1 before macOS 10.14.4, 2 with the stable-ABI
// Objective-C runtime that Darling has.
uintptr_t _swift_classIsSwiftMask = 2;
