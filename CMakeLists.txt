file(GLOB DYLIBS "*.dylib")
install(FILES ${DYLIBS} DESTINATION libexec/darling/usr/lib/swift)

# libswiftCore re-exports this (see build.sh)
set(DYLIB_INSTALL_NAME "/usr/lib/swift/libswiftCoreLegacy.dylib")
add_darling_library(swiftCoreLegacy SHARED legacy.c)
make_fat(swiftCoreLegacy)
install(TARGETS swiftCoreLegacy DESTINATION libexec/darling/usr/lib/swift)
