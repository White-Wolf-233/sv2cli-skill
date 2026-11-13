---
name: sv2cli-production
description: 使用 sv2cli 编辑、渲染和验收 Synthesizer V Studio 2 工程；填词分音、音程检查、动机追踪、响度分析、分轨交付。
---

# SV2 工程制作

工具版本：sv2cli 0.3.0.dev2 或更新。每次使用前确认：

```sh
sv2cli --version && sv2cli doctor && sv2cli capabilities
```

## 按需加载说明

只读与当前任务相关的 ref，不要一次加载全部。

| 任务 | 加载 |
|------|------|
| 首次使用、端到端步骤 | [official-usage.md](references/official-usage.md) |
| 音色、声库、编辑渲染 | [edit-and-render.md](references/edit-and-render.md) |
| 填词、分音、逐音计划 | [lyrics-and-syllables.md](references/lyrics-and-syllables.md) |
| 时序、起收音、表情 | [timing-and-expression.md](references/timing-and-expression.md) |
| 渲染失败、分轨、交付 | [delivery.md](references/delivery.md) |
| 进度、质量闭环、反馈 | [feedback-loop.md](references/feedback-loop.md) |
| MIDI、短音、平直音高 | [midi-and-pitch.md](references/midi-and-pitch.md) |
| 乐理、不协和音程 | [music-theory.md](references/music-theory.md) |
| 曲式、段落结构 | [song-structure.md](references/song-structure.md) |
| 押韵、歌词写作 | [rhyme-and-lyrics.md](references/rhyme-and-lyrics.md) |
| 动机记录与追踪 | [motif-tracking.md](references/motif-tracking.md) |
| 响度 LUFS 分析 | [loudness.md](references/loudness.md) |
| 全曲文本化导出 | [full-score-text.md](references/full-score-text.md) |
| 素材和模板 | [sample-library.md](references/sample-library.md) |

## 执行原则

1. 明确输入工程、目标轨、改动目标和输出。只有缺少会改变结果的信息才提问。
2. 区分三类需求：修正谱面 onset/duration；修正实际起收音；对齐参考表演。
3. `inspect` → `validate` → `preflight`，用 `groups`/`notes` 确认选择器，再操作。
4. 把要求转成 recipe，检查 `recipe-schema`。用 score-lock 保护不需要改的谱面数据。
5. 覆盖时用 `--in-place` 或 `-o 原工程 --force`，工具自动备份。
6. 需要音频时先做代表性短片段，再完整渲染。每个输入配置只渲染一次。
7. 验收分别报告：谱面差异、实际发声时序、参考表演对照、听审结论。

## 动机追踪强制规则

处理全曲时，对每个核心动机必须：
- 在 `motif-log.json` 记录全曲出现次数和每次的 treatment 与 distance_from_prev_q。
- 在交付报告中明确写出出现次数和最大间隔（小节数）。
- 间隔 > 32 小节标注为潜在结构断裂。

## 完成标准

用户要求修改工程 → 交付实际保存的工程文件，说明覆盖路径和备份路径。  
用户要求音频 → 交付本次生成并读回检查的音频，列出未决项。
