# 响度

## 概念层级

| 层级 | 测量 | 用途 |
|------|------|------|
| 采样峰值 dBFS | 单个采样点最大值 | 防削波，交付上限 |
| 真峰值 dBTP | 过采样后波形峰值 | 更接近实际模拟峰值 |
| 整合响度 LUFS | BS.1770-4 K 计权后分块均值 | 主观响度参考 |
| 短期响度 | 3 s 窗口 LUFS | 段落动态对比 |
| 瞬时响度 | 400 ms 窗口 LUFS | 实时波动观察 |

声库参数里的 `loudness` 是演唱力度参数，与音频工程响度是两套体系，不要混用。

## 命令

```sh
# 只查采样峰值、RMS、削波（快）
sv2cli audio-check mix.wav

# 加入 LUFS 和近似真峰值（较慢）
sv2cli audio-check mix.wav --lufs

# 独立的响度报告，含逐秒短期 LUFS
sv2cli loudness-check mix.wav -o loudness.json
```

`loudness-check` 输出 `integratedLUFS`、`truePeakDBFS` 和 `shortTermBins`（每秒一个 LUFS 值）。

真峰值采用 4 倍、129 抽头窗函数 sinc FIR 重建估算，能检测采样点之间的峰值。

## 按段落对比

用 `shortTermBins` 检查段落间响度差：

```python
import json
d = json.load(open('loudness.json'))
bins = d['shortTermBins']
# 副歌通常比主歌响 1–3 LUFS
for b in bins:
    print(f"{b['second']:4d}s  {b['lufs']:+.1f} LUFS")
```

主歌到副歌的响度爬升是常见制作手法；副歌间响度应接近（±1 LUFS 内），否则听感不统一。

## 交付目标参考

| 平台 | 整合响度目标 | 真峰值上限 |
|------|-------------|-----------|
| 流媒体（-14 LUFS 规范）| -14 LUFS | -1 dBTP |
| CD | -9 ~ -7 LUFS | -0.1 dBTP |
| 人声干声交付 | -18 LUFS | -1 dBTP |

`audio-normalize` 只按采样峰值调增益，不改变 LUFS 目标；逐轨归一化会改变声部平衡，仅在需要时使用。

## 合唱声部电平

多声部渲染后，主旋律应在混音中清晰可辨，伴奏低声部通常低 3–6 dB。用各分轨的 `audio-check` 单独查峰值和 LUFS，比对主唱和伴唱的整合响度差值。
