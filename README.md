# 奶娃桌宠

一个使用 Python、Tkinter 和 Pillow 编写的 Windows 桌面宠物程序。启动后，奶娃会以置顶的透明窗口显示在桌面上。

## 功能

- 启动时自动显示在屏幕右下角
- 按住角色可以拖动窗口位置
- 单击角色触发肚子膨胀动画
- 右键打开菜单并退出程序
- 可打包为无需 Python 环境的 Windows 单文件可执行程序

## 环境要求

- Windows
- Python 3.10 或更高版本
- Pillow
- PyInstaller（仅打包时需要）

安装 Pillow：

```powershell
py -m pip install Pillow
```

## 运行源码

首次运行或替换参考图片后，先生成透明背景素材：

```powershell
py process_asset.py
```

启动桌面宠物：

```powershell
py naiwa_pet.py
```

## 构建 Windows 程序

运行构建脚本：

```powershell
.\build.ps1
```

脚本会检查并安装 PyInstaller，然后生成无控制台窗口的单文件程序：

```text
dist\naiwa_desktop_pet.exe
```

也可以直接使用已有的 spec 文件进行构建：

```powershell
py -m PyInstaller --noconfirm --clean naiwa_desktop_pet.spec
```

## 项目结构

```text
assets/
  naiwa.png             # 程序运行时使用的透明角色图片
  naiwa_reference.png   # 用于生成透明素材的原始图片
naiwa_pet.py            # 桌面宠物主程序
process_asset.py        # 图片抠图和素材处理脚本
build.ps1               # Windows 打包脚本
naiwa_desktop_pet.spec  # PyInstaller 配置
```

`build/`、`dist/`、`__pycache__/` 和本地运行截图属于生成文件，已通过 `.gitignore` 排除，不应提交到 GitHub。

## 许可

当前仓库未声明开源许可证。如需公开发布，请根据素材和代码的授权情况补充 LICENSE 文件。
