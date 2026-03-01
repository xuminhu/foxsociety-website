#!/bin/bash
# 狐狸学社网站快速部署脚本

echo "🦊 Fox Society Website Deploy Script"
echo "===================================="

# 检查 hugo
if ! command -v hugo &> /dev/null; then
    echo "❌ Hugo 未安装，请先安装 Hugo"
    echo "Mac: brew install hugo"
    echo "Windows: choco install hugo-extended"
    exit 1
fi

echo "✅ Hugo 已安装"

# 构建
echo "🔨 构建网站..."
hugo --minify

if [ $? -eq 0 ]; then
    echo "✅ 构建成功"
    echo "📁 输出目录: public/"
    echo ""
    echo "下一步:"
    echo "1. 确保已配置 GitHub Secrets"
    echo "2. git push 到 main 分支"
    echo "3. 查看 GitHub Actions 自动部署"
else
    echo "❌ 构建失败"
    exit 1
fi
