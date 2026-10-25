# 编辑与实际渲染

优先使用 CLI 的稳定编辑路径，不直接改裸 JSON。recipe 顶层未知字段会被拒绝，`recipe-schema` 给出每种操作的必填/可选字段。版本相关的原生字段仍需依据实际 SVP 样本。

```sh
sv2cli inspect song.svp
sv2cli validate song.svp
sv2cli edit song.svp --recipe recipe.json --score-lock --in-place --dry-run
sv2cli edit song.svp --recipe recipe.json --score-lock --in-place
```

原位写入自动创建 `song.svp.<timestamp>.bak`。`voice/mixer/repair/edit` 支持原位写入；`-o song.svp --force` 也允许覆盖。源工程执行期间被其他程序修改会拒绝覆盖。不要为每次覆盖再次索取已经给出的许可；用户要求另存时则不用原位覆盖。

覆盖不放松谱面约束。只改音色/混音时保持 score-lock，改谱面时值需要 allow-score-changes，不能同时期待 score-lock 放行。受控 JSON Patch 使用 test 检查版本/原值，仍受验证和谱面锁约束。

voice 的名称匹配是精确的。`voices` 缓存目录不是安装或激活证明；从原工程/安装信息核对 name/backendType/version/language/phoneset，必要时实际渲染三音符探针。默认数据库参数不是跨声库通用答案。对 vocalModeParams、phonemes、effects 和特殊 note attributes，不臆造原生结构。

`paramToneShift` 为 cents，不是 MIDI 转调。改变 gender/tension/loudness 可以影响表现，但不是“变成另一个歌手”的保证。换库核对 Mandarin/xsampa、Japanese/romaji，避免只改显示名称。

## 保留认可的音色，再局部处理气泡音

用户认可整体音色、只担心气泡音或沙哑时，先保存该版的实际音频、源工程、声库身份、各引用 voice/Vocal Mode、表达曲线与混音/效果配置及哈希，作为任务内音色基准。将“整体音色认可”和“低音/句尾的气泡音尚待优化”分开记录，不因为局部问题全曲换库、转调或反复改所有声部的 Gender。保存旧版是音色参考，不等于旧版谱面/时序也通过验收。

定位到同一干声片段，排除削波、编码和混音掩蔽，再检查低音区、气声、张力、音色变形与 Vocal Mode。参数作用方向从实际版本/文档核实，不能靠 male/female 标签猜正负号。音色处理不自动改音符八度、歌词或时值；调整表达时保留无关曲线。自然低频周期、粗糙声、齿音和削波不可只凭宽带能量相互归因。

有依据地做局部或单声部候选，与认可基准按相同时间段、相近响度比较，检查起音/连唱是否退化。程序可验证参数写入、保谱和波形，不能证明“气泡音已经消除”或“比原版更好听”；需要实际试听才记录听感接受。合排要同步使用更新的目标声部，旧声部和认可版本保留。

```sh
sv2cli render song.svp --track '#1' -o lead.wav --warmup 30 --attempts 1 --timeout 1800
sv2cli render song.svp --stems -o stems --bit-depth 24
```

原生宿主按整数采样时钟单次渲染，禁止重渲染收敛或自动回退旧宿主。有声文件不等于验收通过；检查所有音符活动、谱面活动区间的异常静音、实际起音和格式。插件回读核对谱面及显式表达/音高曲线/效果参数，仍不证明目标听感。需要真实试听的需求应制作短 A/B，区分可程序化检查与听审。
