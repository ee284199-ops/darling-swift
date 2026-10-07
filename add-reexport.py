#!/usr/bin/env python3
# Add an LC_REEXPORT_DYLIB load command to a thin 64-bit Mach-O dylib, so that it also exports
# the symbols of another dylib. The command goes into the padding between the load commands and
# the first section, like install_name_tool's edits. Running it again changes nothing.
#
# usage: add-reexport.py <dylib> <install name of the dylib to re-export>
import struct
import sys

MH_MAGIC_64 = 0xFEEDFACF
LC_SEGMENT_64 = 0x19
LC_REEXPORT_DYLIB = 0x8000001F
MH_NO_REEXPORTED_DYLIBS = 0x100000

if len(sys.argv) != 3:
    sys.exit("usage: add-reexport.py <dylib> <install name of the dylib to re-export>")
path, name = sys.argv[1], sys.argv[2]

with open(path, "rb") as f:
    data = bytearray(f.read())

magic, _, _, _, ncmds, sizeofcmds, flags = struct.unpack_from("<7I", data, 0)
if magic != MH_MAGIC_64:
    sys.exit("%s: not a thin 64-bit Mach-O file" % path)

# The load commands can grow up to the first byte of section data.
first_section = len(data)
off = 32
for _ in range(ncmds):
    cmd, cmdsize = struct.unpack_from("<2I", data, off)
    if cmd == LC_SEGMENT_64:
        nsects = struct.unpack_from("<I", data, off + 64)[0]
        for i in range(nsects):
            sect_offset = struct.unpack_from("<I", data, off + 72 + i * 80 + 48)[0]
            if sect_offset != 0:  # zero-fill sections have no file data
                first_section = min(first_section, sect_offset)
    elif cmd == LC_REEXPORT_DYLIB:
        name_offset = struct.unpack_from("<I", data, off + 8)[0]
        existing = bytes(data[off + name_offset:off + cmdsize]).split(b"\0")[0].decode()
        if existing == name:
            print("%s already re-exports %s" % (path, name))
            sys.exit(0)
    off += cmdsize

encoded = name.encode() + b"\0"
size = (24 + len(encoded) + 7) & ~7
if off + size > first_section:
    sys.exit("%s: no room for another load command (%d bytes free, %d needed)"
             % (path, first_section - off, size))
if any(data[off:off + size]):
    sys.exit("%s: the space after the load commands is not empty" % path)

# dylib_command: name offset, timestamp, current version, compatibility version (1.0.0)
command = struct.pack("<6I", LC_REEXPORT_DYLIB, size, 24, 2, 0x10000, 0x10000) + encoded
data[off:off + size] = command.ljust(size, b"\0")
struct.pack_into("<3I", data, 16, ncmds + 1, sizeofcmds + size, flags & ~MH_NO_REEXPORTED_DYLIBS)

with open(path, "wb") as f:
    f.write(data)
print("%s now re-exports %s" % (path, name))
