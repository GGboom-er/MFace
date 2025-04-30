@echo off
rem --------------------------------------------------
rem  示例：Y:\GGbommer\scripts\MFace\plug-ins\test.bat
rem  本脚本假设与 CMakeLists.txt 同级
rem --------------------------------------------------

rem 1. 获取当前脚本所在目录
set SCRIPT_DIR=%~dp0
echo [Info] Script dir: %SCRIPT_DIR%

rem 2. 进入项目根目录（去掉末尾的反斜杠）
cd /d "%SCRIPT_DIR:~0,-1%"

rem 3. 创建并切换到 build 目录
if not exist build (
    mkdir build
)
cd build

rem 4. 调用 CMake 生成 VS2022 工程
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_BUILD_TYPE=Release
if errorlevel 1 (
    echo [Error] CMake 配置失败！
    pause
    exit /b 1
)

rem 5. 编译 Release 配置
cmake --build . --config Release
if errorlevel 1 (
    echo [Error] 编译失败！
    pause
    exit /b 1
)

echo [Info] 编译完成，输出文件位于 %CD%
pause
