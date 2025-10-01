<script setup>
import { ref, computed } from 'vue';
import { defineProps } from 'vue';
import LeagueTable from '../components/LeagueTable.vue';
import TournamentBracket from '../components/TournamentBracket.vue';

const props = defineProps({
    sportName: String, // URLから渡される
});

const processedSportName = computed(() => {
    if (props.sportName === 'バスケ') {
        return '女バス';
    }
    return props.sportName;
});

const leagues = ['A', 'B', 'C', 'D'];
const isLeaguesVisible = ref(true); // New state for leagues
const isTournamentVisible = ref(true);

const toggleLeagues = () => { // New toggle function for leagues
    isLeaguesVisible.value = !isLeaguesVisible.value;
};

const toggleTournament = () => {
    isTournamentVisible.value = !isTournamentVisible.value;
};
</script>

<template>
    <div class="sport-detail-container">
        <header class="sport-header">
            <h1>{{ sportName }}</h1>
        </header>
        <div class="content-wrapper">
            <section class="leagues card">
                <div class="leagues-header"> <!-- New header div for leagues -->
                    <h2>予選リーグ</h2>
                    <button @click="toggleLeagues" class="toggle-button">
                        {{ isLeaguesVisible ? '隠す' : '表示する' }}
                    </button>
                </div>
                <div v-if="isLeaguesVisible"> <!-- Wrap content with v-if -->
                    <div v-for="league in leagues" :key="league" class="league-section">
                        <LeagueTable :sport="processedSportName" :league="league" />
                    </div>
                </div>
            </section>
            <section class="tournament card">
                <div class="tournament-header">
                    <h2>決勝トーナメント</h2>
                    <button @click="toggleTournament" class="toggle-button">
                        {{ isTournamentVisible ? '隠す' : '表示する' }}
                    </button>
                </div>
                <TournamentBracket v-if="isTournamentVisible" :sport="processedSportName" />
            </section>
        </div>
    </div>
</template>

<style scoped>
.sport-detail-container {
    min-height: 100vh;
    padding: 2rem 1rem;
    /* Background and color are now handled by body style in main.css */
}

.sport-header {
    text-align: center;
    margin-bottom: 2rem;
}

.sport-header h1 {
    font-size: 1.6rem;
    font-weight: bold;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    /* Softer shadow for light theme */
}

.content-wrapper {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}

.card {
    background: var(--color-card-background);
    border-radius: 15px;
    padding: 1.5rem;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid var(--color-border);
    box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.1);
    min-width: 0;
    /* Crucial fix for grid item overflow */
}

.card h2 {
    font-size: 1.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--color-border);
    text-align: center;
}

.leagues.card h2 {
    margin-bottom: 1.5rem;
}

.tournament-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.tournament-header h2 {
    margin-bottom: 0;
    border-bottom: none;
}

.toggle-button {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    font-weight: bold;
    color: var(--color-text);
    background-color: var(--color-background-mute);
    border: 1px solid var(--color-border);
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.toggle-button:hover {
    background-color: var(--color-background-soft);
}

.league-section:not(:last-child) {
    margin-bottom: 2rem;
}

/* New styles for leagues header */
.leagues-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.leagues-header h2 {
    margin-bottom: 0;
    border-bottom: none;
}

/* Desktop Styles */
@media (min-width: 768px) {
    .sport-detail-container {
        padding: 3rem;
    }

    .content-wrapper {
        grid-template-columns: 1fr 1fr;
    }

    .sport-header h1 {
        font-size: 3.5rem;
    }
}
</style>
