# 歌曲结构

## 常见曲式

| 标签 | 含义 | 典型小节数 |
|------|------|-----------|
| Intro | 前奏，建立氛围 | 4–16 |
| Verse (A) | 主歌，叙事推进 | 8–16 |
| Pre-chorus | 导歌，累积张力 | 4–8 |
| Chorus (B) | 副歌，主题高潮 | 8–16 |
| Bridge (C) | 桥段，对比转折 | 8 |
| Outro | 尾奏，渐弱收尾 | 4–8 |
| Interlude | 间奏 | 4–8 |

通俗结构：Intro → Verse → Pre → Chorus → Verse → Pre → Chorus → Bridge → Chorus → Outro  
简化结构：Verse → Chorus × 2 → Bridge → Chorus  
through-composed：无重复段，逐段发展

## 写作要点

- 副歌旋律最高音通常是全曲的音域顶点。
- 桥段换调、换节奏或换织体，制造"第三种感觉"。
- 相邻段落的末音和下一段的起音音程若为纯四/五度或大小三度，衔接自然；小二度会制造张力感。
- 前奏通常复用副歌旋律或其核心动机，让听众熟悉后有期待感。

## 在 sv2cli 中标注段落

用 `full-score-text` 的 JSON 输出作为基础，给每段加 `section_label`：

```python
# 示例：按小节范围给每个 phrase 打标签
SECTIONS = {range(1,5):'Intro', range(5,21):'Verse1', range(21,37):'Chorus1'}

def label(bar):
    for r,s in SECTIONS.items():
        if bar in r: return s
    return 'unknown'
```

段落标注确定后录入 motif-log（`motif-log-template.json`），以便动机追踪时关联段次。
