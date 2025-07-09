# 手势识别控制系统

这是一个基于计算机视觉的手势识别系统，可以通过手势控制系统功能，支持 **Windows、macOS 和 Linux** 跨平台运行。

## 系统要求

- Python 3.8+
- 摄像头（用于手势识别）
- 支持的操作系统：
  - ✅ Windows 10/11
  - ✅ macOS 10.14+  
  - ✅ Linux (Ubuntu 18.04+, Fedora, Arch 等)

## 跨平台安装

### 1. 克隆项目
```bash
git clone <项目地址>
cd project
```

### 2. 安装依赖

**所有平台通用：**
```bash
pip install -r requirements.txt
```

**或使用 uv（推荐）：**
```bash
uv sync
```

### 3. 平台特定配置

#### Windows
- `pywin32` 会自动安装，提供完整的窗口管理功能
- 支持所有系统功能（音量、窗口控制、媒体键等）

#### macOS
- 某些功能需要授予辅助功能权限
- 音量控制使用 AppleScript
- 窗口管理使用系统快捷键

#### Linux
- 音量控制支持：`alsa-utils`、`pulseaudio-utils` 或 `pulseaudio-ctl`
- 窗口管理（可选）：`wmctrl`

**Ubuntu/Debian 安装额外工具：**
```bash
sudo apt install alsa-utils pulseaudio-utils wmctrl
```

**Fedora/RHEL 安装额外工具：**
```bash
sudo dnf install alsa-utils pulseaudio-utils wmctrl
```

**Arch Linux 安装额外工具：**
```bash
sudo pacman -S alsa-utils pulseaudio wmctrl
```

## 功能支持矩阵

| 功能 | Windows | macOS | Linux |
|------|---------|-------|-------|
| 键盘快捷键 | ✅ | ✅ | ✅ |
| 窗口最大化/最小化 | ✅ | ✅ | ✅* |
| 窗口关闭 | ✅ | ✅ | ✅ |
| 音量控制 | ✅ | ✅ | ✅* |
| 媒体键 | ✅ | ✅ | ✅ |
| 鼠标滚轮 | ✅ | ✅ | ✅ |
| 窗口切换 | ✅ | ✅ | ✅ |

*需要安装额外工具以获得最佳体验

## 启动项目

### 启动 Socket 服务器
```bash
cd project
python app.py
```

### 启动手势识别客户端
```bash
cd dyn_gestures  
python main.py
```

## 故障排除

### Windows
- 如果遇到 `pywin32` 相关错误，请重新安装：
  ```bash
  pip uninstall pywin32
  pip install pywin32
  ```

### macOS
- 首次运行可能需要在"系统偏好设置 > 安全性与隐私 > 辅助功能"中授权
- 如果音量控制失败，检查"系统偏好设置 > 安全性与隐私 > 自动化"权限

### Linux
- 如果音量控制不工作，尝试安装不同的音频工具：
  ```bash
  # 尝试 PulseAudio
  sudo apt install pulseaudio pulseaudio-utils
  
  # 或者 ALSA
  sudo apt install alsa-utils
  ```
- 如果窗口管理功能受限，安装 `wmctrl`：
  ```bash
  sudo apt install wmctrl
  ```

### 通用问题
- **权限错误**：某些功能可能需要管理员权限
- **摄像头访问**：确保系统允许 Python 访问摄像头
- **防火墙**：Socket 通信可能被防火墙阻止

## 开发说明

项目采用跨平台设计：
- 核心功能使用 `pynput` 库实现跨平台兼容
- Windows 特有功能通过 `pywin32` 增强（可选）
- macOS 使用 AppleScript 进行系统集成
- Linux 通过命令行工具和标准快捷键实现

# CVZone 手势检测项目

这是一个基于CVZone和MediaPipe的实时手势检测应用程序，使用模块化架构设计，支持多种静态和动态手势识别。

## 功能特点

- **实时手势检测**: 使用摄像头进行实时手势识别
- **多种手势支持**: 
  - 静态手势: V字手势(胜利手势)、竖大拇指(点赞)、倒竖大拇指
  - 动态手势: 握拳到张开手势
- **双手支持**: 同时检测和识别两只手的手势
- **手势绑定系统**: 支持将手势绑定到快捷键和系统功能
- **图形化界面**: 提供直观的PyQt界面进行配置和监控
- **可配置界面**: 支持显示/隐藏手部关键点、手掌中心等
- **模块化设计**: 易于扩展新的手势检测器

## 项目结构

```
dyn_gestures/
├── app.py                # 应用程序入口
├── main.py               # 命令行版本主程序
├── run_qt.py             # PyQt版本启动脚本
├── config.py             # 配置文件
├── gesture_manager.py    # 手势管理器
├── hand_utils.py         # 手部工具类
├── core/                 # 核心功能模块
│   ├── __init__.py
│   ├── gesture_bindings.py  # 手势绑定配置
│   └── action_executor.py   # 动作执行器
├── ui/                   # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py    # 主窗口
│   ├── widgets/          # UI组件
│   │   ├── __init__.py
│   │   └── binding_config.py  # 手势绑定配置组件
│   └── threads/          # 后台线程
│       ├── __init__.py
│       └── gesture_detection.py  # 手势检测线程
├── gestures/             # 手势检测器模块
│   ├── __init__.py
│   ├── base.py          # 基础检测器类
│   ├── static/          # 静态手势检测器
│   │   ├── peace_sign.py # V字手势检测器
│   │   └── thumbs.py    # 竖大拇指检测器
│   └── dynamic/         # 动态手势检测器
│       └── hand_open.py # 握拳张开检测器
├── pyproject.toml       # 项目配置
└── README.md            # 项目说明
```

## 安装要求

- Python 3.12+
- 摄像头设备

## 安装步骤

1. 克隆或下载项目到本地
2. 安装依赖包：
   ```bash
   uv sync
   ```

## 运行方法

```bash
python app.py
```

### 或使用命令行版本
```bash
uv run main.py
```

## 使用说明

### 支持的手势
- **✌️ V字手势**: 伸出食指和中指形成V字形（默认绑定：音量增加）
- **👍 竖大拇指**: 竖起大拇指，其他手指握拳（默认绑定：音量减少）
- **👎 倒竖大拇指**: 倒竖大拇指，其他手指握拳（默认绑定：静音）
- **🖐️ 握拳张开**: 从握拳状态快速张开手掌（默认绑定：窗口最大化）
- **👌 OK手势**: 拇指和食指形成圆圈（默认绑定：复制）
- **⬅️ 左滑手势**: 手背到手心的左滑动作（默认绑定：后退）
- **➡️ 右滑手势**: 手背到手心的右滑动作（默认绑定：前进）
- **⬆️ 上滑手势**: 手背到手心的上滑动作（默认绑定：向上翻页）
- **⬇️ 下滑手势**: 手背到手心的下滑动作（默认绑定：向下翻页）

### 支持的动作类型
- **键盘快捷键**: 如 Ctrl+C、Alt+Tab、F5 等
- **系统功能**: 窗口最大化/最小化、音量控制、媒体播放控制等
- **自定义功能**: 可扩展的自定义动作

## 配置选项

可以通过修改 `config.py` 文件来调整以下设置：

- **摄像头配置**: 摄像头索引、检测参数
- **显示配置**: 是否显示关键点、手掌中心、摄像头窗口等
- **手势参数**: 各种手势的检测阈值和敏感度
- **颜色配置**: 界面元素的颜色设置

## 手势检测原理

### 静态手势
- **V字手势**: 检测食指和中指是否伸直且分开，其他手指是否弯曲，拇指是否收起
- **竖大拇指**: 检测大拇指是否朝上伸直，其他手指是否握拳贴近手掌

### 动态手势
- **握拳张开**: 通过分析手指尖位置的方差变化来检测从握拳到张开的动作

## 扩展开发

### 添加新的手势检测器

1. 在 `gestures/static/` 或 `gestures/dynamic/` 目录下创建新的检测器文件
2. 继承 `StaticGestureDetector` 或 `DynamicGestureDetector` 基类
3. 实现 `detect()` 方法
4. 在 `gesture_manager.py` 中注册新的检测器

### 自定义手势参数

修改 `config.py` 中的 `GESTURE_CONFIG` 部分来调整检测参数。
