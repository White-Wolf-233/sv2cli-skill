"""
motif_distance.py — 从 full-score-text 导出中找动机片段，
报告每次出现离上次的距离（四分拍数）。

用法：
    sv2cli full-score-text song.svp -o score.json
    python motif_distance.py score.json --motif "5 7 5" --track 1

--motif 是以空格分隔的 MIDI 音高序列，匹配精确音高，允许任意节奏。
--interval 改为按音程轮廓匹配，值是以空格分隔的半音数（有符号）。
--track 只在指定轨中搜索，省略则全轨。

输出 JSON：每次出现的起始小节、拍位、onset_q、距上次出现的四分拍间隔。
"""
import argparse, json, sys

def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def all_notes(data, track=None):
    rows = []
    for t in data['tracks']:
        if track is not None and t['track'] != track:
            continue
        for sec in t['sections']:
            for bar in sec['bars']:
                for n in bar['notes']:
                    rows.append({'track': t['track'], 'bar': bar['bar'], **n})
    return sorted(rows, key=lambda n: (n['track'], n['onset_q']))

def find_pitch_motif(notes, motif_pitches):
    hits = []
    m = len(motif_pitches)
    for i in range(len(notes) - m + 1):
        if [notes[i+j]['midi'] for j in range(m)] == motif_pitches:
            end = max(n['onset_q'] + n['duration_q'] for n in notes[i:i+m])
            hits.append({**notes[i], 'end_q': end})
    return hits

def find_interval_motif(notes, semitone_intervals):
    hits = []
    m = len(semitone_intervals)
    for i in range(len(notes) - m):
        if all(notes[i+j+1]['midi'] - notes[i+j]['midi'] == semitone_intervals[j] for j in range(m)):
            end = max(n['onset_q'] + n['duration_q'] for n in notes[i:i+m+1])
            hits.append({**notes[i], 'end_q': end})
    return hits

def main():
    p = argparse.ArgumentParser(description='Locate motif recurrences in full-score-text output')
    p.add_argument('score', help='full-score-text JSON output')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--motif', help='Space-separated MIDI pitches, e.g. "60 62 64"')
    g.add_argument('--interval', help='Space-separated signed semitones, e.g. "2 2 -4"')
    p.add_argument('--track', type=int, default=None)
    a = p.parse_args()

    data = load(a.score)
    notes = all_notes(data, a.track)

    try:
        pattern = list(map(int, (a.motif if a.motif is not None else a.interval).split()))
        if not pattern:
            p.error('Provide at least one pitch or interval')
    except ValueError:
        p.error('Pitches and intervals must be integers')
    mode = 'pitch' if a.motif is not None else 'interval'
    from itertools import groupby
    hits = []
    for _, track_notes in groupby(notes, key=lambda n: n['track']):
        sequence = list(track_notes)
        search = find_pitch_motif if mode == 'pitch' else find_interval_motif
        hits.extend(search(sequence, pattern))

    result = []
    previous = {}
    for h in sorted(hits, key=lambda n: (n['onset_q'], n['track'])):
        prev = previous.get(h['track'])
        dist = round(h['onset_q'] - prev['onset_q'], 4) if prev is not None else None
        gap = round(h['onset_q'] - prev['end_q'], 4) if prev is not None else None
        result.append({
            'track': h['track'], 'bar': h['bar'], 'beat': h['beat'],
            'onset_q': h['onset_q'], 'lyrics': h['lyrics'],
            'distance_from_prev_q': dist,
            'end_q': round(h['end_q'], 4),
            'duration_q': round(h['end_q'] - h['onset_q'], 4),
            'gap_from_prev_q': gap,
        })
        previous[h['track']] = h

    out = {'mode': mode, 'matchCount': len(result), 'occurrences': result}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()

if __name__ == '__main__':
    main()
