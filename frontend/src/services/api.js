import axios from 'axios';

const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// リクエストインターセプターを追加
apiClient.interceptors.request.use(config => {
    // sessionStorageからトークンを取得
    const token = sessionStorage.getItem('authToken');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, error => {
    return Promise.reject(error);
});


export default {
    // --- Read APIs ---
    // 総合ランキングを取得
    getTotalRankings(params = {}) {
        return apiClient.get('/rankings/total/', { params });
    },

    // 全てのリーグデータを削除
    deleteAllLeagueData() {
        return apiClient.delete('/all-leagues');
    },

    // 試合結果のみを全て削除
    deleteAllScores() {
        return apiClient.delete('/scores/all');
    },
    getLeagueStandings(sport, league) {
        return apiClient.get(`/leagues/${sport}/${league}/standings/`);
    },
    getLeagueMatches(sport, league) {
        return apiClient.get(`/leagues/${sport}/${league}/matches/`);
    },
    getLeagueTeams(sport, league) {
        return apiClient.get(`/leagues/${sport}/${league}/teams/`);
    },
    getTournament(sport) {
        return apiClient.get(`/tournaments/${sport}/`);
    },
    getClasses() {
        return apiClient.get('/classes/');
    },

    // --- Writing ---
    createClass(className) { // 新しくクラス作成APIを追加
        return apiClient.post('/classes/', { name: className });
    },
    createLeagueMatch(matchData) {
        return apiClient.post('/league_matches/', matchData);
    },
    generateTournament(sport) {
        return apiClient.post(`/tournaments/${sport}/generate/`);
    },
    updateTournamentMatch(sport, matchId, matchData) {
        return apiClient.put(`/tournaments/${sport}/matches/${matchId}/`, matchData);
    },
    updateLeagueMatch(matchId, matchData) {
        return apiClient.put(`/leagues/matches/${matchId}/`, matchData);
    },
    deleteLeagueMatches(sport, league) {
        return apiClient.delete(`/leagues/${sport}/${league}/matches/`);
    },
    removeTeamFromLeague(teamData) { // teamData = { sport, league, class_id }
        return apiClient.delete(`/leagues/teams/`, { data: teamData });
    },
    addTeamToLeague(teamData) { // teamData = { sport, league, class_id }
        return apiClient.post(`/leagues/teams/`, teamData);
    },
    generateLeagueMatches(sport, league) {
        return apiClient.post(`/leagues/${sport}/${league}/generate_matches/`);
    },
};