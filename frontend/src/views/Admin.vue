<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '../services/api';
import TotalRanking from '../components/TotalRanking.vue'; // Import TotalRanking

const allSports = [
    'バレー',
    '男バス',
    '女バス',
    'ソフトボール',
    'サッカー',
    '卓球',
    'バドミントン',
];
const allLeagues = ['A', 'B', 'C', 'D'];

const allClasses = ref([]); // 全クラスリスト
const selectedSport = ref(allSports[0]);
const selectedLeague = ref(allLeagues[0]);

const leagueTeams = ref([]); // 選択されたリーグのチームリスト
const availableClasses = computed(() => {
    // 既にリーグに登録されているクラスを除外
    const registeredClassIds = new Set(leagueTeams.value.map(team => team.id));
    return allClasses.value.filter(cls => !registeredClassIds.has(cls.id));
});
const classesToAdd = ref([]); // リーグに追加するクラス (複数選択用)

// --- Methods ---
const fetchLeagueDetails = async () => {
    try {
        // リーグ所属チームの取得
        const teamsRes = await api.getLeagueTeams(selectedSport.value, selectedLeague.value);
        leagueTeams.value = teamsRes.data;
        classesToAdd.value = []; // 選択をリセット
    } catch (error) {
        console.error("Failed to fetch league details:", error);
        leagueTeams.value = [];
    }
};

// --- mounted ---
onMounted(async () => {
    try {
        const response = await api.getClasses();
        allClasses.value = response.data;
        await fetchLeagueDetails(); // 初期表示時にリーグ詳細を読み込む
    } catch (error) {
        console.error("Failed to fetch classes:", error);
        alert("クラスリストの取得に失敗しました。");
    }
});

// --- Watchers ---
watch([selectedSport, selectedLeague], fetchLeagueDetails);

const addTeamsToLeague = async () => {
    if (classesToAdd.value.length === 0) {
        alert("追加するクラスを選択してください。");
        return;
    }
    try {
        for (const classId of classesToAdd.value) {
            const payload = {
                sport: selectedSport.value,
                league: selectedLeague.value,
                class_id: classId
            };
            await api.addTeamToLeague(payload);
        }
        alert(`${classesToAdd.value.length}件のクラスをリーグに追加しました。`);
        await fetchLeagueDetails(); // リストを更新
    } catch (error) {
        console.error("Failed to add teams to league:", error);
        alert(`エラー: ${error.response?.data?.detail || 'クラスの追加に失敗しました。'}`);
    }
};

const removeTeamFromLeague = async (classId) => {
    if (!confirm("このクラスをリーグから削除しますか？")) return;
    try {
        const payload = {
            sport: selectedSport.value,
            league: selectedLeague.value,
            class_id: classId
        };
        await api.removeTeamFromLeague(payload);
        alert("クラスをリーグから削除しました。");
        await fetchLeagueDetails(); // リストを更新
    } catch (error) {
        console.error("Failed to remove team from league:", error);
        alert(`エラー: ${error.response?.data?.detail || 'クラスの削除に失敗しました。'}`);
    }
};

const generateLeagueMatches = async () => {
    if (!confirm("このリーグの総当たり戦の組み合わせを生成しますか？（既存の試合はスキップされます）")) return;
    try {
        const response = await api.generateLeagueMatches(selectedSport.value, selectedLeague.value);
        alert(`試合を生成しました: ${response.data.created_count}件`);
    } catch (error) {
        console.error("Failed to generate matches:", error);
        alert(`エラー: ${error.response?.data?.detail || '試合の生成に失敗しました。'}`);
    }
};

const deleteAllLeagueMatches = async () => {
    if (!confirm("警告: このリーグの全試合結果を削除します。よろしいですか？")) return;
    try {
        const response = await api.deleteLeagueMatches(selectedSport.value, selectedLeague.value);
        alert(`全試合を削除しました: ${response.data.num_deleted}件`);
    } catch (error) {
        console.error("Failed to delete all matches:", error);
        alert(`エラー: ${error.response?.data?.detail || '試合の削除に失敗しました。'}`);
    }
};

const deleteAllLeagueData = async () => {
    if (!confirm("警告: すべてのリーグの試合結果とチーム編成を削除します。この操作は元に戻せません。よろしいですか？")) return;
    try {
        const response = await api.deleteAllLeagueData();
        alert(`すべてのリーグデータを削除しました: ${response.data.num_matches_deleted}件の試合, ${response.data.num_teams_deleted}件のチーム編成`);
        await fetchLeagueDetails(); // 表示を更新
    } catch (error) {
        console.error("Failed to delete all league data:", error);
        alert(`エラー: ${error.response?.data?.detail || '全リーグデータの削除に失敗しました。'}`);
    }
};

const deleteAllScores = async () => {
    if (!confirm("警告: すべての試合結果（予選リーグと決勝トーナメント）を削除します。チーム編成は維持されます。この操作は元に戻せません。よろしいですか？")) return;
    try {
        const response = await api.deleteAllScores();
        alert(`すべての試合結果を削除しました: ${response.data.num_league_matches_deleted}件の予選リーグ試合, ${response.data.num_tournament_matches_deleted}件のトーナメント試合`);
        // No need to refetch data as this page doesn't display scores directly
    } catch (error) {
        console.error("Failed to delete all scores:", error);
        alert(`エラー: ${error.response?.data?.detail || '全試合結果の削除に失敗しました。'}`);
    }
};

// --- 既存のトーナメント・予選リーグ結果入力関連 ---
const tournamentMatches = ref([]);
const adminLeagueForm = ref({ sport: allSports[0], league: 'A' }); // 予選リーグ結果入力用
const unfinishedMatches = ref([]);

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

const isBallGame = (sport) => ['サッカー', 'バレー', '男バス', '女バス'].includes(sport);

const fetchLeagueMatches = async () => {
    try {
        const res = await api.getLeagueMatches(adminLeagueForm.value.sport, adminLeagueForm.value.league);
        unfinishedMatches.value = res.data
            .filter(m => !m.is_finished)
            .map(m => ({ ...m, score1: 0, score2: 0, sets1: 0, sets2: 0, winner_id: null }));
    } catch (err) {
        alert('対戦データの取得に失敗しました。');
    }
};

const submitLeagueResult = async (match) => {
    if (!match.winner_id) {
        alert('勝者を選択してください。');
        return;
    }
    const payload = {
        class1_score: match.score1,
        class2_score: match.score2,
        class1_sets_won: match.sets1,
        class2_sets_won: match.sets2,
        winner_id: match.winner_id,
    };
    try {
        await api.updateLeagueMatch(match.id, payload);
        alert('結果を保存しました。');
        unfinishedMatches.value = unfinishedMatches.value.filter(m => m.id !== match.id);
    } catch (err) {
        alert('結果の保存に失敗しました。');
    }
};
</script>

<template>
    <div class="admin-panel">
        <h2>管理者パネル</h2>

        <section class="card">
            <h3>リーグ管理</h3>
            <div class="form-group">
                <label for="admin-sport-select">種目:</label>
                <select id="admin-sport-select" v-model="selectedSport">
                    <option v-for="s in allSports" :key="s" :value="s">{{ s }}</option>
                </select>
            </div>
            <div class="form-group">
                <label for="admin-league-select">リーグ:</label>
                <select id="admin-league-select" v-model="selectedLeague">
                    <option v-for="l in allLeagues" :key="l" :value="l">{{ l }}リーグ</option>
                </select>
            </div>

            <h4>所属チーム</h4>
            <div v-if="leagueTeams.length === 0">このリーグにはまだチームが登録されていません。</div>
            <ul v-else class="team-list">
                <li v-for="team in leagueTeams" :key="team.id">
                    {{ team.name }}
                    <button @click="removeTeamFromLeague(team.id)" class="remove-btn">削除</button>
                </li>
            </ul>

            <div class="form-group">
                <label>クラスを追加 (複数選択可):</label>
                <div class="checkbox-group">
                    <div v-for="cls in availableClasses" :key="cls.id" class="checkbox-item">
                        <input type="checkbox" :id="'class-' + cls.id" :value="cls.id" v-model="classesToAdd" />
                        <label :for="'class-' + cls.id">{{ cls.name }}</label>
                    </div>
                </div>
                <button @click="addTeamsToLeague" :disabled="classesToAdd.length === 0">選択したクラスを追加</button>
            </div>

            <div class="form-actions-group">
                <button @click="generateLeagueMatches">総当たり戦を生成</button>
                <button @click="deleteAllLeagueMatches" class="delete-btn">このリーグの全試合を削除</button>
            </div>
        </section>

        <section class="card">
            <h3>全体管理</h3>
            <p>すべてのリーグの試合結果とチーム編成を一括で削除します。この操作は元に戻せません。</p>
            <button @click="deleteAllLeagueData" class="delete-btn">すべてのリーグデータを削除</button>
            <p style="margin-top: 20px;">すべての試合結果（予選、トーナメント）のみを削除します。チーム編成は維持されます。</p>
            <button @click="deleteAllScores" class="delete-btn">試合結果のみを全削除</button>
        </section>

        <section class="card">
            <h3>決勝トーナメント生成</h3>
            <select v-model="selectedSport">
                <option v-for="s in allSports" :key="s" :value="s">{{ s }}</option>
            </select>
            <button @click="handleGenerateTournament">この種目で生成</button>
        </section>

        <section class="card">
            <h3>全クラス総合ランキング</h3>
            <TotalRanking :skipCount="0" />
        </section>

        <!--
        <section class="card">
            <h3>予選リーグ結果入力</h3>
            <div class="form-group">
                <select v-model="adminLeagueForm.sport">
                    <option v-for="s in allSports" :key="s" :value="s">{{ s }}</option>
                </select>
                <select v-model="adminLeagueForm.league">
                    <option v-for="l in allLeagues" :key="l" :value="l">{{ l }}リーグ</option>
                </select>
                <button @click="fetchLeagueMatches">このリーグの未完了の試合を表示</button>
            </div>

            <div v-for="match in unfinishedMatches" :key="match.id" class="match-input-box">
                <span>{{ match.class1.name }} vs {{ match.class2.name }}</span>
                <div v-if="isBallGame(match.sport)">
                    スコア: <input type="number" v-model="match.score1" /> - <input type="number" v-model="match.score2" />
                </div>
                <div v-else>
                    セット: <input type="number" v-model="match.sets1" /> - <input type="number" v-model="match.sets2" />
                </div>
                <select v-model="match.winner_id">
                    <option :value="null">勝者</option>
                    <option :value="match.class1.id">{{ match.class1.name }}</option>
                    <option :value="match.class2.id">{{ match.class2.name }}</option>
                </select>
                <button @click="submitLeagueResult(match)">結果を保存</button>
            </div>
        </section>

        <section class="card">
            <h3>決勝トーナメント結果入力</h3>
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
    -->
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
    margin-bottom: 15px;
}

.form-group label {
    font-weight: bold;
    margin-bottom: 5px;
}

select,
input[type="text"],
input[type="number"] {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-size: 1rem;
    width: 100%;
    box-sizing: border-box;
}

button {
    padding: 12px;
    border-radius: 8px;
    border: none;
    background-color: var(--primary-blue);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
    width: 100%;
}

button:hover {
    background-color: #0056b3;
}

.remove-btn {
    background-color: #f44336;
}

.remove-btn:hover {
    background-color: #d32f2f;
}

.delete-btn {
    background-color: #f44336;
}

.delete-btn:hover {
    background-color: #d32f2f;
}

.form-actions-group {
    display: flex;
    gap: 10px;
    margin-top: 20px;
}

.form-actions-group button {
    flex: 1;
}

.team-list {
    list-style: none;
    padding: 0;
    margin-top: 10px;
}

.team-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.team-list li:last-child {
    border-bottom: none;
}

.match-input-box {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
    padding: 15px;
    background-color: #f0f8ff;
    border-radius: 8px;
    margin-top: 15px;
}

.match-input-box input[type="number"] {
    width: 50px;
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

.checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 10px;
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 8px;
    max-height: 150px;
    overflow-y: auto;
    border: 1px solid #ccc;
}

.checkbox-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 5px;
    background-color: #fff;
    border-radius: 4px;
}

.checkbox-item input[type="checkbox"] {
    width: auto;
}

.checkbox-item label {
    font-weight: normal;
    margin-bottom: 0;
}
</style>
