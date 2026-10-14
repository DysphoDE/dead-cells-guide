"""Minimaler GNU-.mo-Parser (UTF-8), liefert dict msgid -> msgstr (Kontext 'ctx\x04id' bleibt erhalten)."""
import struct

def read_mo(path):
    b = open(path, "rb").read()
    magic = struct.unpack("<I", b[:4])[0]
    e = "<" if magic == 0x950412DE else ">"
    _, n, oo, to = struct.unpack(e + "4I", b[4:20])
    out = {}
    for i in range(n):
        ol, op = struct.unpack(e + "2I", b[oo + 8 * i: oo + 8 * i + 8])
        tl, tp = struct.unpack(e + "2I", b[to + 8 * i: to + 8 * i + 8])
        k = b[op:op + ol].decode("utf-8", "replace")
        v = b[tp:tp + tl].decode("utf-8", "replace")
        out[k] = v
    return out
