cmake_minimum_required(VERSION 3.27)
project(bs_api LANGUAGES CXX)

# -------------------- 1. 编译选项 --------------------
if (MSVC)
    # 让 cl.exe 用 UTF-8 编码读取源码
    add_compile_options(/utf-8)
    # 与 Maya 运行时保持一致，使用动态 CRT (/MD)
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /MD")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -------------------- 2. 路径变量 --------------------
# Maya 2025 安装根目录
set(MAYA_LOCATION "C:/Program Files/Autodesk/Maya2025")
# Maya devkit 路径
set(DEVKIT_INCLUDE "${MAYA_LOCATION}/include")
set(DEVKIT_LIB     "${MAYA_LOCATION}/lib")

# JsonCpp 头文件 & 库（静态版 jsoncpp.lib）
set(JSONCPP_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/include")
set(JSONCPP_LIB     "${CMAKE_CURRENT_SOURCE_DIR}/3rdparty/jsoncpp.lib")

# -------------------- 3. 声明目标 --------------------
add_library(bs_api MODULE
    bs_api.cpp
)

# -------------------- 4. 包含头文件路径 --------------------
target_include_directories(bs_api PRIVATE
    "${DEVKIT_INCLUDE}"
    "${DEVKIT_INCLUDE}/Python311/Python"    # Maya 自带 Python 3.11 头
    "${DEVKIT_INCLUDE}/tbb"          # Maya 自带 TBB
    "${JSONCPP_INCLUDE}"
)

# -------------------- 5. 链接库 --------------------
target_link_libraries(bs_api PRIVATE
    # Maya API
    "${DEVKIT_LIB}/Foundation.lib"
    "${DEVKIT_LIB}/OpenMaya.lib"
    "${DEVKIT_LIB}/OpenMayaAnim.lib"
    # Maya 内置 Python
    "${DEVKIT_LIB}/python311.lib"
    # TBB
    "${DEVKIT_LIB}/tbb.lib"
    # JsonCpp 静态库
    "${JSONCPP_LIB}"
)

# -------------------- 6. 输出设置 --------------------
# 去掉默认 lib 前缀，后缀设为 .pyd 以便 Python import
set_target_properties(bs_api PROPERTIES
    PREFIX ""
    SUFFIX ".mll"
)

# -------------------- 7. 预处理宏 --------------------
# 让代码中可通过 #ifdef maya2025 / #ifdef python3 做条件编译
target_compile_definitions(bs_api PRIVATE
    maya2025
    python3
    JSONCPP_STATIC
)
