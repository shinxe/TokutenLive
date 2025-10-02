<script setup>
import { ref, onMounted } from 'vue';

const props = defineProps({
  match: {
    type: Object,
    required: true,
  },
  sport: {
    type: String,
    required: true,
  }
});

const emit = defineEmits(['save', 'cancel']);

const isSetsBased = ['卓球', 'バドミントン'].includes(props.sport);

// Form state
const score1 = ref(0);
const score2 = ref(0);

onMounted(() => {
  // Initialize form with existing scores if they exist
  if (isSetsBased) {
    score1.value = props.match.class1_sets_won || 0;
    score2.value = props.match.class2_sets_won || 0;
  } else {
    score1.value = props.match.class1_score || 0;
    score2.value = props.match.class2_score || 0;
  }
});

const handleSave = () => {
  let winnerId = null;
  if (score1.value > score2.value) {
    winnerId = props.match.class1.id;
  } else if (score2.value > score1.value) {
    winnerId = props.match.class2.id;
  }

  const matchData = {
    class1_score: isSetsBased ? 0 : score1.value,
    class2_score: isSetsBased ? 0 : score2.value,
    class1_sets_won: isSetsBased ? score1.value : 0,
    class2_sets_won: isSetsBased ? score2.value : 0,
    winner_id: winnerId,
  };

  emit('save', matchData);
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<template>
  <div class="edit-form">
    <div class="form-inputs">
      <div class="team-input">
        <label :for="`score1-${match.id}`">{{ match.class1.name }}</label>
        <input type="number" v-model.number="score1" :id="`score1-${match.id}`" min="0">
      </div>
      <span class="separator">-</span>
      <div class="team-input">
        <input type="number" v-model.number="score2" :id="`score2-${match.id}`" min="0">
        <label :for="`score2-${match.id}`">{{ match.class2.name }}</label>
      </div>
    </div>
    <div class="form-actions">
      <button @click="handleSave" class="save-btn">保存</button>
      <button @click="handleCancel" class="cancel-btn">取消</button>
    </div>
  </div>
</template>

<style scoped>
.edit-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 5px;
  background-color: #f9f9f9;
  border-radius: 6px;
}

.form-inputs {
  display: flex;
  align-items: center;
  gap: 5px;
}

.team-input {
  display: flex;
  align-items: center;
  gap: 5px;
}

.team-input label {
  font-weight: bold;
  font-size: 0.9em;
}

.team-input input {
  width: 45px;
  padding: 4px;
  text-align: center;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.separator {
  font-weight: bold;
}

.form-actions {
  display: flex;
  gap: 10px;
}

button {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85em;
}

.save-btn {
  background-color: #4CAF50;
  color: white;
}

.cancel-btn {
  background-color: #f44336;
  color: white;
}
</style>
