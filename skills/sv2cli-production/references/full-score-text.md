# 全曲文本化

把 SVP 工程转成可读的结构化 JSON：段落 → 小节 → 音符，每个音符含歌词、音程、音高。

## 命令

```sh
sv2cli full-score-text song.svp -o score.json
```

输出结构：

```
{
  "tracks": [
    {
      "track": 1,
      "name": "Track 1",
      "sections": [
        {
          "label": "bars 1–8",
          "bars": [
            {
              "bar": 1,
              "notes": [
                {
                  "beat": 1.0,
                  "onset_q": 0.0,
                  "duration_q": 1.0,
                  "pitch": 60,
                  "midi": 60,
                  "lyrics": "山",
                  "phonemes": "",
                  "musicalType": "singing",
                  "interval_from_prev": {
                    "semitones": 2,
                    "name": "M2",
                    "octaves": 0,
                    "direction": "up",
                    "dissonant": true
                  }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## 用途

| 目标 | 用法 |
|------|------|
| 人工校对全曲歌词 | 按 bar → lyrics 逐行读 |
| 检查不协和音程落点 | 过滤 `interval_from_prev.dissonant == true` |
| 动机搜索 | 传给 `motif_distance.py` |
| 段落响度 / 音域分析 | 结合 `loudness-check` 的 shortTermBins |
| 生成歌词翻译对照 | 按 onset_q 排序后逐音输出 |

## 音程标记

`interval_from_prev` 是当前音符相对于同轨前一个音符的音程。首个音符为 null。  
`dissonant` 按 m2 M2 TT m7 M7 标注，仅供参考，实际协和度依调性语境判断。

## 段落边界

默认按小节间隔检测（连续小节归同一段，间隔处断开）。  
精确段落标注需要外部结构表，参见 [song-structure.md](song-structure.md)。

## 配合歌词检查

`full-score-text` 只导出数据，不核对歌词计划。  
核对用 `lyrics-check`：

```sh
sv2cli lyrics-check song.svp --plan plan.json --require-full-project -o audit.json
```

两步分开：先用 full-score-text 确认旋律结构和歌词排布，再用 lyrics-check 核对计划匹配。
