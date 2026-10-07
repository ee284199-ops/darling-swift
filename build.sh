#!/bin/sh
# Fetch the Swift runtime libraries from the official macOS toolchain package of version.txt.
#
# Since Swift 5.3 the toolchain no longer ships the SDK overlays (libswiftFoundation,
# libswiftAppKit, ...), so those stay at the last version that had them, 5.2.2. They import a
# few symbols that newer libswiftCore builds dropped; libswiftCoreLegacy (legacy.c) provides
# them and libswiftCore is patched to re-export it.
set -e

version=$(cat version.txt)
libs="libswiftCore libswiftDarwin libswiftDistributed libswiftObservation libswiftRegexBuilder
	libswiftRemoteMirror libswiftSwiftOnoneSupport libswift_Concurrency libswift_Differentiation
	libswift_RegexParser libswift_StringProcessing"
lipo=$(command -v lipo || command -v llvm-lipo)

mkdir -p build
cd build
wget "https://download.swift.org/swift-${version}-release/xcode/swift-${version}-RELEASE/swift-${version}-RELEASE-osx.pkg" -O source.pkg

echo "Extracting the PKG"
if command -v xar > /dev/null; then
	xar -x -f source.pkg
else
	7z x -y source.pkg > /dev/null
fi

echo "Extracting the payload"
gunzip < "swift-${version}-RELEASE-osx-package.pkg/Payload" | cpio -id "./usr/lib/swift/macosx/*.dylib" "usr/lib/swift/macosx/*.dylib"

echo "Moving the useful files"
for lib in $libs; do
	# Darling only runs x86_64 code
	"$lipo" -thin x86_64 "./usr/lib/swift/macosx/$lib.dylib" -output "../$lib.dylib"
done
cd ..
rm -rf build

python3 add-reexport.py libswiftCore.dylib /usr/lib/swift/libswiftCoreLegacy.dylib
