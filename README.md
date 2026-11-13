# dsh-visualize-first

DeepSeek Harness 技能：回答任何「讲清楚」类问题时先出图。交付是硬性的两步：先用 `write` 把 SVG 落盘到工作区临时目录（`.dsh-tmp/diagrams/`），再用 `![说明](相对路径)` 内联在正文里——**没有 write 的引用必然「图片无法预览」**。

## 这个技能解决什么

DSH 宿主的正文渲染有硬约束（均经源码核实）：

- 围栏代码块（```xml / ```svg / ```mermaid）只走 Shiki 语法高亮，**不渲染成图**；
- 正文裸 `<svg>` 是 literal text（raw HTML 不进 DOM）；
- `data:` URI 在作者层被 `sanitizeUrl` 显式拒绝；
- `![]()` 只解析**会话工作区内**的文件（`api/file` 要求工作区绝对路径）。

所以「写一段 SVG 就想让它显示」的所有歧路都被堵死，唯一出口是落盘 + 内联引用。本技能把这条唯一路径、两个已实证的雷区（① **引用先于落盘**：最终消息带 `![]()` 却没先 `write`，整批图「图片无法预览」——多会话复盘中占比最高的失败形态；② 根节点必须显式像素 `width`/`height`、viewBox 四个真实数字）和完整的画图规范固化下来，模型照做即可稳定出图。

## 安装

```sh
# 装到用户级技能目录（推荐用软链，跟随本仓库更新）
git clone git@github.com:ice-ai-lab/dsh-visualize-first.git
mkdir -p ~/.dsh/skills
ln -s "$(pwd)/dsh-visualize-first" ~/.dsh/skills/dsh-visualize-first

# 或直接拷贝
cp -r dsh-visualize-first ~/.dsh/skills/
```

DSH 对符号链接有显式支持：发现层 `stat` 穿透收录，watch 层 `canonicalizeWatchPath` 锚定真实目录——软链方式下改仓库文件即时热更新。

也可以放进项目级目录 `<projectRoot>/.dsh/skills/`（优先级更高）或用 `customSkillDirs` 配置指向任意目录。

## 文件

```
SKILL.md                      # 技能主文档（frontmatter + 规范全文）
references/design-system.md   # 9 色系 × 7 档色板、字号标定、组件模板
references/self-check.py      # SVG 合规自检脚本（支持 stdin）
_meta.json                    # DSH 技能元数据（版本跟踪）
```

## 自检脚本

```sh
python3 references/self-check.py diagram.svg   # 检查文件
python3 references/self-check.py - < diagram.svg   # 检查 stdin
```

检查 viewBox 数值合法性、显式像素宽高与 viewBox 一致性、字号下限（11px）、字重白名单（400/500）、连接线 `fill="none"`、无障碍属性（`role="img"` + `<title>` + `<desc>`）、违禁效果（渐变/阴影/旋转）与 emoji。

## 版本

- **1.4.0** — 交付方式定为「落盘到工作区 `.dsh-tmp/diagrams/` + `![]()` 内联」；写入宿主渲染链路实测结论（代码块/裸 SVG/data URI/$DSH_HOME 均不可渲染）；新增文件卫生节。
- 1.2–1.3 — 迭代过程中的中间形态（曾试过 fenced code block 内联交付，因宿主不渲染代码块而废弃）。

## License

MIT
