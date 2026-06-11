# Custom hook to include project workflow module
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# 收集项目 workflow 模块的所有子模块
hiddenimports = collect_submodules('workflow')
