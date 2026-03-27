@echo off
REM PyPI 发布脚本 (Windows)

echo.
echo ==========================
echo   Shadow_Coding PyPI 发布脚本
echo ==========================
echo.

REM 1. 清理旧的构建文件
echo [1/4] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.egg-info rmdir /s /q *.egg-info

REM 2. 构建新的分发包
echo [2/4] 构建分发包...
python -m build

REM 3. 验证分发包
echo [3/4] 验证分发包...
twine check dist/*

REM 4. 提示用户
echo.
echo 构建完成！请选择发布方式：
echo.
echo   1. 发布到 TestPyPI (测试)
echo   2. 发布到 PyPI (正式)
echo   3. 退出
echo.
set /p choice="请选择 (1/2/3): "

if "%choice%"=="1" goto testpypi
if "%choice%"=="2" goto pypi
if "%choice%"=="3" goto end
goto invalid

:testpypi
echo [4/4] 发布到 TestPyPI...
twine upload --repository testpypi dist/*
echo.
echo 发布完成！访问：https://test.pypi.org/project/shadow_coding/
goto end

:pypi
echo [4/4] 发布到 PyPI...
twine upload dist/*
echo.
echo 发布完成！访问：https://pypi.org/project/shadow_coding/
goto end

:invalid
echo 无效选择
exit /b 1

:end
echo.
pause
