#!/usr/bin/env python3
"""把 guandan.html 打包成可安装、可离线的 PWA。
   改完 guandan.html 之后重跑一次这个脚本即可。
   用法: python3 build-pwa.py
"""
import json, math, os, re, struct, zlib

SRC = 'guandan.html'
OUT = 'docs'   # GitHub Pages 只认仓库根目录或 /docs
VERSION = 'v25'                     # 改了内容就改这里，装过的手机才会拿到新版本

# ---------------------------------------------------------------- 图标
# 图标是设计稿（白牌 + 朱砂「掼」），存在 icons/，这里只负责复制过去。
# 要改图标就改 icons/ 里的文件，别在这里画。
import shutil
ICONS = ['icon-192.png', 'icon-512.png', 'icon-180.png', 'icon-512-maskable.png']

# ---------------------------------------------------------------- 组装
os.makedirs(OUT, exist_ok=True)
src = open(SRC, encoding='utf-8').read()

head_end = src.index('</style>') + len('</style>')
head_src, body_src = src[:head_end], src[head_end:]
title = re.search(r'<title>(.*?)</title>', head_src).group(1)
head_src = re.sub(r'<meta charset="utf-8">\s*', '', head_src)

head_extra = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#141A18" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#E7EAE5" media="(prefers-color-scheme: light)">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icon-180.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="掼蛋助手">
<style>
  /* 装到主屏幕后没有浏览器边框，得自己让开刘海和home条 */
  .top{{padding-top:calc(10px + env(safe-area-inset-top))}}
  .shell{{padding-bottom:calc(64px + env(safe-area-inset-bottom))}}
</style>
'''

sw_reg = '''<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('sw.js').catch(function () { /* 离线或不支持，App 照常用 */ });
  });
}
</script>
'''

html = ('<!doctype html>\n<html lang="zh-CN">\n<head>\n' + head_extra + head_src
        + '\n</head>\n<body>\n' + body_src.strip() + '\n' + sw_reg + '\n</body>\n</html>\n')
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)

manifest = {
    "name": title,
    "short_name": "掼蛋助手",
    "description": "掼蛋记牌器、出牌建议、进贡助手与升级计分器",
    "start_url": ".",
    "scope": ".",
    "display": "standalone",
    "background_color": "#141A18",
    "theme_color": "#141A18",
    "lang": "zh-CN",
    "icons": [
        {"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
open(os.path.join(OUT, 'manifest.json'), 'w', encoding='utf-8').write(
    json.dumps(manifest, ensure_ascii=False, indent=2))

sw = f'''/* 掼蛋助手 —— 离线缓存。改了内容就把 CACHE 版本号改掉。
   页面网络优先（推完打开一次就是新版），静态资源缓存优先。 */
const CACHE = 'guandan-{VERSION}';
const SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
}});

self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
}});

self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  const isPage = e.request.mode === 'navigate'
              || e.request.destination === 'document'
              || url.pathname.endsWith('/')
              || url.pathname.endsWith('/index.html');

  if (isPage) {{
    // 页面走网络优先：有网永远拿最新的，推完打开一次就更新；没网回落到缓存
    e.respondWith(
      fetch(e.request).then(res => {{
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {{}});
        return res;
      }}).catch(() => caches.match(e.request).then(hit => hit || caches.match('./')))
    );
    return;
  }}

  // 图标、字体这些不会变的，缓存优先
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {{
      if (res && (res.ok || res.type === 'opaque')) {{
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {{}});
      }}
      return res;
    }}))
  );
}});
'''
open(os.path.join(OUT, 'sw.js'), 'w', encoding='utf-8').write(sw)

for name in ICONS:
    src_icon = os.path.join('icons', name)
    if os.path.exists(src_icon):
        shutil.copy2(src_icon, os.path.join(OUT, name))
    else:
        print('  ⚠ 缺图标:', src_icon)

readme = '''# 掼蛋牌桌助手 · PWA

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
'''
open(os.path.join(OUT, 'README.md'), 'w', encoding='utf-8').write(readme)

print('生成完毕 →', OUT + '/')
for f in sorted(os.listdir(OUT)):
    print('  %-24s %8.1f KB' % (f, os.path.getsize(os.path.join(OUT, f)) / 1024))
