"""
phrase_merge.py — 逐句分工后合并进全曲歌词计划库。

工作流：
  1. 对每一句单独生成 lyrics-plan 片段（JSON 对象，含 id/start/end/text/notes）。
  2. 用本脚本把各片段 merge 进总计划文件，检测 id 重复和小节重叠。
  3. 合并后的计划用于 lyrics-check / render --lyrics-plan。

用法：
    # 把 phrase_verse1_line2.json 合并进 master-plan.json
    python phrase_merge.py master-plan.json phrase_verse1_line2.json [更多片段...]

    # 读取 stdin 的片段（方便管道）
    echo '{"id":"v1l3",...}' | python phrase_merge.py master-plan.json -

输出：覆盖 master-plan.json（先备份为 .bak）。

片段格式（单个 phrase 对象）：
{
  "id": "verse-1-line-2",
  "start": "4",
  "end": "8",
  "text": "山河",
  "notes": [ {"at": "4", "dur": "1", "pitch": 60, "lyrics": "山"}, ... ]
}

master-plan 格式与 sv2cli lyrics-plan-schema 一致；
片段中可指定 "track_selector"（默认 "#1"）决定归入哪条轨。
"""
import argparse, json, sys
from pathlib import Path

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def save(path, data):
    p = Path(path)
    bak = p.with_suffix(p.suffix + '.bak')
    if p.exists():
        bak.write_bytes(p.read_bytes())
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(bak) if bak.exists() else None

def _fraction(s):
    from fractions import Fraction
    return Fraction(str(s))

def merge_phrase(master, phrase):
    selector = phrase.get('track_selector', '#1')
    # find or create track entry
    track = None
    for t in master.setdefault('tracks', []):
        if t.get('selector') == selector:
            track = t
            break
    if track is None:
        track = {'selector': selector, 'phrases': []}
        master['tracks'].append(track)

    # duplicate id check
    existing_ids = {ph['id'] for ph in track.get('phrases', [])}
    pid = phrase.get('id', '')
    if pid in existing_ids:
        return False, f"duplicate phrase id '{pid}' in track {selector}"

    # overlap check
    new_start = _fraction(phrase.get('start', '0'))
    new_end   = _fraction(phrase.get('end', '0'))
    for ph in track.get('phrases', []):
        s = _fraction(ph.get('start', '0'))
        e = _fraction(ph.get('end', '0'))
        if new_start < e and new_end > s:
            return False, f"phrase '{pid}' [{phrase['start']},{phrase['end']}) overlaps existing '{ph['id']}' [{ph['start']},{ph['end']})"

    p_entry = {
        'id': pid,
        'start': str(phrase['start']),
        'end': str(phrase['end']),
        'text': phrase.get('text', ''),
        'notes': phrase.get('notes', []),
    }
    track['phrases'].append(p_entry)
    track['phrases'].sort(key=lambda x: _fraction(x['start']))
    return True, 'ok'

def main():
    p = argparse.ArgumentParser(description='Merge phrase fragments into a master lyrics plan')
    p.add_argument('master', help='Master plan JSON (created if missing)')
    p.add_argument('fragments', nargs='+', help='Phrase JSON files or - for stdin')
    a = p.parse_args()

    mp = Path(a.master)
    if mp.exists():
        master = load(a.master)
    else:
        master = {'source': {'reference': '', 'reviewed': False}, 'tracks': []}

    errors = []
    merged = 0
    for frag_path in a.fragments:
        if frag_path == '-':
            phrase = json.load(sys.stdin)
        else:
            phrase = load(frag_path)
        ok, msg = merge_phrase(master, phrase)
        if ok:
            merged += 1
            print(f'  merged: {phrase.get("id", "?")}')
        else:
            errors.append(msg)
            print(f'  ERROR: {msg}', file=sys.stderr)

    bak = save(a.master, master)
    total = sum(len(t.get('phrases', [])) for t in master.get('tracks', []))
    print(f'\nmerged {merged} phrase(s). master now has {total} phrase(s).')
    if bak:
        print(f'backup: {bak}')
    if errors:
        print(f'{len(errors)} error(s); master saved with successful merges only.')
        sys.exit(1)

if __name__ == '__main__':
    main()
