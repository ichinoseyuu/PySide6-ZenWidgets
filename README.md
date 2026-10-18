# ZenWidgets

## preview

!\[预览](https://cdn.jsdelivr.net/gh/ichinoseyuu/Image/202511141737733.png)

## initialization

Recommend using uv tools to manage projects

```powershell
uv init
uv sync
uv pip install -e .
```

## build

```powershell
uv build
```

## install

```powershell
uv add ./dist/zenui-0.1.0-py3-none-any.whl #or
uv add ./dist/zenui-0.1.0.tar.gz
```

本文档介绍项目的定位、源码结构、运行方式以及扩展和打包时需要了解的约定。组件的详细行为以源码和 Gallery 示例为准。

This document describes the project's purpose, source layout, development workflow, extension points, and packaging notes. For exact widget behavior, refer to the implementation and the Gallery application.

## 1. 项目简介 / Project overview

ZenWidgets 是一个基于 PySide6/Qt Widgets 的 Python 桌面 UI 组件库，提供自绘控件、容器与布局、主题和颜色数据、动画辅助，以及无边框窗口相关实现。仓库同时包含 Gallery 演示程序和若干设计资料。

ZenWidgets is a Python desktop UI component library built on PySide6/Qt Widgets. It provides custom-painted controls, containers and layouts, theme and color data, animation helpers, and frameless-window implementations. The repository also includes a Gallery application and design materials.

| 项目 / Item | 当前值 / Current value |
| --- | --- |
| Python | `>=3.12` |
| Qt binding | PySide6 (`>=6.10.1`) |
| 导入包 / Import package | `ZenWidgets` |
| 项目元数据名 / Distribution metadata name | `pyside6-zenwidgets-master` |
| 平台提示 / Platform note | Windows 定向；主题读取和窗口工具依赖 Windows API。 / Windows-oriented; theme detection and window helpers use Windows APIs. |

依赖声明见仓库根目录的 [`pyproject.toml`](../pyproject.toml)。除 PySide6 外，当前声明的运行依赖还包括 `blurwindow`、`numpy` 和 `pywin32`。目前源码中的主题实现直接导入 Python `winreg`，窗口子包也包含 Win32 工具，因此不要假定该项目可在非 Windows 系统上完整导入或运行。

See the root [`pyproject.toml`](../pyproject.toml) for dependency declarations. In addition to PySide6, the declared runtime dependencies include `blurwindow`, `numpy`, and `pywin32`. The theme implementation imports Python's `winreg` module directly, and the window package contains Win32 helpers; do not assume the project can be fully imported or run on non-Windows systems.

## 2. 安装与运行 / Setup and run

### 在仓库中开发 / Develop in this repository

在仓库根目录执行以下命令，使用锁文件安装依赖并启动 Gallery：

From the repository root, install the locked dependencies and start the Gallery:

```powershell
uv sync
uv run python .\zen_widget_gallery\main.py
```

Gallery 是手动交互式示例，不是自动化测试套件。它展示导航栏、页面容器、组件、主题设置和窗口相关示例。也可以在 IDE 中将 `zen_widget_gallery\main.py` 设为启动目标。

The Gallery is an interactive example, not an automated test suite. It demonstrates navigation, stacked pages, widgets, theme settings, and window-related examples. It can also be launched by configuring `zen_widget_gallery\main.py` as the IDE run target.

### 在其他项目中使用 / Use from another project

从源码进行可编辑安装：

Install an editable copy from source:

```powershell
uv pip install -e .
```

代码从 `ZenWidgets` 包导入。示例：

Import the library from the `ZenWidgets` package. Example:

```python
import sys

from PySide6.QtWidgets import QApplication
from ZenWidgets import ZButton, ZStandardFramelessWindow, ZVBoxLayout

app = QApplication(sys.argv)
window = ZStandardFramelessWindow()
content = window.centerWidget()
layout = ZVBoxLayout(content)
layout.addWidget(ZButton(parent=content, text="Hello, ZenWidgets"))
window.show()
sys.exit(app.exec())
```

运行 GUI 前必须创建 `QApplication`。上述控件和布局通过 `ZenWidgets` 的顶层重导出导入；也可以从 `ZenWidgets.component...` 或 `ZenWidgets.gui...` 的具体子包导入，以便明确依赖来源。顶层模块使用通配符重导出，新增 API 时应同时检查对应子包的 `__init__.py` 是否导出了该符号。

Create a `QApplication` before starting the GUI event loop. The example imports widgets and layouts through the top-level `ZenWidgets` re-exports; importing from a specific `ZenWidgets.component...` or `ZenWidgets.gui...` subpackage makes dependencies explicit. The top-level module uses wildcard re-exports, so when adding an API, check that its package `__init__.py` exports the symbol.

## 3. 源码结构 / Source layout

运行时代码采用 `src` 布局，主要包位于 `src/ZenWidgets/`：

Runtime code uses a `src` layout. The main package is under `src/ZenWidgets/`:

| 路径 / Path | 职责 / Responsibility |
| --- | --- |
| `src/ZenWidgets/__init__.py` | 顶层公共导入入口，重导出组件、核心辅助和 GUI/主题 API。 / Top-level import entry point; re-exports components, core helpers, and GUI/theme APIs. |
| `src/ZenWidgets/component/base/` | 自定义控件基类、控件组以及颜色、尺寸、位置、透明度、动画等控制器。 / Widget foundations, groups, and controllers for color, size, position, opacity, and animation. |
| `src/ZenWidgets/component/input/` | 按钮、开关、滑块、下拉框等输入控件。 / Input controls such as buttons, switches, sliders, and combo boxes. |
| `src/ZenWidgets/component/container/` | 堆叠、分割、滚动及列表视图控件。 / Stacked, split, scroll, and list-view widgets. |
| `src/ZenWidgets/component/layouts/` | `QLayout` 实现（盒式/流式布局）和间隔项；布局不是 widget。 / `QLayout` implementations (box/flow layouts) and spacer items; layouts are not widgets. |
| `src/ZenWidgets/component/developing/` | 开发中的自定义水平/垂直、密集、流式和 masonry 容器。 / Custom horizontal/vertical, dense, flow, and masonry containers under development. |
| `src/ZenWidgets/component/text/` | 标题、文本块、单行编辑、登录编辑和数字编辑控件。 / Headline, text block, line edit, login edit, and number edit controls. |
| `src/ZenWidgets/component/navigations/`、`menu/`、`dialogs/` | 导航栏、菜单和对话框组件。 / Navigation bars, menus, and dialogs. |
| `src/ZenWidgets/component/panel/`、`cards/`、`media/`、`info/` | 面板、卡片、图像和提示信息组件。 / Panels, cards, images, and informational components. |
| `src/ZenWidgets/component/window/` | 标题栏、无边框窗口及 Win32 窗口辅助代码。 / Title bars, frameless windows, and Win32 window helpers. |
| `src/ZenWidgets/component/spareparts/` | 滚动手柄、分隔线等可复用小部件。 / Reusable parts such as scroll handles and separators. |
| `src/ZenWidgets/core/` | 动画、枚举、数据类、转换器、全局对象、调试和通用工具。 / Animations, enums, data classes, converters, globals, debugging, and utilities. |
| `src/ZenWidgets/gui/` | 主题管理、调色板/颜色数据、样式、效果和 Qt 资源。 / Theme management, palettes/color data, styles, effects, and Qt resources. |
| `zen_widget_gallery/` | 交互式控件库演示程序及其页面。 / Interactive component-library demo and its pages. |
| `zen_PortableBox/`、`zen_bieganmao/` | 仓库中的其他演示/应用代码。 / Other demo/application code in the repository. |
| `scripts/` | 颜色数据解析等辅助脚本。 / Helper scripts, including color-data parsing. |
| `docs/design_paper/` | Draw.io 图和设计草稿。 / Draw.io diagrams and design notes. |

### 主要控件 / Representative widgets

下面列出便于定位源码的代表性 API；这不是完整的逐方法 API 参考：

The following representative APIs help locate the source; this is not an exhaustive method-by-method API reference:

* 输入控件 / Inputs: `ZButton`, `ZRepeatButton`, `ZToggleButton`, `ZLongPressButton`, `ZProgressButton`, `ZSlider`, `ZSwitch`, `ZComboBox`
* 容器 / Containers: `ZStackView`, `ZSplitView`, `ZHSplitView`, `ZVSplitView`, `ZScrollView`, `ZListView`, `ZHListView`, `ZVListView`
* 布局 / Layouts (`QLayout`): `ZBoxLayout`, `ZHBoxLayout`, `ZVBoxLayout`, `ZFlowLayout`
* 开发中容器 / Developing containers: `ZHContainer`, `ZVContainer`, `ZHDenseContainer`, `ZVDenseContainer`, `ZFlowContainer`, `ZMasonryContainer`
* 文本与展示 / Text and display: `ZHeadLine`, `ZTextBlock`, `ZLineEdit`, `ZLoginEdit`, `ZNumberEdit`, `ZImage`
* 导航与窗口 / Navigation and windows: `ZNavigationBar`, `ZTitleBar`, `ZFramelessWindow`, `ZStandardFramelessWindow`
* 其他 / Other: `ZPanel`, `ZCard`, `ZDialog`, `ZMenu`, `ZContextMenu`, `ZToolTip`

具体名称及导出范围以各目录的 `__init__.py` 和实现为准。/ Verify exact names and exports in the relevant `__init__.py` files and implementations.

**注意：** `QLayout` 类型应通过 `QWidget.setLayout()` 或父布局的 `addLayout()` 安装，不可传给 `addWidget()`。`ZFlowLayout` 是布局管理器，不提供 `ZFlowContainer` 的容器/拖拽 API。

**Note:** Install a `QLayout` using `QWidget.setLayout()` or a parent layout's `addLayout()`; do not pass it to `addWidget()`. `ZFlowLayout` is a layout manager and does not provide `ZFlowContainer`'s container/drag APIs.

## 4. 主题、样式与资源 / Themes, styles, and resources

`ZenWidgets.gui` 集中放置外观相关能力。`ZTheme` 表示浅色/深色主题，`ZThemeMode` 表示跟随系统或预设模式，`ZThemeManager` 管理主题状态并通过 `themeChanged` 发出变化信号。当前系统主题探测使用 Windows 注册表。控件的颜色数据由 `ZColorData`、`ZPalette` 和相关 provider/manager 提供；样式枚举和数据定义位于 `gui/style.py`。

Appearance-related functionality lives in `ZenWidgets.gui`. `ZTheme` represents light/dark themes, `ZThemeMode` selects system-following or preset mode, and `ZThemeManager` manages theme state and emits `themeChanged`. System-theme detection currently reads the Windows registry. Widget color data is provided through `ZColorData`, `ZPalette`, and related providers/managers; style enums and data definitions are in `gui/style.py`.

全局入口 `ZGlobal` 提供主题管理器、图标包、调色板和样式数据管理器等共享对象。更改主题或样式时，应使用现有管理器和信号机制，并检查相关控件是否订阅了更新，而不是只修改一个控件的绘制颜色。

The `ZGlobal` entry point exposes shared objects such as the theme manager, icon pack, palette, and style-data manager. When changing themes or styles, use the existing managers and signal mechanism, and verify that affected widgets subscribe to updates rather than changing only a single widget's paint color.

Qt 资源位于 `src/ZenWidgets/gui/resource/`，包括图标、资源清单和生成的 `icons_rc.py`。变更资源时需同步维护资源清单及运行时实际使用的资源模块；不要只改生成文件或只改源图标。

Qt resources live in `src/ZenWidgets/gui/resource/` and include icons, a resource manifest, and generated `icons_rc.py`. When changing resources, keep the manifest and the runtime resource module in sync; do not update only the generated file or only the source icons.

## 5. 开发约定 / Development conventions

1. 组件按职责放入对应子包；基类/跨组件机制放在 `component/base/`，通用非 UI 逻辑放在 `core/`，主题和绘制样式放在 `gui/`。<br>
   Place components in the subpackage matching their responsibility; put shared widget mechanisms in `component/base/`, general non-UI logic in `core/`, and theme/painting styles in `gui/`.
2. Qt 控件必须遵循 Qt 的对象父子关系、信号槽和 GUI 线程约束。耗时操作不要阻塞 GUI 事件循环。<br>
   Follow Qt's object ownership, signals/slots, and GUI-thread rules. Do not block the GUI event loop with long-running work.
3. 新增公开控件时，更新其模块导出链（所属目录的 `__init__.py`，必要时 `component/__init__.py` 和顶层入口），并在 Gallery 中补充可运行示例。<br>
   When adding a public widget, update its export chain (the package `__init__.py`, and where appropriate `component/__init__.py` and the top-level entry point), and add a runnable Gallery example.
4. 新增或调整 Windows API 功能时，明确记录平台依赖，并为系统资源/线程提供清理路径。<br>
   When adding or changing Windows API functionality, document the platform dependency and provide cleanup paths for system resources and threads.
5. 更新界面资源时同步维护资源清单和生成资源模块；更新依赖时同步维护 `pyproject.toml` 与锁文件。<br>
   Keep the resource manifest and generated resource module in sync when changing UI assets; update both `pyproject.toml` and the lock file when dependencies change.
6. 修改后至少启动受影响的示例并手动检查交互；若添加自动化测试，应覆盖新增行为及平台限定逻辑。<br>
   After changes, launch the affected example and manually verify interactions. Add automated tests for new behavior and platform-specific logic where practical.

## 6. 构建与验证 / Build and validation

构建发行包的仓库命令：

Build a distribution package with:

```powershell
uv build
```

仓库当前没有独立的自动化测试目录或测试运行配置；不要把成功构建误认为界面行为已验证。提交前应在 Windows/PySide6 环境中运行 Gallery，检查受影响组件，并查看 Git diff 确认无意外资源或生成文件变更。

The repository currently has no separate automated-test directory or test-runner configuration. A successful build does not verify UI behavior. Before submitting changes, run the Gallery in a Windows/PySide6 environment, inspect affected components, and review the Git diff for unintended resource or generated-file changes.

如需生成独立桌面可执行文件，可使用 Nuitka 或 PyInstaller；这属于应用打包步骤，而不是本库的运行时要求。应在目标 Windows 环境中验证 Qt 插件、图标资源和 Win32 依赖是否一并包含。

Nuitka or PyInstaller may be used to produce a standalone desktop executable. This is an application-packaging step, not a runtime requirement of the library. Verify Qt plugins, icon resources, and Win32 dependencies in the target Windows environment.

## 7. 相关资料 / Related documentation

* [架构说明](./Architecture.md)：模块依赖、类协作关系和完整类/方法索引。 / Module dependencies, class relationships, and a complete class/method index.
* [README](../README.md)：仓库简介及基本构建命令。 / Repository introduction and basic build commands.
* [QWidget 笔记](./QWidget.md)：Qt Widgets 相关笔记。 / Notes on Qt Widgets.
* [Qt 笔记](./Qt.md)：Qt 相关笔记。 / Notes on Qt.
* [设计资料](./design_paper/)：组件设计草稿与图示。 / Component design drafts and diagrams.
* [Gallery 源码](../zen_widget_gallery/main.py)：演示应用入口及控件组合示例。 / Demo application entry point and widget-composition example.
* [许可证](../LICENSE)：项目许可证文本。 / Project license.
