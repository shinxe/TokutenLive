import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://127.0.0.1:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default {
    // --- Read APIs ---
    getTotalRankings() {
        return apiClient.get('/rankings/total/');
    },
    getLeagueStandings(sport, league) {
        return apiClient.get(`/leagues/${sport}/${league}/standings/`);
    },
    getTournament(sport) {
        return apiClient.get(`/tournaments/${sport}/`);
    },
    getClasses() {
        return apiClient.get('/classes/');
    },

    // --- Writing ---
    createLeagueMatch(matchData) {
        return apiClient.post('/league_matches/', matchData);
    },
    generateTournament(sport) {
        return apiClient.post(`/tournaments/${sport}/generate/`);
    },
    updateTournamentMatch(sport, matchId, winnerId) {
        return apiClient.put(`/tournaments/${sport}/matches/${matchId}/`, { winner_id: winnerId });
    },
};