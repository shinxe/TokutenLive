<script setup>
import { ref, onMounted, defineProps } from 'vue';
import api from '../services/api';

const props = defineProps({
  skipCount: {
    type: Number,
    default: 5
  }
});

const rankings = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchRankings = async () => {
  try {
    const response = await api.getTotalRankings({ skip: props.skipCount });
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

const getRankClass = (rank) => {
  if (rank === 1) return 'rank-gold';
  if (rank === 2) return 'rank-silver';
  if (rank === 3) return 'rank-bronze';
  return 'rank-normal';
};

const getRankIcon = (rank) => {
  if (rank === 1) return '🥇';
  if (rank === 2) return '🥈';
  if (rank === 3) return '🥉';
  return null;
};
</script>

<template>
  <div class="total-ranking-container">
    <h2 class="ranking-title">総合ランキング</h2>
    <div v-if="loading" class="loading-state">読み込み中...</div>
    <div v-if="error" class="error-state">{{ error }}</div>
    <div class="table-container" v-if="!loading && !error">
      <table>
        <thead>
          <tr>
            <th class="rank-col">順位</th>
            <th class="class-col">クラス</th>
            <th class="points-col">合計得点</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in rankings" :key="item.class_id" :class="getRankClass(item.rank)">
            <td class="rank-col">
              <span class="rank-icon">{{ getRankIcon(item.rank) }}</span>
              <span v-if="!getRankIcon(item.rank)">{{ item.rank }}</span>
            </td>
            <td class="class-col">{{ item.class_name }}</td>
            <td class="points-col">{{ item.total_points }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.total-ranking-container {
    padding: 2rem 1rem;
    background: var(--color-background);
}

.ranking-title {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 2rem;
    color: var(--color-heading);
    text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.loading-state, .error-state {
    text-align: center;
    padding: 2rem;
    font-size: 1.2rem;
    color: var(--color-text-mute);
}

.error-state {
    color: #e53e3e; /* A standard error color */
}

.table-container {
    max-width: 800px;
    margin: 0 auto;
    background: var(--color-card-background);
    border-radius: 15px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    overflow: hidden;
    border: 1px solid var(--color-border);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 1rem 1.5rem;
    text-align: left;
    border-bottom: 1px solid var(--color-border);
}

th {
    background-color: var(--color-background-soft);
    font-weight: 600;
    font-size: 1rem;
    color: var(--color-heading);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

tr:last-child td {
    border-bottom: none;
}

tbody tr:hover {
    background-color: var(--color-background-mute);
}

.rank-col {
    width: 80px;
    text-align: center;
    font-weight: bold;
}

.class-col {
    font-weight: 500;
    color: var(--color-text);
}

.points-col {
    text-align: right;
    font-weight: bold;
    color: var(--color-heading);
}

.rank-icon {
    font-size: 1.5rem;
    vertical-align: middle;
}

/* Rank-specific styling */
.rank-gold td {
    background-color: rgba(255, 215, 0, 0.1);
    font-size: 1.1rem;
}
.rank-silver td {
    background-color: rgba(192, 192, 192, 0.1);
    font-size: 1.05rem;
}
.rank-bronze td {
    background-color: rgba(205, 127, 50, 0.1);
}

.rank-gold .class-col {
    font-weight: 700;
    color: #c99700;
}
.rank-silver .class-col {
    font-weight: 600;
    color: #8d8d8d;
}
.rank-bronze .class-col {
    font-weight: 600;
    color: #a4661b;
}
</style>

