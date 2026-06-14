#!/bin/bash
# Offer捕手 · GitHub Pages 一键部署
set -e
cd "$(dirname "$0")"

REPO_NAME="${1:-tencent-offer-catcher}"

if ! command -v gh &>/dev/null; then
  echo "请先安装 GitHub CLI: brew install gh" >&2
  exit 1
fi

if ! gh auth status &>/dev/null; then
  echo "请先登录 GitHub: gh auth login"
  exit 1
fi

echo ">>> 创建/推送仓库: ${REPO_NAME}"
if git remote get-url origin &>/dev/null; then
  git push -u origin main
else
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push --description "Offer捕手 · 腾讯岗位专属匹配工具"
fi

OWNER=$(gh api user -q .login)
echo ">>> 开启 GitHub Pages"
gh api "repos/${OWNER}/${REPO_NAME}/pages" -X POST \
  -f build_type=legacy \
  -f source[branch]=main \
  -f source[path]=/ 2>/dev/null || \
gh api "repos/${OWNER}/${REPO_NAME}/pages" -X PUT \
  -f build_type=legacy \
  -f source[branch]=main \
  -f source[path]=/

echo ""
echo "=========================================="
echo " 部署完成！约 1-3 分钟后可访问："
echo ""
echo " 作业一（主应用）："
echo "   https://${OWNER}.github.io/${REPO_NAME}/index.html"
echo ""
echo " 作业二（方案说明）："
echo "   https://${OWNER}.github.io/${REPO_NAME}/doc.html"
echo "=========================================="
