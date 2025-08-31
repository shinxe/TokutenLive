<script setup>
const sports = ['サッカー', 'バレー', 'バスケ', 'バドミントン', '卓球'];
</script>

<template>
  <div id="app-wrapper">
    <header>
      <h1>クラスマッチ 得点集計</h1>
    </header>

    <main>
      <router-view />
    </main>

    <nav>
      <router-link to="/">
        <span class="icon">🏆</span>
        <span class="text">総合</span>
      </router-link>
      <router-link v-for="sport in sports" :key="sport" :to="`/sports/${sport}`">
        <span class="icon">{{ sport.slice(0, 1) }}</span> <span class="text">{{ sport }}</span>
      </router-link>
      <router-link to="/admin">
        <span class="icon">⚙️</span>
        <span class="text">管理</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
/* グローバルスタイル */
:root {
  --primary-blue: #007bff;
  --light-blue: #e3f2fd;
  --background-color: #f0f8ff;
  --text-color: #333;
  --card-background: #ffffff;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  --nav-height: 60px;
  /* ナビゲーションバーの高さ */
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
}

#app-wrapper {
  padding-bottom: var(--nav-height);
  /* 下部ナビゲーションの高さ分、余白を確保 */
}

header {
  text-align: center;
  padding: 15px 0;
  background-color: var(--card-background);
  box-shadow: var(--shadow);
  border-bottom: 1px solid var(--light-blue);
}

header h1 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--primary-blue);
}

main {
  padding: 20px 15px;
}

/* 下部固定ナビゲーション */
nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  background-color: var(--card-background);
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  justify-content: space-around;
  align-items: center;
  z-index: 1000;
  overflow-x: auto;
  /* 種目が多い場合スクロールできるように */
}

nav a {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: #888;
  font-size: 0.7rem;
  flex: 1;
  min-width: 60px;
  /* 各タブの最小幅 */
}

nav a .icon {
  font-size: 1.2rem;
  margin-bottom: 2px;
}

nav a.router-link-exact-active {
  color: var(--primary-blue);
  font-weight: bold;
}

/* レスポンシブ対応 (PCなど幅が広い画面) */
@media (min-width: 768px) {
  main {
    max-width: 800px;
    margin: 0 auto;
  }
}
</style>