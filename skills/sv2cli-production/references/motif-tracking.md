# 动机追踪

## 什么是动机

动机（motif）是由 2–8 个音构成的最小旋律单元，同时包含音程轮廓和节奏骨架。  
一首歌的结构统一感通常来自核心动机在各段中的处理和变体。

## 动机信息字段（录入 motif-log.json）

每个动机必须记录：

| 字段 | 内容 |
|------|------|
| `id` | 唯一标识，如 `motif-A` |
| `pitch_contour` | MIDI 音高序列 |
| `interval_contour` | 有符号半音差序列 |
| `rhythm` | 四分拍为单位的时值序列 |
| `first_statement` | 首次出现的小节/轨 |
| `occurrences` | 每次出现，含 treatment 和 distance_from_prev_q |

treatment 枚举：`statement` / `sequence` / `truncation` / `variation` / `augmentation` / `diminution` / `inversion` / `retrograde` / `development` / `recapitulation`

## 搜索和计算

```sh
# 导出全曲文本
sv2cli full-score-text song.svp -o score.json

# 按音高精确匹配
python scripts/motif_distance.py score.json --motif "60 62 64 62" --track 1

# 按音程轮廓匹配（允许任意移调）
python scripts/motif_distance.py score.json --interval "2 2 -2"
```

输出字段 `distance_from_prev_q`：从上次出现的起点到本次起点，单位四分拍。  
如果想算"上次唱完到现在多久"：`distance_from_prev_q - prev_duration_q`。

## 密度规则

- 副歌中核心动机至少出现 2 次，建立记忆点。
- 相邻两次出现间隔 < 2 拍视为密集叠用，需要有意图（如高潮堆叠）。
- 动机完全消失超过 16 小节，再出现时建议标注 `recapitulation`。

## 强制记录规则

Agent 在处理全曲时必须：

1. 对每个核心动机，在 motif-log.json 中记录**全曲出现次数**（`occurrences` 长度）。
2. 每次出现都填写 `treatment` 和 `distance_from_prev_q`。
3. 在交付报告中明确写出每个动机的出现次数和最大间隔。
4. 若有间隔 > 32 小节，标注为潜在结构断裂。

motif-log.json 使用 [assets/motif-log-template.json](../assets/motif-log-template.json) 初始化。

## 与段落结构关联

在 `occurrences` 条目中加 `section_label`（Verse/Chorus/Bridge 等），配合 [song-structure.md](song-structure.md) 确认动机在哪些段出现、哪些段缺失。核心动机在 Bridge 通常做变体或回避，在 Chorus 再现或加强。
