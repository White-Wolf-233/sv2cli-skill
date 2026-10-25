# sv2cli 官方使用指导

这是 sv2cli 项目的维护使用约定，面向使用者和自动化 Agent。适用于
0.3.0.dev2 的歌词计划核对、单次原生宿主及后续兼容版本；Synthesizer V 的原生功能和
接口定义以 Dreamtonics 文档、已安装版本及实际插件回读为准。

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

离线工程操作不要求打开 Studio。原生合成需要已安装和激活的 VST3、声库、
NumPy，以及独立构建或随便携包提供的 native 宿主。doctor 只检查前提，
`renderReadyToAttempt` 不表示已经成功合成。原生宿主构建说明在 CLI 源码的
`native/README.md`；不要把旧 DawDreamer 安装当作新宿主的替代品。

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

带歌词的 MIDI、手工写谱、PDF 转换和多段词，先读 [填词与分音](lyrics-and-syllables.md)。必须核对独立来源与各段实际文本，再核对每字/续唱音符；`validate`、F0 命中和 score-lock 不能替代这一步。

```sh
sv2cli inspect song.svp
sv2cli validate song.svp
sv2cli preflight song.svp -o preflight.json
sv2cli groups song.svp
sv2cli notes song.svp --track '#1' -o notes.json
```

轨号为一基 `#1`、`#2`；轨名必须精确且唯一。`--track` 的具体复用方式
以相应命令的 `--help` 为准，不能把各命令的选择器参数混用。
`preflight` 会定位同一声乐轨的重叠音，包括不同组引用之间的重叠。
旋律、节奏、歌词需要忠于原谱时，先核对源数据，再保持谱面字段不变。

```sh
sv2cli voice song.svp --track '#1' --name 'Kasane Teto AI 2' -o voiced.svp
sv2cli voice voiced.svp --track '#1' --language-override mandarin -o zh.svp
sv2cli edit zh.svp --recipe mix.json --score-lock -o ready.svp
sv2cli diff zh.svp ready.svp --summary
sv2cli render ready.svp --stems -o stems --sample-rate 48000 --bit-depth 24
```

声库名称、版本与语言按本机实际安装配置，示例不保证其他声库可用。
缓存目录不证明已经安装或激活。配方格式查 `recipe-schema`；效果与发声参数
按实际 schema 或有依据的原生字段填写，不根据显示名称猜字段。

新建输出默认不覆盖。用户已允许原位保存时，编辑命令使用 `--in-place`，
自动备份并原子替换；不反复询问同一授权。改谱必须明确
`--allow-score-changes`，覆盖授权本身不等于允许改变音高、时值或歌词。

## 从 MIDI 到独立声部

```sh
sv2cli convert midi-in score.mid --polyphony split --lyric-default a -o voices.svp
sv2cli preflight voices.svp
sv2cli convert midi-in performance.mid --truncate-overlaps --polyphony split -o repaired.svp
```

复音默认保留并警告，声乐渲染前会拒绝同轨重叠。split 保留音符并分轨，
但自动分轨不等于识别出原作者的 S1/S2/A1/A2/T1/T2/B1/B2：轨名和声部归属
需要对照原谱。`--top-voice` 会取最高音；`--truncate-overlaps` 会截断同音
重叠，二者都可能改变音乐数据，应按用户目的明确选择并检查转换报告。
有 MIDI 歌词事件的音符保留歌词，其余才使用 `--lyric-default`。

完整练习分轨中，同唱段要出现在每个独立声部里，不能只交内部差分轨。核对分声部入口的一字多音接续、同音延音线和回到同唱处；不要在分叉处补一次新的“啊”。没有实际分写的声部按用户要求合成一份。详见 [分声部与音高说明](midi-and-pitch.md)。

## 连续元音、滑音与断音

```sh
sv2cli tune song.svp --mode rigid --vibrato 0 -o rigid.svp
sv2cli tune song.svp --mode flat --transition-ms 5 --vibrato 0 -o flat.svp
sv2cli diff song.svp flat.svp --summary
```

rigid 设置 SV2 表达；flat 另外生成明确的原生音高曲线，控制换音过渡宽度，
不改谱面音高、起点和时值。已有音高编辑默认保留并阻止冲突写入；确实要
替换时使用 `--replace-controls`，且选择整个受影响组。
`--mode default` 只恢复默认表达，不自动删除明确写入的曲线。

音高不滑与每个元音重新起声是不同需求。需要真正留间隙时使用显式
`notes.articulate` 配方并允许改谱；不要为关闭滑音自动缩短全部音符。
不要把仅适用于 SV1 的 tF0Left/tF0Right 当成 SV2 的有效滑音开关。

## 渲染架构与失败处理

Python CLI 管理工程和任务；独立 worker 加载 C++ JUCE/VST3 宿主；宿主以
整数采样时钟驱动已授权 SynthV 插件，先保留原始 WAV，再做验收和明确选择的
增益处理。消息处理期间不推进采样位置，速度和拍号边界按采样切分。

每个输入和配置只做一次原生渲染，`--attempts` 只接受 1。失败时读取
manifest 的错误码、任务目录的日志和 coverage.json；有依据地修正输入、
配置或代码后再验证新版本。禁止按误差或缺失窗口反复渲染、自动改变阈值，
也不从多次结果里挑选一次侥幸通过。固定数量的宿主诊断对照不能替代生产修复。

```sh
sv2cli job-status stems
sv2cli render ready.svp --stems -o stems --sample-rate 48000 --bit-depth 24 --resume
```

resume 用于修复原因后恢复匹配的中断任务并复用已验证完成轨，不是自动
重试机制。配置、源数据或验收规则改变时应使用新任务；不靠 `--force`
掩盖不匹配的 checkpoint，也不删除全局缓存或终止用户的其他 Studio 实例。

## 验收与交付

```sh
sv2cli audio-check stems/01.wav
sv2cli coverage-check ready.svp stems/01.wav --track '#1' -o coverage.json
sv2cli entry-check ready.svp stems/01.wav --track '#1' -o entry.json
sv2cli timing-check ready.svp stems/01.wav --track '#1' -o timing.json
sv2cli audio-normalize mix.wav --target-peak -1 -o delivery.wav
```

示例假定 01.wav 对应源工程 #1；实际按 manifest 的轨道映射选择，不能在
跳过空轨/禁用轨后仍根据编号猜声部。新分轨共享完整原工程时间轴。
宽频起音受合法辅音提前影响时，可在检查频谱后明确选 `--landmark voiced`；
不能自动切换标记直到通过。能量有活动不代表每个音高、短字或音素都正确。

原生渲染自动核对工程与明确设置的参数回读、所有音符活动窗口、谱面活动
区间的异常静音、格式及首个独立声部起音。多轨合排需用
`--entry-policy report` 明确接受未完成独立起音验收的结果；逐声部验收用
stems。混响和其他轨会掩盖漏音，所以不能用总混音替代独立分轨检查。

逐轨独立归一化会改变声部相对电平；保留原混音平衡时对合排处理增益。
CLI 原生输出 WAV，MP3/FLAC 由实际可用的编码器另行转码；钢琴音色需要
相应乐器渲染器，不能把钢琴 MIDI 交给声库就宣称导出了钢琴伴奏。

最终报告区分：原谱核对与数据差异、实际合成与格式、活动和可测起收音、
音高分析、参考表演对照、主观听审。缺少任何一层，就明确写出该层未验证。
用户没有试听回复不等于已经接受；不能用指纹一致或 valid:true 宣称
“完全符合原谱”“所有声部绝对同时出声”。

验收中另外列出逐段歌词与逐音分配；不要将“某两个音抽查正确”推广为整轨音高正确，也不要将自相关/F0 失败直接归因为低电平。没有独立证据时保留为测量未决项。不同声部的不同旋律/歌词不能默认用整段能量互相关当统一时间真值；先在同拍、同歌词或有明确信号锚点的独立片段上核查。

更细的故障与数据选项见 [MIDI 与音高说明](midi-and-pitch.md)，时序定位见
[时序与表达](timing-and-expression.md)，交付与续跑见 [交付说明](delivery.md)。
