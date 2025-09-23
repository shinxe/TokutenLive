<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { auth } from '../services/auth';

const password = ref('');
const error = ref(false);
const router = useRouter();

const handleLogin = () => {
  if (auth.login(password.value)) {
    router.push('/admin');
  } else {
    error.value = true;
    password.value = '';
  }
};
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h2>管理者ログイン</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="password">パスワード</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            :class="{ 'error-input': error }"
          />
        </div>
        <button type="submit">ログイン</button>
        <p v-if="error" class="error-message">パスワードが違います。</p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 70vh;
}

.login-box {
  width: 100%;
  max-width: 320px;
  padding: 30px;
  background: var(--card-background);
  border-radius: 12px;
  box-shadow: var(--shadow);
  text-align: center;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--primary-blue);
}

.form-group {
  margin-bottom: 20px;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

input[type="password"] {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-sizing: border-box;
}

.error-input {
  border-color: #f44336;
}

button {
  width: 100%;
  padding: 12px;
  border-radius: 8px;
  border: none;
  background-color: var(--primary-blue);
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #0056b3;
}

.error-message {
  color: #f44336;
  margin-top: 15px;
  font-size: 0.9rem;
}
</style>
