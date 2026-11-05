# 设计系统参考

SKILL.md 的展开版。需要精确数值或组件模板时查这里。

## 完整色板（9 色系 × 7 档）

档位含义：50 = 最浅填充，100–200 = 浅填充，400 = 中间色，600 = 强调 / 描边，800–900 = 浅底上的文字。

| 色系 | 50 | 100 | 200 | 400 | 600 | 800 | 900 |
|---|---|---|---|---|---|---|---|
| purple | `#EEEDFE` | `#CECBF6` | `#AFA9EC` | `#7F77DD` | `#534AB7` | `#3C3489` | `#26215C` |
| teal | `#E1F5EE` | `#9FE1CB` | `#5DCAA5` | `#1D9E75` | `#0F6E56` | `#085041` | `#04342C` |
| coral | `#FAECE7` | `#F5C4B3` | `#F0997B` | `#D85A30` | `#993C1D` | `#712B13` | `#4A1B0C` |
| pink | `#FBEAF0` | `#F4C0D1` | `#ED93B1` | `#D4537E` | `#993556` | `#72243E` | `#4B1528` |
| gray | `#F1EFE8` | `#D3D1C7` | `#B4B2A9` | `#888780` | `#5F5E5A` | `#444441` | `#2C2C2A` |
| blue | `#E6F1FB` | `#B5D4F4` | `#85B7EB` | `#378ADD` | `#185FA5` | `#0C447C` | `#042C53` |
| green | `#EAF3DE` | `#C0DD97` | `#97C459` | `#639922` | `#3B6D11` | `#27500A` | `#173404` |
| amber | `#FAEEDA` | `#FAC775` | `#EF9F27` | `#BA7517` | `#854F0B` | `#633806` | `#412402` |
| red | `#FCEBEB` | `#F7C1C1` | `#F09595` | `#E24B4A` | `#A32D2D` | `#791F1F` | `#501313` |

### 主题速查

- **浅色**：50 填充 + 600 描边 + 800 标题 / 600 副标题
- **深色**：800 填充 + 200 描边 + 100 标题 / 200 副标题

### 语义映射建议

| 含义 | 色系 |
|---|---|
| 中性 / 结构 / 背景元素 | gray |
| 正常路径 / 输入 | blue |
| 成功 / 健康 / 已完成 | green 或 teal |
| 警告 / 待观察 / 成本 | amber |
| 错误 / 风险 / 阻塞 | red |
| 抽象概念 / 强调分支 | purple 或 coral |

## 字号标定表

用于估算文字宽度，避免文字溢出框：

| 文本类型 | 字符数 | 字重 | 字号 | 实际渲染宽度 |
|---|---|---|---|---|
| 标题 | 12 | 500 | 14px | ~88px |
| 副标题 | 16 | 400 | 13px | ~104px |
| 正文 | 24 | 400 | 13px | ~156px |
| 注释 | 20 | 400 | 12px | ~120px |

中文按每字 ≈ 字号宽度算，英文按每字符 ≈ 字号 × 0.55 算。混排取两者较大值。

**框宽公式**：`rect_width = max(标题字数 × 7, 副标题字数 × 6) + 24`

## 箭头 marker

每张用箭头的图都要带上，放在 `<defs>` 最前：

```svg
<defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5"
    markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke"
      stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </marker>
</defs>
```

`stroke="context-stroke"` 让箭头自动跟随连线颜色，不用另写一套 marker。

## 节点模板

单行（44px）：

```svg
<g>
  <rect x="100" y="20" width="180" height="44" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
  <text x="190" y="42" text-anchor="middle" dominant-baseline="central"
        font-size="14" font-weight="500" fill="#0C447C">T-cells</text>
</g>
```

双行（56px）：

```svg
<g>
  <rect x="100" y="20" width="180" height="56" rx="8" fill="#E6F1FB" stroke="#185FA5" stroke-width="0.5"/>
  <text x="190" y="40" text-anchor="middle" dominant-baseline="central"
        font-size="14" font-weight="500" fill="#0C447C">线粒体</text>
  <text x="190" y="60" text-anchor="middle" dominant-baseline="central"
        font-size="12" font-weight="400" fill="#185FA5">Mitochondrion</text>
</g>
```

## 柱状图配置

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 680 264" width="680" height="264" role="img">
  <title>…</title>
  <desc>…</desc>
  <text x="340" y="36" text-anchor="middle" font-size="15" font-weight="500" fill="#27500A">标题</text>
  <rect x="60" y="100" width="64" height="120" rx="4" fill="#97C459" stroke="#3B6D11" stroke-width="0.5"/>
  <text x="92" y="92" text-anchor="middle" font-size="12" font-weight="400" fill="#27500A">12</text>
  <text x="92" y="244" text-anchor="middle" font-size="12" font-weight="400" fill="#4C4C48">周一</text>
</svg>
```

要点：
- 柱子用 400 档填充 + 600 档描边，rx 4
- 数值标签在柱顶上方 8px，类目标签在基线下 24px
- 每根柱子 ≤ 5 根，多了拆图或改折线

## 折线图配置

```svg
<polyline points="60,180 190,120 320,150 450,90 580,60"
  fill="none" stroke="#185FA5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="60" cy="180" r="4" fill="#185FA5"/>
<circle cx="190" cy="120" r="4" fill="#185FA5"/>
```

要点：
- 折线 `fill="none"`，2px，圆角端点
- 关键拐点画 4px 圆点
- 多条线用不同色系，每条 ≤ 3 个系列

## 常见错误

| 错误 | 后果 | 修法 |
|---|---|---|
| 忘记 `dominant-baseline="central"` | 文字在框里偏上 | 每个框内 `<text>` 都加 |
| 连接线没写 `fill="none"` | 出现黑色三角填充 | 所有 path / polyline 都加 |
| 节点太多挤在一张图 | 缩到 11px 以下不可读 | 拆成两张图 |
| 用 600/700 字重 | 中文渲染过粗、发虚 | 只用 400/500 |
| 文字宽度没估准 | 溢出框边界 | 用框宽公式算 |
| 圆形循环图 | 读者不知道从哪开始 | 改 stepper 或线性 + 回环 |
| 内联 `.html` | 宿主当纯文本输出 | 写 `.svg` 文件内联 |
| 只写 `viewBox` + `width="100%"` | `<img>` 解码成空白盒 | 根节点带显式像素 `width`/`height` |
| 图落在 `$DSH_HOME` 或 `/tmp` | `api/file` 拒绝非工作区路径 | 落盘到工作区 `.dsh-tmp/diagrams/` |
| 用 `data:` URI 内嵌 | 作者层 sanitizeUrl 拒绝，只剩 alt 文本 | 落盘成 `.svg` 文件再 `![]()` |
