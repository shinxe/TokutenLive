<script setup>
import { ref, onMounted, watch } from 'vue';
import api from '../services/api';

const props = defineProps({
  sport: String,
});

const matches = ref([]);
const loading = ref(true);

const fetchTournament = async () => {
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

onMounted(fetchTournament);
watch(() => props.sport, fetchTournament);
</script>

<template>
  <div>
    <div v-if="loading">...</div>
    <ul v-else-if="matches.length > 0">
      <li v-for="match in matches" :key="match.id">
        <strong>{{ match.match_name }}</strong>:
        <span>{{ match.class1?.name || '未定' }}</span> vs
        <span>{{ match.class2?.name || '未定' }}</span>
        <span v-if="match.winner"> -> <b>勝者: {{ match.winner.name }}</b></span>
      </li>
    </ul>
    <p v-else>トーナメントが生成されていません</p>
  </div>
</template>

<style scoped>
ul {
  list-style-type: none;
  padding: 0;
}

li {
  background-color: #f9f9f9;
  border: 1px solid #eee;
  padding: 10px;
  margin-bottom: 5px;
  border-radius: 4px;
}
</style>