#!/bin/bash
# PyPI 发布脚本

echo "🚀 Shadow_Coding PyPI 发布脚本"
echo "=========================="

# 1. 清理旧的构建文件
echo "🧹 清理旧的构建文件..."
rm -rf build/ dist/ *.egg-info

# 2. 构建新的分发包
echo "📦 构建分发包..."
python -m build

# 3. 验证分发包
echo "✅ 验证分发包..."
twine check dist/*

# 4. 提示用户
echo ""
echo "✨ 构建完成！请选择发布方式："
echo ""
echo "  1. 发布到 TestPyPI (测试)"
echo "  2. 发布到 PyPI (正式)"
echo "  3. 退出"
echo ""
read -p "请选择 (1/2/3): " choice

case $choice in
    1)
        echo "📤 发布到 TestPyPI..."
        twine upload --repository testpypi dist/*
        echo "✅ 发布完成！访问：https://test.pypi.org/project/shadow_coding/"
        ;;
    2)
        echo "📤 发布到 PyPI..."
        twine upload dist/*
        echo "✅ 发布完成！访问：https://pypi.org/project/shadow_coding/"
        ;;
    3)
        echo "👋 退出"
        exit 0
        ;;
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac
