<script setup>
import { defineProps } from 'vue';
import LeagueStandings from '../components/LeagueStandings.vue';
import TournamentBracket from '../components/TournamentBracket.vue';

const props = defineProps({
    sportName: String, // URLから渡される
});

const leagues = ['A', 'B', 'C', 'D'];
</script>

<template>
    <div>
        <h2>{{ sportName }}</h2>
        <div class="content-wrapper">
            <div class="leagues">
                <h3>予選リーグ</h3>
                <LeagueStandings v-for="league in leagues" :key="league" :sport="sportName" :league="league" />
            </div>
            <div class="tournament">
                <h3>決勝トーナメント</h3>
                <TournamentBracket :sport="sportName" />
            </div>
        </div>
    </div>
</template>

<style scoped>
.content-wrapper {
    display: flex;
    gap: 30px;
}

.leagues {
    flex: 1;
}

.tournament {
    flex: 1;
}
</style>