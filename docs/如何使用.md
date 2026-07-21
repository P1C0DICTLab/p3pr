# P3PR7 使用教程

**版本**：7.0  
**状态**：稳定  
**适用对象**：需要生成 3D 点云可视化 HTML 文件的 Python 开发者  

---

## 1. 简介

`p3pr7` 是一个轻量级的 Python 库，用于构建 3D 点云场景并导出为**独立的 HTML 文件**，无需任何外部服务器或依赖。它基于全新的 **3PR 查看器渲染引擎（v7）**，核心改进如下：

- **纯嵌入数据驱动**：查看器完全从 `window.__EMBEDDED_DATA__` 读取配置和点数据，不发起任何网络请求（不再加载 `data.json`），适合离线或内嵌分发。
- **健壮的降级显示**：即便数据注入失败（如占位符未替换），查看器仍能绘制空场景（背景 + 坐标轴），而非直接黑屏，便于调试。
- **更紧凑的输出**：数据通过 JSON 字符串一次性注入 HTML，无需额外文件。
- 支持所有前序功能：丰富的点样式、元数据悬停展示、交互控制（旋转/缩放/平移/键盘）、场景配置（标题、背景、相机、坐标轴、图例）。

**设计理念**：延续 `plotly` 风格，通过简单的 Python 接口快速生成可视化结果，同时为高级用户提供自定义模板的灵活性。

---

## 2. 安装

`p3pr7` 是一个单文件库，无需额外依赖（仅使用 Python 标准库 `json`, `numbers`, `webbrowser`, `tempfile`, `os`）。

### 获取文件

将 `p3pr7.py` 放置到您的项目目录中，或通过 `import p3pr7` 使用。

**注意**：`p3pr7.py` 已内嵌完整的查看器 HTML 代码，开箱即用。HTML 模板中包含占位符 `__DATA_PLACEHOLDER__`，导出时会被替换为实际数据。

---

## 3. 快速开始

### 3.1 最简示例

```python
import p3pr7

# 1. 创建场景
scene = p3pr7.Scene(title="我的第一个点云")

# 2. 添加一些点
scene.add_point([0, 0, 0], color="#ffffff", size=8, meta={"id": "原点"})
scene.add_point([3, 2, 1], color="#ff8800", size=10, meta={"类别": "A"})
scene.add_point([-2, 4, -1], color="#00ccff", size=6, shape="square", meta={"类别": "B"})

# 3. 生成并打开 HTML
scene.show()   # 自动在浏览器中打开临时文件
```

### 3.2 批量添加点

```python
points_data = [
    {"pos": [5, 0, 0], "color": "#ff8800", "size": 7, "meta": {"类别": "A"}},
    {"pos": [0, 5, 0], "color": "#00ccff", "size": 9, "meta": {"类别": "B"}},
    {"pos": [0, 0, 5], "color": "#ff33cc", "size": 8, "meta": {"类别": "C"}},
]
scene.add_points(points_data)
```

---

## 4. 核心 API 详解

### 4.1 类 `Scene`

构造方法：

```python
Scene(
    title: Optional[str] = None,
    background: Optional[str] = None,
    camera: Optional[Dict[str, Any]] = None,
    axis: Optional[Dict[str, Any]] = None,
    legend: Optional[List[Dict[str, str]]] = None
)
```

- `title`：显示在页面顶部的标题。
- `background`：CSS 颜色字符串，如 `'#1a1a2e'`。
- `camera`：字典，包含 `distance`, `theta`, `phi`, `target`（均为数值）。
- `axis`：坐标轴配置，含 `enabled`, `x`, `y`, `z` 子字典（含 `label`, `color`），`leftHanded`, `length`。
- `legend`：图例列表，每项为 `{'label': str, 'color': str}`。

### 4.2 配置方法

#### `set_title(title: str)`
设置页面标题。

#### `set_background(color: str)`
设置背景色（支持十六进制 `#rrggbb` 或 `#rgb`）。

#### `set_camera(distance, theta, phi, target)`
设置相机初始状态：
- `distance`：观察距离。
- `theta`：水平角度（弧度）。
- `phi`：垂直角度（弧度，范围 -π/2 ~ π/2）。
- `target`：观察焦点坐标 `[x, y, z]`。

#### `set_axis(enabled, x_label, y_label, z_label, x_color, y_color, z_color, left_handed, length)`
配置坐标轴：
- `enabled`：是否显示坐标轴（默认 `True`）。
- 各轴标签和颜色。
- `left_handed`：是否为左手坐标系（默认 `False`，即右手系）。
- `length`：轴线长度（默认 500）。

#### `add_legend(label, color)`
添加一个图例项（可多次调用）。

#### `set_legend(legend_list)`
直接设置整个图例列表（覆盖之前的内容）。

#### `update_layout(**kwargs)`
灵活更新配置，支持 `title`, `background`, `camera`, `axis`, `legend`。对于 `camera` 和 `axis`，会进行字典合并，而非完全覆盖。

示例：
```python
scene.update_layout(
    title="新标题",
    background="#222244",
    camera={"distance": 40, "theta": 0.8},
    axis={"enabled": False}   # 关闭坐标轴
)
```

### 4.3 点操作方法

#### `add_point(pos, color=None, size=1.0, shape='circle', meta=None)`
添加单个点：
- `pos`：`[x, y, z]` 坐标。
- `color`：颜色，支持十六进制字符串 `'#ff8800'` 或 RGB 元组 `(1.0, 0.5, 0.0)` 或 `(255, 128, 0)`。默认白色。
- `size`：像素大小。
- `shape`：可选 `'circle'`, `'square'`, `'triangle'`, `'diamond'`, `'star'`, `'cross'`。
- `meta`：字典，用于存储附加信息（悬停时显示）。

#### `add_points(points_data)`
批量添加点，支持两种格式：
1. **字典列表**：每项包含 `pos`, `color`, `size`, `shape`, `meta`（后四项可选）。
2. **元组/列表列表**：每项为 `(pos, color, size, shape, meta)`，其中 `pos` 必填，其余可选。

### 4.4 导出方法

#### `to_dict() -> Dict`
返回符合查看器规范的完整数据结构（包含 `config` 和 `testPoints`）。

#### `to_json(compact=True, **kwargs) -> str`
输出 JSON 字符串。`compact=True` 时无多余空格。

#### `save_json(filename, compact=True, **kwargs)`
保存 JSON 到文件。

#### `write_html(filename, open_browser=False)`
生成独立的 HTML 文件。内部会将 `to_json()` 的结果替换模板中的 `__DATA_PLACEHOLDER__`，生成一个完全自包含的页面。

#### `show()`
生成临时 HTML 文件并在默认浏览器中打开（类似 `plotly.show()`）。

---

## 5. 颜色格式详解

所有颜色参数统一支持以下格式，内部会转换为紧凑的 `#rrggbb` 字符串：

| 格式 | 示例 | 说明 |
|------|------|------|
| 十六进制短码 | `'#f80'` | 自动扩展为 `#ff8800` |
| 十六进制长码 | `'#ff8800'` | 原样保留 |
| 0~1 RGB 元组 | `(1.0, 0.5, 0.0)` | 映射到 0~255 |
| 0~255 RGB 元组 | `(255, 128, 0)` | 直接使用 |
| 列表 | `[1.0, 0.5, 0.0]` 或 `[255, 128, 0]` | 同上 |

---

## 6. 完整示例

```python
import p3pr7
import random

# 创建场景
scene = p3pr7.Scene(
    title="3D 点云示例",
    background="#0a0a1a",
    camera={"distance": 30, "theta": 0.2, "phi": 0.6, "target": [0, 0, 0]},
    axis={
        "enabled": True,
        "x": {"label": "X", "color": "#ff6666"},
        "y": {"label": "Y", "color": "#66ff66"},
        "z": {"label": "Z", "color": "#6666ff"},
        "length": 400
    }
)

# 添加图例
scene.add_legend("类别 A", "#ff8800")
scene.add_legend("类别 B", "#00ccff")
scene.add_legend("类别 C", "#ff33cc")

# 生成随机点云
for i in range(100):
    x = random.uniform(-10, 10)
    y = random.uniform(-10, 10)
    z = random.uniform(-10, 10)
    category = random.choice(["A", "B", "C"])
    color = {"A": "#ff8800", "B": "#00ccff", "C": "#ff33cc"}[category]
    scene.add_point(
        pos=[x, y, z],
        color=color,
        size=random.uniform(4, 12),
        shape=random.choice(["circle", "square", "triangle"]),
        meta={"类别": category, "值": round(random.random(), 2)}
    )

# 生成并打开
scene.write_html("output.html", open_browser=True)
```

---

## 7. 高级技巧

### 7.1 自定义点元数据
您可以在 `meta` 中存放任意键值对，悬停时自动展示：
```python
scene.add_point([1,2,3], meta={"名称": "测量点", "温度": 23.5, "状态": "正常"})
```

### 7.2 动态更新场景
在导出前可多次调用配置方法：
```python
scene.set_camera(distance=50)
scene.set_axis(enabled=False)   # 临时隐藏坐标轴
scene.update_layout(background="#112233")
```

### 7.3 仅导出 JSON（非 HTML）
如果您想使用其他前端框架，可以仅导出 JSON：
```python
json_str = scene.to_json()
# 或保存为文件
scene.save_json("data.json")
```

### 7.4 自定义 HTML 模板
默认模板已内嵌在 `Scene._HTML_TEMPLATE` 中。若需替换（例如更换样式或调试），您可以：
1. 修改源代码中的 `_HTML_TEMPLATE` 类变量。
2. 或者在调用 `write_html` 前，将新模板字符串赋值给 `Scene._HTML_TEMPLATE`。

**注意**：自定义模板中**必须**包含占位符 `__DATA_PLACEHOLDER__`，否则数据无法注入。

---

## 8. 常见问题 (FAQ)

**Q：为什么我运行 `scene.show()` 后页面没有显示点？**  
A：请检查点数据是否添加成功，以及 `p3pr7.py` 源文件中 `_HTML_TEMPLATE` 是否包含 `__DATA_PLACEHOLDER__` 占位符。若模板被错误修改，将导致注入失败。

**Q：直接打开生成的 HTML 时，控制台报错 `__DATA_PLACEHOLDER__ is not defined`，但页面显示了背景和坐标轴，这是正常的吗？**  
A：这是正常的。新版查看器采用“先渲染，后注入”的机制，即使数据占位符未被替换（例如您手动打开未替换的模板），查看器仍会绘制空场景（背景 + 坐标轴）并保持交互功能。此设计便于调试和模板开发。但在实际使用中，`p3pr7` 库会正确替换占位符，因此不会出现该报错。

**Q：如何关闭坐标轴？**  
A：使用 `scene.set_axis(enabled=False)` 或 `scene.update_layout(axis={"enabled": False})`。

**Q：颜色字符串 `#f80` 支持吗？**  
A：支持，内部会自动扩展为 `#ff8800`。

**Q：能否在浏览器中旋转/缩放？**  
A：可以，查看器支持鼠标左键旋转、滚轮缩放、右键平移，以及 WASDQE 键盘控制焦点。

**Q：点的大小是否随距离变化？**  
A：查看器会自动根据深度调整点的屏幕大小，以模拟透视效果。

**Q：如何调整相机初始位置？**  
A：通过 `set_camera(distance, theta, phi)` 设置，或直接在 `Scene` 构造时传入 `camera` 字典。

**Q：旧版生成的 HTML 还能用新版查看器吗？**  
A：不能。新版查看器仅接受 `{ config, testPoints }` 格式，且数据必须通过 `__DATA_PLACEHOLDER__` 注入。建议使用 `p3pr7` 重新生成。

---

## 9. 与旧版（p3pr5,p3pr6）的区别

- **查看器内核升级**：新版查看器完全依赖嵌入数据，不再发起任何外部请求，更适合离线环境。
- **健壮性提升**：即使数据注入失败，页面仍能显示空场景（含坐标轴），方便调试。
- **模板占位符标准化**：统一使用 `__DATA_PLACEHOLDER__`，生成工具只需替换该字符串即可。
- **API 完全兼容**：所有 Python API（`Scene` 类及方法）保持不变，升级只需替换库文件。
- **输出更紧凑**：移除了多余的 `metadata` 兼容逻辑，数据格式更纯净。

---

## 10. 技术细节：数据注入原理

生成 HTML 时，`write_html()` 会执行以下步骤：
1. 调用 `to_json(compact=True)` 将场景数据序列化为紧凑 JSON 字符串。
2. 读取 `Scene._HTML_TEMPLATE`（默认内置完整 HTML）。
3. 将模板中的 `__DATA_PLACEHOLDER__` 替换为上述 JSON 字符串。
4. 写入目标文件。

查看器启动时，会执行以下操作：
```javascript
window.__EMBEDDED_DATA__ = __DATA_PLACEHOLDER__;
```
若占位符被正确替换，`window.__EMBEDDED_DATA__` 将包含完整数据对象；若未替换（如直接打开模板文件），则会抛出 `ReferenceError`，但查看器核心渲染循环早已启动，会基于默认值绘制空场景。

这一设计使得模板开发更加灵活，同时也保证了最终用户生成的 HTML 页面完全自包含、无外部依赖。