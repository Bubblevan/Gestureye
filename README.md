# 手势识别控制系统

这是一个基于计算机视觉的手势识别系统，可以通过手势控制系统功能，支持 **Windows、macOS 和 Linux** 跨平台运行。

## 系统要求

- Python 3.8+
- 摄像头（用于手势识别）
- 支持的操作系统：
  - ✅ Windows 10/11
  - ✅ macOS 10.14+  
  - ✅ Linux (Ubuntu 18.04+, Fedora, Arch 等)


交互式安装脚本会自动：
- 检测你的操作系统和可用包管理器
- 推荐最适合的安装方式
- 自动处理平台特定配置

### ⚙️ 手动安装

我们也提供两种手动安装方式，供有经验的用户选择：

### 方式 1: 使用 Conda（推荐 - 自动处理系统依赖）

```bash
# 克隆项目
git clone <项目地址>
cd project

# 创建并激活 conda 环境
conda env create -f environment.yml
conda activate gesture-control-system

# 启动应用
python app.py
```

**Conda 方式优势：**
- ✅ 自动安装系统级音频库（Linux ALSA/PulseAudio）
- ✅ 无需手动安装系统包
- ✅ 环境隔离更好
- ✅ 跨平台依赖管理

### 方式 2: 使用 UV/pip（轻量级）

```bash
# 克隆项目
git clone <项目地址>
cd project

# 使用 uv（推荐）
uv sync
# 或使用 pip
pip install -r requirements.txt

# Linux 用户可选安装增强功能
uv add --optional linux
# 或: pip install ".[linux]"

# 启动应用  
python app.py
```

**UV/pip 方式优势：**
- ✅ 安装速度更快
- ✅ 更轻量级
- ✅ 现代化包管理
- ✅ 可选依赖组支持

## 📦 依赖管理对比

| 特性 | Conda | UV/pip |
|------|-------|--------|
| 系统级音频库 | ✅ 自动安装 | ⚠️ 需手动安装* |
| 安装速度 | 中等 | 很快 |
| 环境隔离 | 完整 | Python级别 |
| 跨平台一致性 | 最佳 | 良好 |
| 磁盘占用 | 较大 | 较小 |

*UV/pip 用户在 Linux 上需要手动安装音频工具获得最佳体验

## 🔧 平台特定配置

### Windows
- `pywin32` 会自动安装，提供完整的窗口管理功能
- 支持所有系统功能（音量、窗口控制、媒体键等）

### macOS
- 某些功能需要授予辅助功能权限
- 音量控制使用 AppleScript
- 窗口管理使用系统快捷键

### Linux

#### Conda 用户（推荐）
```bash
# 依赖已自动安装，直接使用
conda activate gesture-control-system
python app.py
```

#### UV/pip 用户
```bash
# 安装系统音频工具（可选，增强体验）
# Ubuntu/Debian:
sudo apt install alsa-utils pulseaudio-utils wmctrl

# Fedora/RHEL:
sudo dnf install alsa-utils pulseaudio-utils wmctrl

# Arch Linux:
sudo pacman -S alsa-utils pulseaudio wmctrl

# 安装 Python X11 支持（可选）
pip install ".[linux]"
```

## 🎯 功能支持矩阵

| 功能 | Windows | macOS | Linux (Conda) | Linux (pip) |
|------|---------|-------|---------------|-------------|
| 键盘快捷键 | ✅ | ✅ | ✅ | ✅ |
| 窗口最大化/最小化 | ✅ | ✅ | ✅ | ✅ |
| 窗口关闭 | ✅ | ✅ | ✅ | ✅ |
| 音量控制 | ✅ | ✅ | ✅ | ⚠️* |
| 媒体键 | ✅ | ✅ | ✅ | ✅ |
| 鼠标滚轮 | ✅ | ✅ | ✅ | ✅ |
| 窗口切换 | ✅ | ✅ | ✅ | ✅ |

*需要手动安装系统音频工具

## 🚀 启动项目

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

## 🛠️ 开发配置

### 安装开发依赖

**Conda:**
```bash
conda activate gesture-control-system
# 开发工具已包含在环境中
```

**UV:**
```bash
# 安装开发依赖
uv add --dev pytest black flake8
# 或使用可选依赖组
uv sync --extra dev
```

### 代码格式化
```bash
# 格式化代码
black .

# 检查代码风格
flake8 .

# 运行测试
pytest
```

## 🔍 故障排除

### 通用问题
- **权限错误**：某些功能可能需要管理员权限
- **摄像头访问**：确保系统允许 Python 访问摄像头
- **防火墙**：Socket 通信可能被防火墙阻止

### Windows
```bash
# 如果遇到 pywin32 相关错误
pip uninstall pywin32
pip install pywin32
```

### macOS
- 首次运行需要在"系统偏好设置 > 安全性与隐私 > 辅助功能"中授权
- 检查"系统偏好设置 > 安全性与隐私 > 自动化"权限

### Linux
```bash
# 音量控制问题 - 尝试不同音频后端
sudo apt install pulseaudio pulseaudio-utils  # PulseAudio
sudo apt install alsa-utils  # ALSA

# 窗口管理增强
sudo apt install wmctrl

# Python X11 支持
pip install python-xlib
```

## 📋 快速检查

运行兼容性测试：
```bash
python -c "
import platform
print(f'平台: {platform.system()}')
try:
    from core.action_executor import ActionExecutor
    print('✅ 核心组件正常')
except ImportError as e:
    print(f'❌ 导入失败: {e}')
"
```

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

---

## 🔄 系统更新 - 轨迹数据处理

### 📊 新增功能 (最新更新)

#### 🎯 完整手势绑定配置
现在所有 10 个手势都已配置完成：

| 编号 | 手势名 | 功能 | 类型 |
|------|--------|------|------|
| 1 | FingerCountOne | 复制 (Ctrl+C) | 静态 |
| 2 | FingerCountTwo | 粘贴 (Ctrl+V) | 静态 |
| 3 | FingerCountThree | 撤销 (Ctrl+Z) | 静态 |
| 4 | HandOpen | 窗口全屏 | 动态 |
| 5 | TwoFingerSwipe | 窗口最小化 | 动态 |
| 6 | HandClose | **真正的窗口拖拽** | 动态+轨迹 |
| 7 | HandSwipe | 窗口切换 | 动态 |
| 8 | HandFlip | 关闭窗口 | 动态 |
| 9 | ThumbsUp | 向上滚动 | 静态 |
| 10 | ThumbsDown | 向下滚动 | 静态 |

#### 🔧 轨迹数据处理系统

**HandClose 手势工作流程：**
1. **触发阶段**：检测到"张开到握拳"动作 → 发送 `gesture_detection` 类型数据
2. **追踪阶段**：握拳移动 → 持续发送 `trail_change` 类型数据，包含 `dx`、`dy` 位移信息
3. **执行阶段**：UI 实时根据位移数据移动活动窗口

**技术实现：**
- ✅ 修复了 Socket 接收器对 `trail_change` 类型数据的处理
- ✅ 新增 `trail_change_detected` 信号传递轨迹数据
- ✅ 实现跨平台窗口拖拽功能（Windows API、macOS AppleScript、Linux wmctrl/X11）
- ✅ 添加鼠标模拟拖拽作为备用方案

#### 🚀 启动测试

1. **启动 project (UI控制台)：**
   ```bash
   cd project
   python app.py
   # 点击 "🔌 启动Socket服务器"
   ```

2. **启动 dyn_gestures (手势识别)：**
   ```bash
   cd dyn_gestures
   python main.py
   ```

3. **测试轨迹拖拽：**
   - 张开手掌，然后握拳 → 触发 HandClose 手势
   - 保持握拳状态并移动手部 → 看到活动窗口实时跟随移动
   - 松开握拳 → 停止拖拽

**调试模式：** 在 project 中启用"开发者模式"可以看到详细的轨迹数据：
```
轨迹变化: left手 移动(+5,-3) 距离=5.8
```

现在系统已完全解决了 HandClose 手势的轨迹数据处理问题，不会再出现重复执行最小化的冲突！🎉
