#!/bin/bash
# GitHub推送辅助脚本

set -e

REPO_DIR="$HOME/projects/ercot-scraper"
GITHUB_USER="lanxindeng8"
REPO_NAME="ercot-scraper"

echo "========================================="
echo "GitHub推送辅助脚本"
echo "========================================="
echo ""

cd "$REPO_DIR"

echo "当前仓库状态："
git status -s
echo ""

echo "待推送的提交："
git log origin/master..HEAD --oneline 2>/dev/null || git log --oneline | head -5
echo ""

echo "请选择推送方式："
echo "1) 使用Personal Access Token (HTTPS)"
echo "2) 使用SSH密钥"
echo "3) 退出"
echo ""

read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "========================================="
        echo "使用Personal Access Token推送"
        echo "========================================="
        echo ""
        echo "如果你还没有token，请访问："
        echo "https://github.com/settings/tokens/new"
        echo ""
        echo "权限要求："
        echo "  ✅ repo (所有子选项)"
        echo "  ✅ workflow"
        echo ""
        read -p "请输入你的Personal Access Token: " token

        if [ -z "$token" ]; then
            echo "错误：Token不能为空"
            exit 1
        fi

        echo ""
        echo "推送中..."
        git push "https://${token}@github.com/${GITHUB_USER}/${REPO_NAME}.git" master

        echo ""
        echo "✅ 推送成功！"
        echo ""
        echo "保存token以便后续使用（可选）："
        echo "  git remote set-url origin https://${token}@github.com/${GITHUB_USER}/${REPO_NAME}.git"
        ;;

    2)
        echo ""
        echo "========================================="
        echo "使用SSH密钥推送"
        echo "========================================="
        echo ""
        echo "检查SSH密钥..."

        if [ ! -f "$HOME/.ssh/id_ed25519" ] && [ ! -f "$HOME/.ssh/id_rsa" ]; then
            echo ""
            echo "未找到SSH密钥，开始生成..."
            read -p "请输入你的邮箱: " email

            ssh-keygen -t ed25519 -C "$email" -f "$HOME/.ssh/id_${GITHUB_USER}" -N ""

            echo ""
            echo "✅ SSH密钥已生成："
            echo "   公钥位置: $HOME/.ssh/id_${GITHUB_USER}.pub"
            echo ""
            echo "请复制以下公钥到GitHub："
            echo "-----------------------------------"
            cat "$HOME/.ssh/id_${GITHUB_USER}.pub"
            echo "-----------------------------------"
            echo ""
            echo "添加步骤："
            echo "1. 访问：https://github.com/settings/keys"
            echo "2. 点击 'New SSH key'"
            echo "3. 粘贴上面的公钥内容"
            echo "4. 点击 'Add SSH key'"
            echo ""
            read -p "完成后按Enter继续..."

            # 添加到ssh-agent
            eval "$(ssh-agent -s)"
            ssh-add "$HOME/.ssh/id_${GITHUB_USER}"
        fi

        # 更改remote为SSH
        echo "配置SSH remote..."
        git remote set-url origin "git@github.com:${GITHUB_USER}/${REPO_NAME}.git"

        echo "推送中..."
        git push -u origin master

        echo ""
        echo "✅ 推送成功！"
        ;;

    3)
        echo "退出"
        exit 0
        ;;

    *)
        echo "无效的选项"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "推送完成！"
echo "========================================="
echo ""
echo "查看仓库："
echo "  https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "下一步："
echo "  1. 配置GitHub Secrets（运行：./configure-secrets.sh）"
echo "  2. 启用GitHub Actions"
echo "  3. 手动触发workflow测试"
echo ""
