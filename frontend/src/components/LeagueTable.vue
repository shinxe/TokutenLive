<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '../services/api';

const props = defineProps({
  sport: String,
  league: String,
});

const matches = ref([]);
const loading = ref(true);
const error = ref(null);

// Helper to determine if a sport is sets-based
const isSetsBased = (sportName) => {
  return ['卓球', 'バドミントン'].includes(sportName);
};

// All unique class names in this league, sorted alphabetically
const teams = computed(() => {
  if (!matches.value.length) return [];
  const classNames = new Set();
  matches.value.forEach(match => {
    if (match.class1) classNames.add(match.class1.name);
    if (match.class2) classNames.add(match.class2.name);
  });
  return Array.from(classNames).sort();
});

// Create a 2D map for easy lookup: results[class1_name][class2_name] = match
const matchResults = computed(() => {
  const results = {};
  teams.value.forEach(t1 => {
    results[t1] = {};
    teams.value.forEach(t2 => {
      results[t1][t2] = null; // Initialize with null
    });
  });

  matches.value.forEach(match => {
    if (match.class1 && match.class2) {
      results[match.class1.name][match.class2.name] = match;
      results[match.class2.name][match.class1.name] = match;
    }
  });

  return results;
});

const fetchMatches = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await api.getLeagueMatches(props.sport, props.league);
    // Filter out matches that are not finished or don't have a winner yet
    matches.value = response.data.filter(m => m.is_finished && m.winner_id);
  } catch (err) {
    console.error(`Failed to fetch matches for ${props.sport} ${props.league} league:`, err);
    error.value = '試合データの読み込みに失敗しました。';
    matches.value = [];
  } finally {
    loading.value = false;
  }
};

// Function to get the result for a specific cell
const getResultForCell = (rowTeam, colTeam) => {
  if (rowTeam === colTeam) {
    return { type: 'self' };
  }

  const match = matchResults.value[rowTeam]?.[colTeam];
  if (!match) {
    return { type: 'no_match' };
  }

  const isRowTeamClass1 = match.class1.name === rowTeam;
  const winnerName = match.winner.name;
  const isWin = winnerName === rowTeam;

  let score;
  if (isSetsBased(props.sport)) {
    const score1 = match.class1_sets_won;
    const score2 = match.class2_sets_won;
    score = isRowTeamClass1 ? `${score1} - ${score2}` : `${score2} - ${score1}`;
  } else {
    const score1 = match.class1_score;
    const score2 = match.class2_score;
    score = isRowTeamClass1 ? `${score1} - ${score2}` : `${score2} - ${score1}`;
  }

  return {
    type: isWin ? 'win' : 'loss',
    symbol: isWin ? '○' : '×',
    score: score,
  };
};

onMounted(fetchMatches);
watch(() => [props.sport, props.league], fetchMatches);

</script>

<template>
  <div class="league-table-container">
    <h4>{{ league }}リーグ 星取表</h4>
    <div v-if="loading">読み込み中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="teams.length === 0" class="no-data">表示できる試合結果がありません。</div>
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th></th>
            <th v-for="team in teams" :key="team">{{ team }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rowTeam in teams" :key="rowTeam">
            <th>{{ rowTeam }}</th>
            <td v-for="colTeam in teams" :key="colTeam" :class="getResultForCell(rowTeam, colTeam).type">
              <div v-if="getResultForCell(rowTeam, colTeam).type === 'self'">-</div>
              <div v-else-if="getResultForCell(rowTeam, colTeam).type !== 'no_match'">
                <span class="symbol">{{ getResultForCell(rowTeam, colTeam).symbol }}</span>
                <span class="score">{{ getResultForCell(rowTeam, colTeam).score }}</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.league-table-container {
  margin-bottom: 20px;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 500px;
  border-collapse: collapse;
  margin-top: 10px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

th, td {
  padding: 10px 12px;
  text-align: center;
  border: 1px solid #e0e0e0;
  font-size: 0.9em;
}

thead th {
  background-color: #f4f6f8;
  color: #333;
  font-weight: 600;
}

tbody th {
  background-color: #f4f6f8;
  font-weight: 600;
  white-space: nowrap;
}

.win {
  color: #d32f2f; /* Red for win */
  font-weight: bold;
}

.loss {
  color: #1976d2; /* Blue for loss */
}

.self {
  background-color: #f0f0f0;
  color: #999;
}

.symbol {
  font-size: 1.2em;
  margin-right: 5px;
}

.score {
  font-size: 0.9em;
  white-space: nowrap;
}

.error, .no-data {
  text-align: center;
  padding: 20px;
  color: #777;
}
</style>
