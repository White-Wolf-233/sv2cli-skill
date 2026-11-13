# sv2cli 官方使用指导

sv2cli 0.3.0.dev2 使用约定，面向使用者和自动化 Agent。

## 先确认正在使用哪一份工具

```sh
sv2cli --version
sv2cli doctor
sv2cli capabilities
sv2cli recipe-schema
sv2cli lyrics-plan-schema
sv2cli lyrics-check --help
```

下文用 `sv2cli` 表示当前版本的入口。Windows 便携包中使用
`.\sv2cli.cmd`；私有虚拟环境中可使用 `.\.venv\Scripts\sv2cli.exe`。
重点核对 doctor 的 `version`、`pythonExecutable`、`packagePath`、
`nativeHost` 和 `renderReadyToAttempt`。下载源码、更新 skill 或打开新终端
不会自动替换另一个 editable 安装；远端是否已有对应发布也以实际版本为准。

离线工程操作不要求打开 Studio。原生合成需要已安装和激活的 VST3、声库、NumPy 及独立构建或随便携包提供的 native 宿主。doctor 检查前提，`renderReadyToAttempt` 是检查结果，不代表已合成。native 宿主构建说明在 CLI 源码的 `native/README.md`。

## 按输入选择入口

| 输入或目标 | 推荐入口 | 需要注意 |
|---|---|---|
| 已有 SVP | inspect → validate → preflight | 结构正确不代表适合单声部演唱 |
| MIDI 合成声乐 | convert midi-in，再配置声库 | 和弦应拆成独立声部；默认歌词为 la |
| PDF / MusicXML 乐谱 | 先取得并核对对应 SVP/MIDI | 本 CLI 不执行 PDF 识谱或完整 MusicXML 导入 |
| 已有 WAV 漏声、起音问题 | coverage-check / entry-check / timing-check | 先检查现有录音，保留原始文件 |
| 降低自动滑音 | tune 的 rigid / flat | 不必缩短原谱音符 |
| 交付电平 | audio-normalize / render --target-peak | 采样峰值增益，不是 LUFS 或真峰值归一化 |

## 已有工程的标准路径

带歌词的 MIDI、手工写谱、PDF 转换和多段词，先读 [填词与分音](lyrics-and-syllables.md)。核对独立来源与各段实际文本，再核对每字/续唱音符。

```sh
sv2cli inspect song.svp
sv2cli validate song.svp
sv2cli preflight song.svp -o preflight.json
sv2cli groups song.svp
sv2cli notes song.svp --track '#1' -o notes.json
```

轨号为一基 `#1`、`#2`；轨名必须精确且唯一。各命令的 `--track` 选择器以相应命令的 `--help` 为准。
`preflight` 会定位同一声乐轨的重叠音，包括不同组引用之间的重叠。
旋律、节奏、歌词需要忠于原谱时，先核对源数据，再保持谱面字段不变。

```sh
sv2cli voice song.svp --track '#1' --name 'Kasane Teto AI 2' -o voiced.svp
sv2cli voice voiced.svp --track '#1' --language-override mandarin -o zh.svp
sv2cli edit zh.svp --recipe mix.json --score-lock -o ready.svp
sv2cli diff zh.svp ready.svp --summary
sv2cli render ready.svp --stems -o stems --sample-rate 48000 --bit-depth 24
```

声库名称、版本与语言按本机实际安装配置，示例不保证其他声库可用。配方格式查 `recipe-schema`；效果与发声参数按实际 schema 或原生字段填写。

新建输出默认不覆盖。允许原位保存时，编辑命令使用 `--in-place`，自动备份并原子替换。改谱必须明确 `--allow-score-changes`。

## 从 MIDI 到独立声部

```sh
sv2cli convert midi-in score.mid --polyphony split --lyric-default a -o voices.svp
sv2cli preflight voices.svp
sv2cli convert midi-in performance.mid --truncate-overlaps --polyphony split -o repaired.svp
```

split 保留音符并分轨，轨名和声部归属需要对照原谱。`--top-voice` 取最高音；`--truncate-overlaps` 截断同音重叠，二者都可能改变音乐数据，按用户目的明确选择并检查转换报告。有 MIDI 歌词事件的音符保留歌词，其余才使用 `--lyric-default`。

完整练习分轨中，同唱段要出现在每个独立声部里。核对分声部入口的一字多音接续和同音延音线。没有实际分写的声部按用户要求合成一份。详见 [分声部与音高说明](midi-and-pitch.md)。

## 连续元音、滑音与断音

```sh
sv2cli tune song.svp --mode rigid --vibrato 0 -o rigid.svp
sv2cli tune song.svp --mode flat --transition-ms 5 --vibrato 0 -o flat.svp
sv2cli diff song.svp flat.svp --summary
```

rigid 设置 SV2 表达；flat 另外生成明确的原生音高曲线，控制换音过渡宽度，不改谱面音高、起点和时值。已有音高编辑默认保留并阻止冲突写入；确实要替换时使用 `--replace-controls`，且选择整个受影响组。`--mode default` 只恢复默认表达，不自动删除明确写入的曲线。

音高不滑与每个元音重新起声是不同需求。真正需要间隙时使用显式 `notes.articulate` 配方并允许改谱。SV2 中 tF0Left/tF0Right 无效。

## 渲染架构与失败处理

Python CLI 管理工程和任务；独立 worker 加载 C++ JUCE/VST3 宿主；宿主以
整数采样时钟驱动已授权 SynthV 插件，先保留原始 WAV，再做验收和明确选择的
增益处理。消息处理期间不推进采样位置，速度和拍号边界按采样切分。

每个输入和配置只做一次原生渲染，`--attempts` 只接受 1。失败时读取 manifest 的错误码、任务目录日志和 coverage.json，修正原因后再验证新版本。

```sh
sv2cli job-status stems
sv2cli render ready.svp --stems -o stems --sample-rate 48000 --bit-depth 24 --resume
```

resume 用于修复原因后恢复匹配的中断任务并复用已验证完成轨。配置、源数据或验收规则改变时使用新任务。

## 验收与交付

```sh
sv2cli audio-check stems/01.wav
sv2cli coverage-check ready.svp stems/01.wav --track '#1' -o coverage.json
sv2cli entry-check ready.svp stems/01.wav --track '#1' -o entry.json
sv2cli timing-check ready.svp stems/01.wav --track '#1' -o timing.json
sv2cli audio-normalize mix.wav --target-peak -1 -o delivery.wav
```

实际按 manifest 的轨道映射选择声部文件。新分轨共享完整原工程时间轴。宽频起音受合法辅音提前影响时，可在检查频谱后明确选 `--landmark voiced`。

原生渲染自动核对工程与参数回读、所有音符活动窗口、谱面活动区间的异常静音及首个独立声部起音。多轨合排用 `--entry-policy report`；逐声部验收用 stems。

逐轨独立归一化会改变声部相对电平；保留原混音平衡时对合排整体处理增益。CLI 原生输出 WAV，MP3/FLAC 由实际可用的编码器另行转码。

最终报告区分：原谱核对与数据差异、实际合成与格式、活动和可测起收音、音高分析、参考表演对照、主观听审。缺少任何一层，明确写出该层未验证。逐段歌词与逐音分配单独列出。

更细的故障与数据选项见 [MIDI 与音高说明](midi-and-pitch.md)，时序定位见
[时序与表达](timing-and-expression.md)，交付与续跑见 [交付说明](delivery.md)。
