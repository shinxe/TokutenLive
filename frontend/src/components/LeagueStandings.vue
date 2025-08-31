<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../services/api';

const props = defineProps({
  sport: String,
  league: String,
});

const standings = ref([]);
const loading = ref(true);

const fetchStandings = async () => {
  loading.value = true;
  try {
    const response = await api.getLeagueStandings(props.sport, props.league);
    standings.value = response.data;
  } catch (err) {
    standings.value = []; // エラーの場合は空にする
  } finally {
    loading.value = false;
  }
};

onMounted(fetchStandings);
// sportやleagueが変わったらデータを再取得
watch(() => [props.sport, props.league], fetchStandings);
</script>

<template>
  <div class="league-table">
    <h4>{{ league }}リーグ</h4>
    <div v-if="loading">...</div>
    <table v-else-if="standings.length > 0">
      <thead>
        <tr>
          <th>順位</th>
          <th>クラス</th>
          <th>勝</th>
          <th>敗</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in standings" :key="item.class_id">
          <td>{{ item.rank }}</td>
          <td>{{ item.class_name }}</td>
          <td>{{ item.wins }}</td>
          <td>{{ item.losses }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>試合データがありません</p>
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