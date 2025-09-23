<script setup>
import { auth } from './services/auth';
import { useRouter } from 'vue-router';

const sports = ['サッカー', 'バレー', 'バスケ', 'バドミントン', '卓球'];
const sportEmojis = {
  'サッカー': '⚽',
  'バレー': '🏐',
  'バスケ': '🏀',
  'バドミントン': '🏸',
  '卓球': '🏓',
};

const router = useRouter();

const handleLogout = () => {
  auth.logout();
  router.push('/'); // ホームにリダイレクト
};
</script>

<template>
  <div id="app-wrapper">
    <header>
      <h1>
        <span class="header-icon">🏆</span>
        クラスマッチ 得点集計
      </h1>
    </header>

    <main>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <nav>
      <router-link to="/">
        <span class="icon">🏆</span>
        <span class="text">総合</span>
      </router-link>
      <router-link v-for="sport in sports" :key="sport" :to="`/sports/${sport}`">
        <span class="icon">{{ sportEmojis[sport] }}</span>
        <span class="text">{{ sport }}</span>
      </router-link>

      <!-- 認証リンク -->
      <router-link v-if="auth.state.isLoggedIn" to="/admin">
        <span class="icon">⚙️</span>
        <span class="text">管理</span>
      </router-link>
      <a v-if="auth.state.isLoggedIn" @click="handleLogout" href="#" class="logout-link">
        <span class="icon">🚗</span>
        <span class="text">ログアウト</span>
      </a>
      <router-link v-else to="/login">
        <span class="icon">⚙️</span>
        <span class="text">ログイン</span>
      </router-link>
    </nav>
  </div>
</template>

<style>
/* グローバルスタイル */
:root {
  --primary-blue: #007bff;
  --primary-blue-dark: #0056b3;
  --light-blue: #e3f2fd;
  --background-color: #f4f7f9;
  --text-color: #333;
  --text-color-light: #666;
  --card-background: #ffffff;
  --shadow: 0 6px 20px rgba(0, 0, 0, 0.07);
  --nav-height: 65px;
}

body {
  margin: 0;
  font-family: 'Helvetica Neue', 'Arial', 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', 'Meiryo', sans-serif;
  background-color: var(--background-color);
  color: var(--text-color);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app-wrapper {
  padding-top: 80px;
  /* ヘッダーの高さ分 */
  padding-bottom: var(--nav-height);
}

header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  text-align: center;
  padding: 20px 0;
  background: linear-gradient(135deg, #007bff, #0056b3);
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
  border-bottom: 1px solid var(--light-blue);
  color: white;
}

header h1 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.header-icon {
  font-size: 1.8rem;
  filter: drop-shadow(0 2px 3px rgba(0, 0, 0, 0.2));
}

main {
  padding: 20px 15px;
}

/* --- 下部固定ナビゲーション --- */
nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  background-color: var(--card-background);
  box-shadow: 0 -5px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-around;
  align-items: stretch;
  /* 上下いっぱいに広げる */
  z-index: 1000;
  overflow-x: auto;
}

nav a {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  color: var(--text-color-light);
  font-size: 0.7rem;
  flex: 1;
  min-width: 65px;
  position: relative;
  transition: color 0.3s ease, background-color 0.3s ease;
}

nav a .icon {
  font-size: 1.6rem;
  /* アイコンを大きく */
  margin-bottom: 4px;
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

nav a .text {
  transition: opacity 0.3s ease;
}

/* アクティブなリンクのスタイル */
nav a.router-link-exact-active {
  color: var(--primary-blue);
  font-weight: 700;
}

nav a.router-link-exact-active .icon {
  transform: translateY(-5px) scale(1.1);
}

/* ログアウトボタンのスタイル調整 */
.logout-link {
  cursor: pointer;
}

/* --- ページ遷移アニメーション --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* レスポンシブ対応 */
@media (min-width: 768px) {
  main {
    max-width: 800px;
    margin: 0 auto;
  }

  #app-wrapper {
    padding-top: 90px;
    /* PCではヘッダーを少し高く */
  }

  header h1 {
    font-size: 1.6rem;
  }

  .header-icon {
    font-size: 2rem;
  }
}
</style>