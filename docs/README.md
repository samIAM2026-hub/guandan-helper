# 掼蛋牌桌助手 · PWA

装到手机主屏幕，离线也能用。

## 部署（GitHub Pages，免费）

1. 在 GitHub 上新建一个仓库（Public，不要勾 README）
2. 在项目根目录执行：

       git remote add origin https://github.com/<用户名>/<仓库名>.git
       git branch -M main
       git push -u origin main

3. 仓库 Settings → Pages → Source 选 `main` 分支 + `/docs` 目录，保存
4. 等一两分钟，地址是 `https://<用户名>.github.io/<仓库名>/`

## 装到手机

- **iPhone**：用 **Safari** 打开那个地址（必须是 Safari，Chrome 不行）→ 分享 → 添加到主屏幕
- **Android**：Chrome 打开 → 菜单 → 安装应用 / 添加到主屏幕

装好之后是全屏的，没有地址栏，断网也能开。数据存在手机本地。

## 更新

改完 `guandan.html`，回到项目根目录跑：

    python3 build-pwa.py

再 `git add -A && git commit -m 更新 && git push`。记得先把 `build-pwa.py` 里的 `VERSION` 改一下，
否则装过的手机会继续用旧缓存。
