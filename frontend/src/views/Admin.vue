<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../services/api';

const allSports = ['サッカー', 'バレー', 'バスケ', 'バドミントン', '卓球'];
const leagues = ['A', 'B', 'C', 'D'];
const ballGames = ['サッカー', 'バレー', 'バスケ'];

const allClasses = ref([]);
const selectedSport = ref(allSports[0]);
const tournamentMatches = ref([]);

// --- フォーム用のデータ ---
const leagueForm = ref({
    sport: allSports[0],
    league: 'A',
    class1_id: null,
    class2_id: null,
    class1_score: 0,
    class2_score: 0,
    class1_sets_won: 0,
    class2_sets_won: 0,
    winner_id: null,
});

// --- mounted ---
onMounted(async () => {
    const response = await api.getClasses();
    allClasses.value = response.data;
});

// --- Methods ---
const handleGenerateTournament = async () => {
    if (!confirm(`${selectedSport.value}のトーナメントを生成しますか？`)) return;
    try {
        await api.generateTournament(selectedSport.value);
        alert('トーナメントを生成しました。');
        fetchTournamentMatches();
    } catch (error) {
        alert(`エラー: ${error.response?.data?.detail || 'トーナメントの生成に失敗しました。'}`);
    }
};

const handleLeagueSubmit = async () => {
    try {
        await api.createLeagueMatch(leagueForm.value);
        alert('予選リーグの結果を登録しました。');
        // フォームをリセット (任意)
        Object.assign(leagueForm.value, { class1_id: null, class2_id: null, winner_id: null });
    } catch (error) {
        alert('エラー: 結果の登録に失敗しました。');
    }
};

const fetchTournamentMatches = async () => {
    try {
        const res = await api.getTournament(selectedSport.value);
        tournamentMatches.value = res.data.filter(m => !m.winner && m.class1 && m.class2);
    } catch {
        tournamentMatches.value = [];
    }
};

const handleTournamentSubmit = async (match, winnerId) => {
    try {
        await api.updateTournamentMatch(selectedSport.value, match.id, winnerId);
        alert('トーナメント結果を更新しました。');
        fetchTournamentMatches(); // リストを更新
    } catch {
        alert('エラー: 結果の更新に失敗しました。');
    }
};

const isBallGame = computed(() => ballGames.includes(leagueForm.value.sport));
</script>

<template>
    <div class="admin-panel">
        <h2>管理者パネル</h2>

        <section class="card">
            <h3>1. 決勝トーナメント生成</h3>
            <select v-model="selectedSport">
                <option v-for="s in allSports" :key="s" :value="s">{{ s }}</option>
            </select>
            <button @click="handleGenerateTournament">この種目で生成</button>
        </section>

        <section class="card">
            <h3>2. 予選リーグ結果入力</h3>
            <form @submit.prevent="handleLeagueSubmit">
                <select v-model="leagueForm.sport">
                    <option v-for="s in allSports" :key="s" :value="s">{{ s }}</option>
                </select>
                <select v-model="leagueForm.league">
                    <option v-for="l in leagues" :key="l" :value="l">{{ l }}リーグ</option>
                </select>
                <select v-model="leagueForm.class1_id" required>
                    <option :value="null">クラス1</option>
                    <option v-for="c in allClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>
                vs
                <select v-model="leagueForm.class2_id" required>
                    <option :value="null">クラス2</option>
                    <option v-for="c in allClasses" :key="c.id" :value="c.id">{{ c.name }}</option>
                </select>

                <div v-if="isBallGame">
                    スコア: <input type="number" v-model="leagueForm.class1_score" /> - <input type="number"
                        v-model="leagueForm.class2_score" />
                </div>
                <div v-else>
                    セット数: <input type="number" v-model="leagueForm.class1_sets_won" /> - <input type="number"
                        v-model="leagueForm.class2_sets_won" />
                </div>

                <select v-model="leagueForm.winner_id" required>
                    <option :value="null">勝者を選択</option>
                    <option v-if="leagueForm.class1_id" :value="leagueForm.class1_id">{{allClasses.find(c => c.id ===
                        leagueForm.class1_id)?.name }}</option>
                    <option v-if="leagueForm.class2_id" :value="leagueForm.class2_id">{{allClasses.find(c => c.id ===
                        leagueForm.class2_id)?.name }}</option>
                </select>

                <button type="submit">予選結果を登録</button>
            </form>
        </section>

        <section class="card">
            <h3>3. 決勝トーナメント結果入力</h3>
            <select v-model="selectedSport" @change="fetchTournamentMatches">
                <option v-for="s in allSports" :key="s" :value="s">{{ s }}</option>
            </select>
            <button @click="fetchTournamentMatches">未完了の試合を検索</button>
            <ul>
                <li v-for="match in tournamentMatches" :key="match.id">
                    {{ match.match_name }}: {{ match.class1.name }} vs {{ match.class2.name }}
                    <button @click="handleTournamentSubmit(match, match.class1.id)">{{ match.class1.name }}の勝ち</button>
                    <button @click="handleTournamentSubmit(match, match.class2.id)">{{ match.class2.name }}の勝ち</button>
                </li>
            </ul>
            <p v-if="tournamentMatches.length === 0">未完了の試合はありません。</p>
        </section>
    </div>
</template>

<style scoped>
.admin-panel {
    display: flex;
    flex-direction: column;
    gap: 25px;
}

.card {
    background: var(--card-background);
    padding: 20px;
    border-radius: 12px;
    box-shadow: var(--shadow);
}

.card h3 {
    margin-top: 0;
    color: var(--primary-blue);
    border-bottom: 2px solid var(--light-blue);
    padding-bottom: 10px;
}

/* フォームの共通スタイル */
.form-group {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

select,
input,
button {
    padding: 12px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 1rem;
    width: 100%;
    box-sizing: border-box;
    /* paddingを含めてwidth:100%にする */
}

button {
    background-color: var(--primary-blue);
    color: white;
    font-weight: bold;
    border: none;
    cursor: pointer;
    transition: background-color 0.2s;
}

button:hover {
    background-color: #0056b3;
}

/* トーナメント結果入力リスト */
ul {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

li {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 15px;
    background: #f0f8ff;
    border-radius: 8px;
}

/* PC幅の時は横並びにする */
@media (min-width: 768px) {
    li {
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
    }
}
</style>