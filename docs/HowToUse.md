# P3PR7 User Guide
**Version**: 7.0
**Status**: Stable
**Target Users**: Python developers who need to generate HTML files for 3D point cloud visualization

## 1. Introduction
`p3pr7` is a lightweight Python library for constructing 3D point cloud scenes and exporting them as **standalone HTML files** with no external servers or dependencies required. It is built on the brand-new **3PR Viewer Rendering Engine (v7)**. Key improvements are as follows:
- **Fully Embedded Data-Driven**: The viewer reads all configurations and point data entirely from `window.__EMBEDDED_DATA__` and sends no network requests (no more loading of `data.json`), making it ideal for offline use or embedded distribution.
- **Robust Degraded Rendering**: If data injection fails (e.g., placeholder not replaced), the viewer still renders an empty scene (background + coordinate axes) instead of a blank black screen, simplifying debugging.
- **More Compact Output**: All data is injected into HTML in one JSON string, eliminating extra auxiliary files.
- Full backward compatibility with legacy features: rich point styles, hover metadata display, interactive controls (rotate/zoom/pan/keyboard shortcuts), and scene configuration (title, background, camera, axes, legend).

**Design Philosophy**: It follows the style of Plotly, enabling quick visualization results via simple Python interfaces, while offering advanced users flexibility for custom templates.

## 2. Installation
`p3pr7` is a single-file library with zero extra dependencies—only Python standard libraries are used: `json`, `numbers`, `webbrowser`, `tempfile`, `os`.

### File Acquisition
Place `p3pr7.py` into your project directory, then import it with `import p3pr7`.

**Note**: The `p3pr7.py` file embeds the complete viewer HTML code out of the box. The HTML template contains a placeholder `__DATA_PLACEHOLDER__`, which will be replaced with actual data during export.

## 3. Quick Start
### 3.1 Minimal Example
```python
import p3pr7
# 1. Create a scene
scene = p3pr7.Scene(title="My First Point Cloud")
# 2. Add individual points
scene.add_point([0, 0, 0], color="#ffffff", size=8, meta={"id": "Origin"})
scene.add_point([3, 2, 1], color="#ff8800", size=10, meta={"Category": "A"})
scene.add_point([-2, 4, -1], color="#00ccff", size=6, shape="square", meta={"Category": "B"})
# 3. Generate and open HTML
scene.show()   # Automatically opens a temporary file in the default browser
```

### 3.2 Batch Add Points
```python
points_data = [
    {"pos": [5, 0, 0], "color": "#ff8800", "size": 7, "meta": {"Category": "A"}},
    {"pos": [0, 5, 0], "color": "#00ccff", "size": 9, "meta": {"Category": "B"}},
    {"pos": [0, 0, 5], "color": "#ff33cc", "size": 8, "meta": {"Category": "C"}},
]
scene.add_points(points_data)
```

## 4. Core API Reference
### 4.1 Class `Scene`
Constructor signature:
```python
Scene(
    title: Optional[str] = None,
    background: Optional[str] = None,
    camera: Optional[Dict[str, Any]] = None,
    axis: Optional[Dict[str, Any]] = None,
    legend: Optional[List[Dict[str, str]]] = None
)
```
- `title`: Header text displayed at the top of the page
- `background`: CSS color string, e.g., `'#1a1a2e'`
- `camera`: Dictionary containing `distance`, `theta`, `phi`, `target` (all numeric values)
- `axis`: Axis configuration dictionary, including sub-dicts `x`, `y`, `z` (each with `label`, `color`), plus `enabled`, `leftHanded`, `length`
- `legend`: Legend entry list; each entry follows the format `{'label': str, 'color': str}`

### 4.2 Layout Configuration Methods
#### `set_title(title: str)`
Set the page header title.

#### `set_background(color: str)`
Set background color (supports hex formats `#rrggbb` or `#rgb`).

#### `set_camera(distance, theta, phi, target)`
Configure initial camera state:
- `distance`: Viewing distance from the target
- `theta`: Horizontal rotation angle (radians)
- `phi`: Vertical rotation angle (radians, range: -π/2 ~ π/2)
- `target`: Focus point coordinate `[x, y, z]`

#### `set_axis(enabled, x_label, y_label, z_label, x_color, y_color, z_color, left_handed, length)`
Configure coordinate axes:
- `enabled`: Toggle axis visibility (default: `True`)
- Axis labels and corresponding colors for X/Y/Z
- `left_handed`: Enable left-handed coordinate system (default: `False`, right-handed)
- `length`: Length of axis lines (default: 500)

#### `add_legend(label, color)`
Append a single legend entry (can be called multiple times).

#### `set_legend(legend_list)`
Overwrite the full legend list with provided entries.

#### `update_layout(**kwargs)`
Flexibly update scene configurations. Supports `title`, `background`, `camera`, `legend`, `axis`. For `camera` and `axis`, new dictionaries are merged with existing settings instead of full replacement.

Example:
```python
scene.update_layout(
    title="New Title",
    background="#222244",
    camera={"distance": 40, "theta": 0.8},
    axis={"enabled": False}   # Hide coordinate axes
)
```

### 4.3 Point Manipulation Methods
#### `add_point(pos, color=None, size=1.0, shape='circle', meta=None)`
Add a single point:
- `pos`: Coordinate `[x, y, z]`
- `color`: Point color; accepts hex strings `'#ff8800'`, RGB tuples `(1.0, 0.5, 0.0)` or `(255, 128, 0)`. Defaults to white.
- `size`: Pixel size of the point
- `shape`: Available options: `'circle'`, `'square'`, `'triangle'`, `'diamond'`, `'star'`, `'cross'`
- `meta`: Dictionary storing custom metadata, displayed on mouse hover

#### `add_points(points_data)`
Batch add multiple points; supports two input formats:
1. List of dictionaries: Each entry contains `pos`, with optional `color`, `size`, `shape`, `meta`
2. List of tuples/lists: Each entry follows `(pos, color, size, shape, meta)`; only `pos` is mandatory

### 4.4 Export Methods
#### `to_dict() -> Dict`
Return a complete structured dataset compliant with viewer specifications (contains `config` and `testPoints` fields).

#### `to_json(compact=True, **kwargs) -> str`
Output JSON string. `compact=True` removes redundant whitespace for minimized output.

#### `save_json(filename, compact=True, **kwargs)`
Write JSON data to a local file.

#### `write_html(filename, open_browser=False)`
Generate a fully self-contained HTML file. Internally, it replaces the `__DATA_PLACEHOLDER__` marker in the template with the output of `to_json()`.

#### `show()`
Generate a temporary HTML file and open it in the default browser (consistent with Plotly’s `show()` behavior).

## 5. Color Format Specification
All color parameters accept the following formats, which are internally converted to compact `#rrggbb` hex strings:

| Format | Example | Description |
|--------|---------|-------------|
| Short hex | `'#f80'` | Automatically expanded to `#ff8800` |
| Full hex | `'#ff8800'` | Used as-is |
| 0~1 RGB tuple | `(1.0, 0.5, 0.0)` | Scaled to 0–255 range |
| 0~255 RGB tuple | `(255, 128, 0)` | Directly applied |
| List format | `[1.0, 0.5, 0.0]` or `[255, 128, 0]` | Identical behavior to tuples |

## 6. Full Working Example
```python
import p3pr7
import random
# Initialize scene
scene = p3pr7.Scene(
    title="3D Point Cloud Demo",
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
# Add legend entries
scene.add_legend("Category A", "#ff8800")
scene.add_legend("Category B", "#00ccff")
scene.add_legend("Category C", "#ff33cc")
# Generate random point cloud
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
        meta={"Category": category, "Value": round(random.random(), 2)}
    )
# Export HTML and auto-open
scene.write_html("output.html", open_browser=True)
```

## 7. Advanced Tips
### 7.1 Custom Point Metadata
Store arbitrary key-value pairs in `meta`; they will be displayed automatically when hovering over points:
```python
scene.add_point([1,2,3], meta={"Name": "Measurement Point", "Temperature": 23.5, "Status": "Normal"})
```

### 7.2 Dynamic Scene Adjustment
Repeatedly call configuration methods before export to modify scene settings:
```python
scene.set_camera(distance=50)
scene.set_axis(enabled=False)   # Temporarily hide axes
scene.update_layout(background="#112233")
```

### 7.3 Export Raw JSON Only (Skip HTML)
If integrating with custom frontend frameworks, export pure JSON data:
```python
json_str = scene.to_json()
# Or save JSON to disk
scene.save_json("data.json")
```

### 7.4 Custom HTML Templates
The default template is embedded as the class variable `Scene._HTML_TEMPLATE`. To customize styles or debug templates:
1. Modify the `_HTML_TEMPLATE` variable directly in the source code
2. Or overwrite the template string before calling `write_html()` by assigning a new value to `Scene._HTML_TEMPLATE`

**Important Note**: Custom templates **must retain the placeholder `__DATA_PLACEHOLDER__`**, otherwise data injection will fail.

## 8. Frequently Asked Questions (FAQ)
**Q: No points render on the page after calling `scene.show()`?**
A: Verify two points: 1) Points were successfully added to the scene; 2) The `_HTML_TEMPLATE` inside `p3pr7.py` contains the `__DATA_PLACEHOLDER__` marker. If the template is corrupted, data injection breaks.

**Q: The browser console throws `__DATA_PLACEHOLDER__ is not defined` when opening the HTML file directly, but background and axes still render. Is this expected?**
A: Yes, this is normal behavior. The new viewer adopts a "render-first, inject-later" pipeline. Even if the placeholder is not replaced (e.g., opening the raw template file manually), the viewer initializes the empty scene with axes and retains full interactivity to simplify template debugging. In standard usage via the p3pr7 library, the placeholder is correctly substituted, so this error will not appear.

**Q: How to hide coordinate axes?**
A: Call `scene.set_axis(enabled=False)` or `scene.update_layout(axis={"enabled": False})`.

**Q: Does the library support short hex color codes like `#f80`?**
A: Yes; short hex values are automatically expanded to full `#rrggbb` format internally.

**Q: Can I interact with the viewer in the browser?**
A: Full interaction support: Left mouse drag to rotate, mouse wheel to zoom, right mouse drag to pan, and WASDQE keyboard shortcuts to adjust the camera focus.

**Q: Do point sizes change with depth for perspective rendering?**
A: The viewer dynamically adjusts point screen size based on depth to simulate natural perspective effects.

**Q: How to adjust the initial camera position?**
A: Use `set_camera(distance, theta, phi)` or pass the `camera` dictionary parameter directly in the `Scene` constructor.

**Q: Are HTML files generated by older versions compatible with the new viewer?**
A: No. The new viewer only accepts data formatted as `{ config, testPoints }` injected via `__DATA_PLACEHOLDER__`. Regenerate HTML files using the latest p3pr7 library for compatibility.

## 9. Breaking Changes from Legacy Versions (p3pr5, p3pr6)
- Upgraded viewer core: The new viewer relies entirely on embedded data and sends zero external network requests, making offline deployment far more reliable.
- Improved fault tolerance: Empty scenes with axes render normally even if data injection fails, streamlining debugging workflows.
- Standardized template placeholder: Unified marker `__DATA_PLACEHOLDER__` simplifies custom template tooling.
- Fully backward-compatible Python APIs: All existing `Scene` class methods remain unchanged; upgrading only requires replacing the library file.
- Minimized output size: Deprecated redundant legacy metadata compatibility logic for cleaner, smaller data payloads.

## 10. Technical Deep Dive: Data Injection Mechanism
When `write_html()` executes, it follows these steps:
1. Serialize the full scene dataset into compact JSON via `to_json(compact=True)`
2. Load the built-in HTML template stored in `Scene._HTML_TEMPLATE`
3. Replace all instances of the `__DATA_PLACEHOLDER__` marker in the template with the serialized JSON string
4. Write the modified template to the target HTML file

On page load, the embedded viewer runs this JavaScript snippet:
```javascript
window.__EMBEDDED_DATA__ = __DATA_PLACEHOLDER__;
```
If the placeholder is substituted correctly, `window.__EMBEDDED_DATA__` holds the complete scene dataset. If unmodified (e.g., opening the raw template file), a `ReferenceError` will trigger, but the viewer’s main rendering loop already initializes and draws an empty scene with default axes and background.

This design balances flexible template development with fully self-contained, offline-capable output HTML files that require no external assets.