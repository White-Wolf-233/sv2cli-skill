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

```sh
sv2cli render song.svp --track '#1' -o lead.wav --warmup 30 --attempts 1 --timeout 1800
sv2cli render song.svp --stems -o stems --bit-depth 24
```

原生宿主按整数采样时钟单次渲染，禁止重渲染收敛或自动回退旧宿主。有声文件不等于验收通过；检查所有音符活动、谱面活动区间的异常静音、实际起音和格式。插件回读核对谱面及显式表达/音高曲线/效果参数，仍不证明目标听感。需要真实试听的需求应制作短 A/B，区分可程序化检查与听审。
