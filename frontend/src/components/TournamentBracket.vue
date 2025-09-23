<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '../services/api';
import MatchEditForm from './MatchEditForm.vue';

const props = defineProps({
  sport: String,
});

const matches = ref([]);
const loading = ref(true);
const editingMatch = ref(null);

const fetchTournament = async () => {
  if (editingMatch.value) return;
  loading.value = true;
  try {
    const response = await api.getTournament(props.sport);
    matches.value = response.data;
  } catch (err) {
    matches.value = [];
  } finally {
    loading.value = false;
  }
};

const firstRound = computed(() =>
  matches.value
    .filter(m => m.match_name.includes('1回戦'))
    .sort((a, b) => a.id - b.id)
);

const semiFinals = computed(() =>
  matches.value
    .filter(m => m.match_name.includes('準決勝'))
    .sort((a, b) => a.id - b.id)
);

const final = computed(() =>
  matches.value.find(m => m.match_name.includes('決勝') && !m.match_name.includes('準'))
);

const thirdPlace = computed(() =>
  matches.value.find(m => m.match_name.includes('3位決定戦'))
);

const champion = computed(() => final.value?.winner);

const isRacketSport = computed(() => firstRound.value.length > 0);
const isSetsBased = computed(() => ['卓球', 'バドミントン'].includes(props.sport));

const handleMatchClick = (match) => {
  if (!match) return;
  if (match.class1 && match.class2) { // is_finishedのチェックを削除
    // Create a deep copy to prevent reactivity issues
    editingMatch.value = JSON.parse(JSON.stringify(match));
  }
};

const handleSave = async (matchData) => {
  if (!editingMatch.value) return;
  try {
    await api.updateTournamentMatch(props.sport, editingMatch.value.id, matchData);
    editingMatch.value = null;
    await fetchTournament();
  } catch (err) {
    console.error('Failed to update match:', err);
    alert('試合結果の更新に失敗しました。');
  }
};

const handleCancel = () => {
  editingMatch.value = null;
};

onMounted(fetchTournament);
watch(() => props.sport, fetchTournament);
</script>

<template>
  <div class="bracket-container">
    <div v-if="loading" class="status-message">...</div>
    <div v-else-if="matches.length > 0" class="bracket-wrapper">
      <div class="bracket">
        <div v-if="isRacketSport" class="round first-round">
           <div class="match-item" v-for="match in firstRound" :key="match.id" @click="handleMatchClick(match)">
            <div class="match-name">{{ match.match_name }}</div>
            <MatchEditForm v-if="editingMatch && editingMatch.id === match.id" :match="editingMatch"
              :sport="props.sport" @save="handleSave" @cancel="handleCancel" />
            <div v-else class="match-content">
              <div class="team" :class="{ winner: match.winner?.id === match.class1?.id }"><span>{{ match.class1?.name
                  || '未定' }}</span><span class="score">{{ isSetsBased ? match.class1_sets_won : match.class1_score ?? '' }}</span></div>
              <div class="team" :class="{ winner: match.winner?.id === match.class2?.id }"><span>{{ match.class2?.name
                  || '未定' }}</span><span class="score">{{ isSetsBased ? match.class2_sets_won : match.class2_score ?? '' }}</span></div>
            </div>
          </div>
        </div>

        <div class="round semifinals">
          <div class="match-item" v-for="match in semiFinals" :key="match.id" @click="handleMatchClick(match)">
            <div class="match-name">{{ match.match_name }}</div>
            <MatchEditForm v-if="editingMatch && editingMatch.id === match.id" :match="editingMatch"
              :sport="props.sport" @save="handleSave" @cancel="handleCancel" />
            <div v-else class="match-content">
              <div class="team" :class="{ winner: match.winner?.id === match.class1?.id }"><span>{{ match.class1?.name
                  || '未定' }}</span><span class="score">{{ isSetsBased ? match.class1_sets_won : match.class1_score ?? '' }}</span></div>
              <div class="team" :class="{ winner: match.winner?.id === match.class2?.id }"><span>{{ match.class2?.name
                  || '未定' }}</span><span class="score">{{ isSetsBased ? match.class2_sets_won : match.class2_score ?? '' }}</span></div>
            </div>
          </div>
        </div>

        <div class="round finals">
          <div class="match-item" v-if="final" @click="handleMatchClick(final)">
            <div class="match-name">決勝</div>
            <MatchEditForm v-if="editingMatch && editingMatch.id === final.id" :match="editingMatch"
              :sport="props.sport" @save="handleSave" @cancel="handleCancel" />
            <div v-else class="match-content">
              <div class="team" :class="{ winner: final.winner?.id === final.class1?.id }"><span>{{ final.class1?.name
                  || '未定' }}</span><span class="score">{{ isSetsBased ? final.class1_sets_won : final.class1_score ?? '' }}</span></div>
              <div class="team" :class="{ winner: final.winner?.id === final.class2?.id }"><span>{{ final.class2?.name
                  || '未定' }}</span><span class="score">{{ isSetsBased ? final.class2_sets_won : final.class2_score ?? '' }}</span></div>
            </div>
          </div>
        </div>

        <div class="round champion" v-if="champion">
          <div class="champion-box">
            🏆 優勝 🏆
            <span>{{ champion.name }}</span>
          </div>
        </div>
      </div>

      <div class="third-place-bracket" v-if="thirdPlace">
        <div class="match-item" @click="handleMatchClick(thirdPlace)">
          <div class="match-name">3位決定戦</div>
          <MatchEditForm v-if="editingMatch && editingMatch.id === thirdPlace.id" :match="editingMatch"
            :sport="props.sport" @save="handleSave" @cancel="handleCancel" />
          <div v-else class="match-content">
            <div class="team" :class="{ winner: thirdPlace.winner?.id === thirdPlace.class1?.id }"><span>{{
              thirdPlace.class1?.name || '未定' }}</span><span class="score">{{ isSetsBased ? thirdPlace.class1_sets_won : thirdPlace.class1_score ?? '' }}</span>
            </div>
            <div class="team" :class="{ winner: thirdPlace.winner?.id === thirdPlace.class2?.id }"><span>{{
              thirdPlace.class2?.name || '未定' }}</span><span class="score">{{ isSetsBased ? thirdPlace.class2_sets_won : thirdPlace.class2_score ?? '' }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>
    <p v-else class="status-message">対象のトーナメント試合がありません</p>
  </div>
</template>

<style scoped>
.bracket-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3rem;
  padding: 1rem 0;
  overflow-x: auto;
}

.bracket {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 2rem;
}

.round {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.first-round {
  justify-content: space-around;
  gap: 2.5rem;
}

.semifinals {
  justify-content: space-around;
  gap: 10.5rem;
}

.finals {
  justify-content: center;
}

.match-item {
  width: 220px;
  flex-shrink: 0;
  cursor: pointer;
  position: relative;
}

.match-name {
  font-size: 0.8rem;
  font-weight: bold;
  color: var(--color-text);
  text-align: center;
  margin-bottom: 0.5rem;
}

.match-content {
  background-color: rgba(255, 255, 255, 0.6);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.match-item:hover .match-content {
  background-color: rgba(255, 255, 255, 0.8);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.team {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  font-size: 1rem;
  color: var(--color-text);
}

.team:first-child {
  border-bottom: 1px solid var(--color-border);
}

.winner {
  font-weight: bold;
  color: var(--color-winner);
}

.winner .score {
  color: var(--color-winner);
}

.score {
  font-weight: bold;
  min-width: 25px;
  text-align: right;
}

/* --- Connectors --- */
.first-round .match-item::after,
.semifinals .match-item::after,
.finals .match-item::after {
  content: '';
  position: absolute;
  top: 50%;
  right: -1rem;
  width: 1rem;
  height: 2px;
  background: #c7d2fe;
}

.semifinals .match-item::before,
.finals .match-item::before {
  content: '';
  position: absolute;
  left: -1rem;
  width: 1rem;
  height: 2px;
  background: #c7d2fe;
  top: 50%;
}

/* Vertical bars */
.first-round .match-item:nth-child(odd)::after {
  height: calc(50% + 2.25rem);
  top: -2.25rem;
  border-top: 2px solid #c7d2fe;
  border-right: 2px solid #c7d2fe;
  border-top-right-radius: 5px;
}
.first-round .match-item:nth-child(even)::after {
  height: calc(50% + 2.25rem);
  top: 50%;
  border-bottom: 2px solid #c7d2fe;
  border-right: 2px solid #c7d2fe;
  border-bottom-right-radius: 5px;
}

.semifinals .match-item:nth-child(odd)::before {
    height: calc(100% + 2.5rem);
    top: -2.5rem;
    border-top: 2px solid #c7d2fe;
    border-left: 2px solid #c7d2fe;
    border-top-left-radius: 5px;
}
.semifinals .match-item:nth-child(even)::before {
    height: calc(100% + 2.5rem);
    bottom: -2.5rem;
    top: auto;
    border-bottom: 2px solid #c7d2fe;
    border-left: 2px solid #c7d2fe;
    border-bottom-left-radius: 5px;
}

.finals .match-item::before {
    height: calc(100% + 10.5rem);
    top: -5.25rem;
    border-top: 2px solid #c7d2fe;
    border-bottom: 2px solid #c7d2fe;
    border-left: 2px solid #c7d2fe;
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
}


/* Champion Box */
.champion-box {
  font-size: 1.2em;
  font-weight: bold;
  color: var(--color-heading);
  padding: 1rem 1.5rem;
  border: 2px solid var(--color-winner);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.third-place-bracket {
  border-top: 2px dashed #c7d2fe;
  padding-top: 2rem;
  margin-top: 1rem;
}

.status-message {
  text-align: center;
  padding: 20px;
}

/* Mobile Styles */
@media (max-width: 1024px) {
  .bracket {
    flex-direction: column;
    gap: 1rem;
  }

  .semifinals, .first-round {
    gap: 2rem;
  }

  .match-item::after, .match-item::before {
    display: none;
  }

  .round::before {
    content: '▼';
    color: var(--color-text);
    text-align: center;
    margin: 0.5rem 0;
  }
  .first-round::before {
    content: '1回戦';
    font-weight: bold;
  }
  .semifinals::before {
    content: '準決勝';
    font-weight: bold;
  }
  .finals::before {
    content: '決勝';
    font-weight: bold;
  }
  .round:first-child::before {
    display: none;
  }
}
</style>
