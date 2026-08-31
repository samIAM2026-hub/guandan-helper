/* 掼蛋助手 —— 离线缓存。改了内容就把 CACHE 版本号改掉。
   页面网络优先（推完打开一次就是新版），静态资源缓存优先。 */
const CACHE = 'guandan-v28';
const SHELL = ['./', './index.html', './manifest.json', './icon-192.png', './icon-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  const isPage = e.request.mode === 'navigate'
              || e.request.destination === 'document'
              || url.pathname.endsWith('/')
              || url.pathname.endsWith('/index.html');

  if (isPage) {
    // 页面走网络优先：有网永远拿最新的，推完打开一次就更新；没网回落到缓存
    e.respondWith(
      fetch(e.request).then(res => {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
        return res;
      }).catch(() => caches.match(e.request).then(hit => hit || caches.match('./')))
    );
    return;
  }

  // 图标、字体这些不会变的，缓存优先
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      if (res && (res.ok || res.type === 'opaque')) {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
      }
      return res;
    }))
  );
});
