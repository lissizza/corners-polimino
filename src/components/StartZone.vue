<!-- src/components/StartZone.vue -->
<template>
  <g>
    <text x="0" y="-10" font-size="16" fill="#333">Стартовая Зона</text>
    <PuzzlePiece
      v-for="piece in pieces"
      :key="piece.id"
      :piece="piece"
      :gridSize="gridSize"
      @update-piece="handleUpdatePiece($event)"
    />
  </g>
</template>

<script>
import PuzzlePiece from './PuzzlePiece.vue';

export default {
  name: 'StartZone',
  components: {
    PuzzlePiece,
  },
  props: {
    pieces: {
      type: Array,
      required: true,
    },
  },
  emits: ['update-piece'],
  setup(props, { emit }) {
    const gridSize = 30; // Размер ячейки

    // Функция обработки события обновления фигурки
    const handleUpdatePiece = (updatedPiece) => {
      // Устанавливаем зону как 'start'
      emit('update-piece', { ...updatedPiece, zone: 'start' });
    };

    return {
      gridSize,
      handleUpdatePiece,
    };
  },
};
</script>

<style scoped>
/* Добавьте необходимые стили, если нужно */
</style>
