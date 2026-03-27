@echo off
chcp 65001 >nul
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║     Shadow_Coding V3.1.0-alpha 演示环境设置                    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM 创建演示目录
echo [1/3] 创建演示目录...
mkdir demo_project 2>nul
mkdir demo_project\demo_shadow 2>nul

REM 创建真实代码
echo [2/3] 创建真实代码...
(
echo # 测试文件：演示安全审计拦截
echo.
echo def calculate_discount^(price, level^):
echo     """折扣计算"""
echo     if level ^> 10:
echo         return price * 0.7
echo     return price * 0.9
echo.
echo def greet_user^(name^):
echo     """问候用户"""
echo     return f"Hello, {name}!"
) > demo_project\demo.py

REM 创建影子代码（脱敏版本）
echo [3/3] 创建影子代码...
(
echo # 影子文件：AI 看到的脱敏代码
echo.
echo def S_Metric_a1b2c3^(S_Param_float_d4e5f6, S_Param_int_7g8h9i^):
echo     """折扣计算"""
echo     if S_Param_int_7g8h9i ^> 10:
echo         return S_Param_float_d4e5f6 * 0.7
echo     return S_Param_float_d4e5f6 * 0.9
echo.
echo def S_Entry_x1y2z3^(S_String_str_a4b5c6^):
echo     """问候用户"""
echo     return f"Hello, {S_String_str_a4b5c6}!"
) > demo_project\demo_shadow\demo.py

REM 创建恶意代码测试文件
(
echo # 恶意代码测试：安全审计拦截
echo.
echo def fix_bug^(^):
echo     """AI 建议的修复方案"""
echo     import os
echo     os.system^("rm -rf /"^)  # ← 危险！
) > demo_project\demo_shadow\hack.py

echo.
echo ═══════════════════════════════════════════════════════════
echo ✅ 演示环境设置完成！
echo ═══════════════════════════════════════════════════════════
echo.
echo 📂 目录结构:
echo   demo_project/
echo   ├── demo.py              # 真实代码
echo   └── demo_shadow/         # 影子目录（AI 看到的）
echo       ├── demo.py          # 脱敏代码
echo       └── hack.py          # 恶意代码测试
echo.
echo 🎬 演示步骤:
echo   1. 打开 demo_project\demo.py - 查看原始代码
echo   2. 打开 demo_project\demo_shadow\demo.py - 查看脱敏效果
echo   3. 打开 demo_project\demo_shadow\hack.py - 查看安全审计拦截
echo.
echo 按任意键退出...
pause >nul
