"""Compatibility entry point; all lyric-plan validation lives in sv2cli."""
import sys

try:
    import sv2cli.lyrics
    from sv2cli.cli import main
except ImportError:
    print("Requires sv2cli 0.3.0.dev2+ with lyrics-check. Use the verified private CLI environment; do not fall back to an older global install.", file=sys.stderr)
    raise SystemExit(2)

if __name__ == '__main__':
    raise SystemExit(main(['lyrics-check', *sys.argv[1:]]))
