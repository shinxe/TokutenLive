import { reactive, readonly } from 'vue';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

const state = reactive({
  isLoggedIn: !!sessionStorage.getItem('authToken'),
  token: sessionStorage.getItem('authToken'),
});

const auth = {
  state: readonly(state),

  async login(password) {
    try {
      const response = await axios.post(`${API_URL}/login`, { password });
      if (response.data.token) {
        const token = response.data.token;
        state.isLoggedIn = true;
        state.token = token;
        sessionStorage.setItem('authToken', token);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Login failed:", error);
      // ログイン失敗時に既存のトークンをクリア
      this.logout();
      return false;
    }
  },

  logout() {
    state.isLoggedIn = false;
    state.token = null;
    sessionStorage.removeItem('authToken');
  },
};

export { auth };