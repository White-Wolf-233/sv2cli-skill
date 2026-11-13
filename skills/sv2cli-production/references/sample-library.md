# 素材库

制作中可直接载入试用的示例文件在 `assets/` 目录：

| 文件 | 用途 |
|------|------|
| `choral-mix.recipe.json` | 合唱混音 recipe 示例 |
| `motif-log-template.json` | 动机记录模板 |
| `phrase-registry-template.json` | 歌词计划主文件模板 |

## 使用方式

**动机记录**

```sh
cp assets/motif-log-template.json motif-log.json
# 编辑 motif-log.json，填入动机信息后运行动机搜索
sv2cli full-score-text song.svp -o score.json
python scripts/motif_distance.py score.json --interval "2 2 -2"
```

**歌词计划分句合并**

```sh
cp assets/phrase-registry-template.json master-plan.json
# 逐句生成片段后合并
python scripts/phrase_merge.py master-plan.json verse1_line1.json verse1_line2.json
sv2cli lyrics-check song.svp --plan master-plan.json --require-full-project -o audit.json
```

**合唱 recipe**

```sh
# 查看 schema 确认字段
sv2cli recipe-schema

# 应用示例 recipe（score-lock 防止改谱）
sv2cli edit song.svp --recipe assets/choral-mix.recipe.json --score-lock -o out.svp --dry-run
sv2cli edit song.svp --recipe assets/choral-mix.recipe.json --score-lock -o out.svp
```

## 添加新素材

把常用 recipe、片段模板或批处理 manifest 放到 `assets/` 目录，文件名清楚说明用途。  
私人路径、声库文件和音频成品不入库。
