# sv2cli-production skill

用于 Synthesizer V Studio 2 工程编辑、实际发声时序诊断、合唱力度与分轨交付的 Agent Skill。配套工具：[sv2cli](https://github.com/White-Wolf-233/sv2cli)，要求 **0.2.0+**。

skill 组织工作流，实际编辑、保存、渲染和音频计算由 CLI 完成。包括原位覆盖与备份、音乐坐标、重复组引用定位、入声诊断、显式音频移位及失败续跑。不会将指纹或“文件有声音”当成已经唱齐，也不声称实现自动参考录音强制对齐。

## 安装

先按 [CLI 文档](https://github.com/White-Wolf-233/sv2cli#readme) 安装工具；时序分析需要 audio extra，原生合成需要 render extra 及已激活声库。

```sh
git clone https://github.com/White-Wolf-233/sv2cli.git
cd sv2cli
python -m pip install ".[render,midi,audio]"
```

建议使用私有虚拟环境，不修改全局 PATH 或已有 Python。在 Codex 中用 skill-installer 安装本仓库 `skills/sv2cli-production`；也可将该目录复制到自己的 skill 目录（默认 `~/.codex/skills/sv2cli-production`）。已有同名 skill 时先检查自定义内容。

## 使用

> 用 $sv2cli-production 处理这个 SVP。旋律歌词不变，低声部更厚一点；允许直接覆盖，先检查实际起收音，再导出分轨。

> 用 $sv2cli-production 检查第二轨第 53–60 小节为什么没唱齐。工程时值与实际发声分开检查，给出同时间轴前后对照。

明确授权覆盖后不会反复询问。CLI 自动备份原位保存的 SVP；音频移位使用独立输出，并检查裁切与发声窗口退化。skill 默认可自动触发。

涉及参考录音、PDF 乐谱、ASR、主观听审时，使用当前环境的相应能力并报告证据范围。本仓库不附歌曲、声库、音频或私人路径。

## 验证

```sh
python tests/smoke.py
```

该 smoke 实际执行示例 recipe、保谱原位保存、音乐坐标和测试信号时序校正；不是模型触发质量评测，也不是歌声听审。许可插件验证与本仓库测试分开。

MIT License。
