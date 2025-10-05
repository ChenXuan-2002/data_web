# ============================
# data_web 自动构建与推送脚本
# ============================

# 1️⃣ 切换到项目根目录
Set-Location "D:\data_web"

Write-Host "=== 清理旧的 HTML 文件 ==="
# 删除旧的 index 和 datasets 下的所有 html
Remove-Item index-zh.html, index-en.html -Force -ErrorAction SilentlyContinue
Remove-Item datasets\*.html -Force -ErrorAction SilentlyContinue

# 2️⃣ 运行 build.py 生成新页面
Write-Host "=== 重新构建网站 ==="
python scripts\build.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ build.py 运行出错，已停止。" -ForegroundColor Red
    exit 1
}

# 3️⃣ Git 操作
Write-Host "=== 提交到 GitHub ==="
git add .
$time = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
git commit -m "auto update website at $time" 2>$null
git push origin main

# 4️⃣ 完成提示
Write-Host "`n✅ 网站已成功更新到 GitHub Pages！"
Write-Host "👉 打开: https://chenxuan-2002.github.io/data_web/"
