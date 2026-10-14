"""Liest das Verzeichnis der Dead-Cells-res.pak (Heaps-PAK-Format) und extrahiert ausgewählte Dateien.
Nutzung: python -I tools/pak_extract.py <res.pak> list [filter]
         python -I tools/pak_extract.py <res.pak> extract <pfad-im-pak> <zieldatei>
Nur lesend; die Spieldatei wird nicht verändert."""
import struct, sys

def read_dir(f):
    assert f.read(3) == b"PAK", "kein PAK"
    version = f.read(1)[0]
    header_size, data_size = struct.unpack("<ii", f.read(8))
    if version >= 1:
        f.read(64)  # Build-Stempel (Hash)
    files = []
    def rd(prefix):
        n = f.read(1)[0]
        name = f.read(n).decode("utf-8")
        flags = f.read(1)[0]
        path = (prefix + "/" + name) if prefix else name
        if flags & 1:
            count = struct.unpack("<i", f.read(4))[0]
            for _ in range(count):
                rd(path)
        else:
            if flags & 2:
                pos = struct.unpack("<d", f.read(8))[0]
            else:
                pos = struct.unpack("<i", f.read(4))[0]
            size, chk = struct.unpack("<ii", f.read(8))
            files.append((path, int(pos), size))
    rd("")
    return header_size, files

def main():
    pak, cmd = sys.argv[1], sys.argv[2]
    with open(pak, "rb") as f:
        hs, files = read_dir(f)
        if cmd == "list":
            flt = sys.argv[3] if len(sys.argv) > 3 else ""
            for p, pos, size in files:
                if flt in p:
                    print(p, size)
        elif cmd == "extract":
            want, out = sys.argv[3], sys.argv[4]
            for p, pos, size in files:
                if p == want or p.endswith("/" + want):
                    f.seek(hs + pos)
                    open(out, "wb").write(f.read(size))
                    print("wrote", out, size)
                    return
            print("not found")

if __name__ == "__main__":
    main()
