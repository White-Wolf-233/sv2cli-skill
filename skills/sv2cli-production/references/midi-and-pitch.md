# MIDI、短音与平直音高

先确认调用的是当前工具：`--version` 和 `doctor` 会报告包路径、Python 与 nativeHost。旧全局命令可能仍指向 0.1.0；沿用任务的私有环境或明确启动器，不自行更改全局 PATH。

```sh
sv2cli convert midi-in score.mid --polyphony split --lyric-default a -o imported.svp
sv2cli preflight imported.svp
sv2cli tune song.svp --mode flat --transition-ms 5 --vibrato 0 -o flat.svp
sv2cli coverage-check song.svp isolated.wav --track '#1' -o coverage.json
```

默认 MIDI 复音原样保留并警告；同轨和弦/重叠会在声乐渲染前失败，不能让引擎静默丢声。`--polyphony split` 保留每个音符的音高和时值并分轨；`--top-voice` 会舍弃或截短较低声部；`--truncate-overlaps` 显式截断同音重叠、按 FIFO 配对 note-off，转换报告列出改动。不要默认替用户丢音、截音。无歌词事件的默认歌词为 la，可用 --lyric-default 设置。

同元音连续发声与音高滑动是两个问题。SV2 的 --mode rigid 调整表达；--mode flat 生成覆盖音高曲线并控制换音宽度，保持谱面音符与时值。已有音高编辑默认不覆盖，--replace-controls 只允许整组明确替换。--mode default 只恢复默认表达，不自动删掉已有曲线。不要向 SV2 填入仅在 SV1 有效的 tF0Left/tF0Right 并假装成功。

需要每音断开时，recipe notes.articulate 的 gapMs 会真实缩短 duration，必须明确 allow-score-changes。它不能作为默认的关滑音办法。音高曲线写入后仍检查插件回读与实际声音；平直音高不代表准确发音或主观满意。

效果字段、支持的枚举和数值约束通过 recipe-schema.effects 获取。clean 是已支持的混响类型；不要从名称猜测其他枚举，未知厂商扩展使用有依据的 JSON Patch。
