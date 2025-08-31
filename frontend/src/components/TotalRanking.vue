<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const rankings = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchRankings = async () => {
  try {
    const response = await api.getTotalRankings();
    rankings.value = response.data;
  } catch (err) {
    error.value = 'ランキングの取得に失敗しました。';
    console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchRankings();
});
</script>

<template>
  <div>
    <h2>総合ランキング</h2>
    <div v-if="loading">読み込み中...</div>
    <div v-if="error" class="error">{{ error }}</div>
    <table v-if="!loading && !error">
      <thead>
        <tr>
          <th>順位</th>
          <th>クラス</th>
          <th>合計得点</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in rankings" :key="item.class_id">
          <td>{{ item.rank }}</td>
          <td>{{ item.class_name }}</td>
          <td>{{ item.total_points }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.table-container {
  overflow-x: auto;
  /* スマホでテーブルがはみ出した場合にスクロール */
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  background-color: var(--card-background);
  box-shadow: var(--shadow);
  border-radius: 8px;
  overflow: hidden;
}

th,
td {
  padding: 12px 15px;
  text-align: center;
  border-bottom: 1px solid var(--light-blue);
}

th {
  background-color: var(--light-blue);
  color: var(--primary-blue);
  font-weight: 600;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: var(--light-blue);
}

.error {
  color: red;
  text-align: center;
}
</style>