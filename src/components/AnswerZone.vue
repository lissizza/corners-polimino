<!-- src/components/AnswerZone.vue -->
<template>
  <g>
    <text x="0" y="-10" font-size="16" fill="#333">Зона Ответа</text>
    <!-- Сетка зоны ответа (можно удалить, т.к. общая сетка уже рисуется в App.vue) -->
    <!--
    <g>
      <line
        v-for="i in rows + 1"
        :key="'h' + i"
        :x1="0"
        :y1="(i - 1) * gridSize"
        :x2="columns * gridSize"
        :y2="(i - 1) * gridSize"
        stroke="#ccc"
      />
      <line
        v-for="i in columns + 1"
        :key="'v' + i"
        :x1="(i - 1) * gridSize"
        :y1="0"
        :x2="(i - 1) * gridSize"
        :y2="rows * gridSize"
        stroke="#ccc"
      />
    </g>
    -->
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
  name: 'AnswerZone',
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
    const rows = 20; // Количество строк в сетке
    const columns = 26; // Количество столбцов в сетке

    // Функция обработки события обновления фигурки
    const handleUpdatePiece = (updatedPiece) => {
      // Устанавливаем зону как 'answer'
      emit('update-piece', { ...updatedPiece, zone: 'answer' });
    };

    return {
      gridSize,
      rows,
      columns,
      handleUpdatePiece,
    };
  },
};
</script>

<style scoped>
/* Добавьте необходимые стили, если нужно */
</style>
