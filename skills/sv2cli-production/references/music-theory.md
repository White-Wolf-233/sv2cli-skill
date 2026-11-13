# 乐理速查

## 音程

| 半音数 | 名称 | 类型 |
|--------|------|------|
| 0 | 纯一度 P1 | 协和 |
| 1 | 小二度 m2 | 不协和 |
| 2 | 大二度 M2 | 不协和 |
| 3 | 小三度 m3 | 不完全协和 |
| 4 | 大三度 M3 | 不完全协和 |
| 5 | 纯四度 P4 | 协和（上下文敏感）|
| 6 | 增四/减五 TT | 不协和 |
| 7 | 纯五度 P5 | 协和 |
| 8 | 小六度 m6 | 不完全协和 |
| 9 | 大六度 M6 | 不完全协和 |
| 10 | 小七度 m7 | 不协和 |
| 11 | 大七度 M7 | 不协和 |
| 12 | 纯八度 P8 | 协和 |

声部写作中，小二度、大七度、增四/减五在强拍落点视为需要解决的不协和音；二声部进行中平行纯五度和纯八度削弱独立性。

`full-score-text` 输出的 `interval_from_prev.dissonant` 字段已按上表标注。

## 调式与大小调

| 调式 | 全音/半音序列（T=全，S=半）|
|------|--------------------------|
| 自然大调 | T T S T T T S |
| 自然小调 | T S T T S T T |
| 和声小调 | T S T T S 增2 S |
| 多利安 | T S T T T S T |
| 弗里几安 | S T T T S T T |
| 利底安 | T T T S T T S |
| 混合利底安 | T T S T T S T |

## 和弦

三和弦：根音 + 三度 + 五度。  
大三和弦：M3 + m3（上）；小三和弦：m3 + M3；减三和弦：m3 + m3；增三和弦：M3 + M3。  
属七（V7）：大三和弦 + 小七度，含强烈的解决倾向到主音（I）。

## 节拍强弱

4/4：强 弱 次强 弱  
3/4：强 弱 弱  
6/8：强 弱 弱 次强 弱 弱  

押韵和强调字应优先对齐强拍。多音节词中重读音节对齐强拍，轻读音节放弱拍或弱位。

## 在 sv2cli 中查音程

```sh
# 导出全曲结构化文本，interval_from_prev 包含不协和标记
sv2cli full-score-text song.svp -o score.json

# 筛查不协和音程
python -c "
import json
d=json.load(open('score.json'))
for t in d['tracks']:
    for s in t['sections']:
        for b in s['bars']:
            for n in b['notes']:
                iv=n.get('interval_from_prev')
                if iv and iv['dissonant']:
                    print(f\"bar {b['bar']} beat {n['beat']} track {t['track']}: {iv['name']} {iv['direction']} lyrics={n['lyrics']!r}\")
"
```
