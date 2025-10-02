<script setup>
import { ref, onMounted, watch, computed, onUnmounted, nextTick } from 'vue';
import api from '../services/api';
import MatchEditForm from './MatchEditForm.vue';
import { auth } from '../services/auth';

const props = defineProps({
  sport: String,
  league: String,
});

const matches = ref([]);
const standings = ref([]);
const loading = ref(true);
const error = ref(null);
const editingMatch = ref(null);
const tableContainerRef = ref(null);

const isSetsBased = (sportName) => {
  return ['卓球', 'バドミントン'].includes(sportName);
};

const fetchLeagueData = async () => {
  if (editingMatch.value) return;
  loading.value = true;
  error.value = null;
  try {
    const [matchesResponse, standingsResponse] = await Promise.all([
      api.getLeagueMatches(props.sport, props.league),
      api.getLeagueStandings(props.sport, props.league)
    ]);
    matches.value = matchesResponse.data;
    standings.value = standingsResponse.data;
  } catch (err) {
    console.error(`Failed to fetch league data for ${props.sport} ${props.league}:`, err);
    error.value = 'リーグデータの読み込みに失敗しました。';
    matches.value = [];
    standings.value = [];
  } finally {
    loading.value = false;
  }
};

const displayStandings = computed(() => standings.value);

const getCellInfo = (rowTeam, colTeam) => {
  if (rowTeam === colTeam) return { type: 'self' };
  const match = matches.value.find(m =>
    (m.class1.name === rowTeam && m.class2.name === colTeam) ||
    (m.class1.name === colTeam && m.class2.name === rowTeam)
  );
  if (!match) return { type: 'no_match' };

  if (editingMatch.value && editingMatch.value.id === match.id) return { type: 'editing', match };
  if (!match.is_finished) return { type: 'not_finished', match };

  const isRowTeamClass1 = match.class1.name === rowTeam;
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

  // Handle tie
  if (!match.winner) {
    return { type: 'finished', match, result: 'tie', symbol: '△', score };
  }

  const isWin = match.winner.name === rowTeam;
  return { type: 'finished', match, result: isWin ? 'win' : 'loss', symbol: isWin ? '○' : '×', score };
};

const handleCellClick = (cellInfo) => {
  // ログインしていない場合
  if (!auth.state.isLoggedIn) {
    if (cellInfo.type === 'not_finished' || cellInfo.type === 'finished') {
      alert('編集にはログインが必要です');
    }
    return;
  }

  // ログインしている場合
  if ((cellInfo.type === 'not_finished' || cellInfo.type === 'finished') && cellInfo.match) {
    editingMatch.value = cellInfo.match;
  }
};

const handleSave = async (matchData) => {
  if (!editingMatch.value) return;
  try {
    await api.updateLeagueMatch(editingMatch.value.id, matchData);
    editingMatch.value = null;
    await fetchLeagueData();
  } catch (err) {
    console.error('Failed to update match:', err);
    alert('試合結果の更新に失敗しました。');
  }
};

const handleCancel = () => { editingMatch.value = null; };

// 外側クリックのハンドラ
const handleClickOutside = (event) => {
  if (editingMatch.value && tableContainerRef.value && !tableContainerRef.value.contains(event.target)) {
    editingMatch.value = null;
  }
};

watch(editingMatch, (newMatch) => {
  if (newMatch) {
    nextTick(() => {
      document.addEventListener('click', handleClickOutside, true);
    });
  } else {
    document.removeEventListener('click', handleClickOutside, true);
  }
});

onMounted(() => {
  fetchLeagueData();
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside, true);
});

watch(() => [props.sport, props.league], fetchLeagueData);

</script>

<template>
  <div class="league-table-container" ref="tableContainerRef">
    <h4 class="league-name">{{ league }}リーグ</h4>
    <div v-if="loading" class="status-message">読み込み中...</div>
    <div v-else-if="error" class="status-message error">{{ error }}</div>
    <div v-else-if="displayStandings.length === 0" class="status-message no-data">このリーグにチームが登録されていません。</div>
    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th class="sticky-col"></th>
            <th v-for="team in displayStandings.map(s => s.class_name)" :key="team">{{ team }}</th>
            <th>勝</th>
            <th>敗</th>
            <th>分</th>
            <th>順位</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rowTeam in displayStandings.map(s => s.class_name)" :key="rowTeam">
            <th class="sticky-col">
              <div class="team-name-in-cell">{{ rowTeam }}</div>
              <div class="rank-in-cell">{{displayStandings.find(s => s.class_name === rowTeam)?.rank}}位</div>
            </th>
            <td v-for="colTeam in displayStandings.map(s => s.class_name)" :key="colTeam"
              @click="handleCellClick(getCellInfo(rowTeam, colTeam))"
              :class="[getCellInfo(rowTeam, colTeam).result, { 'is-clickable': auth.state.isLoggedIn }]">
              <div v-if="getCellInfo(rowTeam, colTeam).type === 'self'" class="self-wrapper">
                <div class="self">-</div>
              </div>
              <MatchEditForm v-else-if="getCellInfo(rowTeam, colTeam).type === 'editing'"
                :match="getCellInfo(rowTeam, colTeam).match" :sport="props.sport" @save="handleSave"
                @cancel="handleCancel" />
              <div v-else-if="getCellInfo(rowTeam, colTeam).type === 'finished'" class="cell-content">
                <span class="symbol">{{ getCellInfo(rowTeam, colTeam).symbol }}</span>
                <span class="score">{{ getCellInfo(rowTeam, colTeam).score }}</span>
              </div>
              <div v-else-if="getCellInfo(rowTeam, colTeam).type === 'not_finished'" class="not-finished cell-content">
                <span class="score">0 - 0</span>
              </div>
              <div v-else-if="getCellInfo(rowTeam, colTeam).type === 'no_match'" class="no-match"></div>
            </td>
            <td class="standings-data">{{displayStandings.find(s => s.class_name === rowTeam)?.wins ?? '-'}}</td>
            <td class="standings-data">{{displayStandings.find(s => s.class_name === rowTeam)?.losses ?? '-'}}</td>
            <td class="standings-data">{{displayStandings.find(s => s.class_name === rowTeam)?.ties ?? '-'}}</td>
            <td class="standings-data rank">{{displayStandings.find(s => s.class_name === rowTeam)?.rank ?? '-'}}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.league-table-container {
  margin-left: -15px;
  margin-right: -15px;
}

@media (min-width: 769px) {
  .league-table-container {
    margin-left: 0;
    margin-right: 0;
  }
}

.league-name {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: var(--color-heading);
}

.status-message {
  text-align: center;
  padding: 20px;
  color: var(--color-text);
}

.error {
  color: var(--color-loss-symbol);
}

.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  position: relative;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-card-background);
}

table {
  width: 100%;
  min-width: 420px;
  border-collapse: collapse;
  color: var(--color-text);
  border-spacing: 0;
}

th,
td {
  padding: 4px;
  text-align: center;
  border-left: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  height: 52px;
  width: 65px;
  vertical-align: middle;
  white-space: nowrap;
  transition: background-color 0.3s;
  font-size: 0.8rem;
}

table thead th {
  border-top: 0;
}

table tr th:first-child,
table tr td:first-child {
  border-left: 0;
}

table tbody tr:last-child th,
table tbody tr:last-child td {
  border-bottom: 0;
}

thead th {
  background-color: rgba(0, 0, 0, 0.08);
  color: var(--color-heading);
  font-weight: 600;
}

tbody th.sticky-col {
  font-weight: 600;
  text-align: center;
  /* Center the flex content */
  line-height: 1.2;
  padding: 2px 4px;
}

.sticky-col {
  position: -webkit-sticky;
  position: sticky;
  left: 0;
  background-color: #f8fafc;
  /* Solid light gray */
  z-index: 1;
  border-right: 1px solid var(--color-border);
}

thead .sticky-col {
  z-index: 2;
}

.team-name-in-cell {
  font-size: 0.8rem;
  font-weight: 600;
}

.rank-in-cell {
  font-size: 0.7rem;
  color: var(--color-text);
  opacity: 0.8;
}

td {
  cursor: default;
}

.cell-content,
.self-wrapper,
.no-match,
.not-finished {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  line-height: 1.1;
}

.win {
  background-color: rgba(40, 167, 69, 0.2);
}

.loss {
  background-color: rgba(220, 53, 69, 0.15);
}

.tie {
  background-color: rgba(108, 117, 125, 0.2);
}

.win .symbol,
.loss .symbol {
  font-weight: bold;
}

.win .symbol {
  color: var(--color-win-symbol);
}

.loss .symbol {
  color: var(--color-loss-symbol);
}

.tie .symbol {
  color: var(--color-text);
}

.self-wrapper {
  cursor: default;
}

.self {
  background-color: rgba(0, 0, 0, 0.08);
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.no-match,
.not-finished {
  cursor: default;
}

.not-finished {
  color: var(--color-text);
  opacity: 0.6;
}

.symbol {
  font-size: 1.2em;
}

.score {
  font-size: 0.85em;
  margin-top: 1px;
}

.match-number {
  font-size: 0.85em;
  margin-top: 2px;
}

.standings-data {
  cursor: default;
  background-color: rgba(0, 0, 0, 0.05);
  font-weight: bold;
}

.standings-data.rank {
  font-size: 1.1em;
}

/* Mobile-specific optimizations */
@media (max-width: 768px) {

  th,
  td {
    height: 48px;
    width: 52px;
    min-width: 52px;
    font-size: 0.75rem;
  }

  .team-name-in-cell {
    font-size: 0.7rem;
  }

  .rank-in-cell {
    font-size: 0.65rem;
  }

  .symbol {
    font-size: 1.1em;
  }

  .score {
    font-size: 0.75em;
  }

  .standings-data.rank {
    font-size: 1em;
  }
}
</style>