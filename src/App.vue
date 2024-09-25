<!-- src/App.vue -->
<template>
  <div class="game-container">
    <StartZone
      :pieces="pieces"
      @start-drag="onStartDrag"
    />
    <AnswerZone
      :placedPieces="placedPieces"
      ref="answerZone"
    />
    <!-- Отображение перетаскиваемой фигурки -->
    <div v-if="isDragging" class="dragging-piece" :style="draggingPieceStyle">
      <PuzzlePiece :piece="draggingPiece" />
    </div>
    <!-- Подсказка по клавишам -->
    <div v-if="isDragging" class="controls">
      <p>Нажмите "A" или "D" для поворота</p>
    </div>
  </div>
</template>

<script>
import StartZone from './components/StartZone.vue';
import AnswerZone from './components/AnswerZone.vue';
import PuzzlePiece from './components/PuzzlePiece.vue';
import { pieces as initialPieces } from './data/pieces.js';

export default {
  name: 'App',
  components: {
    StartZone,
    AnswerZone,
    PuzzlePiece,
  },
  data() {
    return {
      pieces: initialPieces.map((piece) => ({
        ...piece,
        rotation: piece.rotation || 0,
      })),
      placedPieces: [],
      isDragging: false,
      draggingPiece: null,
      cursorPosition: { x: 0, y: 0 },
    };
  },
  computed: {
    draggingPieceStyle() {
      return {
        position: 'fixed',
        top: `${this.cursorPosition.y - this.draggingPiece.offsetY}px`,
        left: `${this.cursorPosition.x - this.draggingPiece.offsetX}px`,
        transform: `rotate(${this.draggingPiece.rotation || 0}deg)`,
        pointerEvents: 'none',
        zIndex: 1000,
      };
    },
  },
  methods: {
    onStartDrag(piece, event) {
      this.isDragging = true;
      this.draggingPiece = JSON.parse(JSON.stringify(piece)); // Глубокое копирование
      this.draggingPiece.offsetX = event.offsetX;
      this.draggingPiece.offsetY = event.offsetY;

      // Удаляем фигурку из списка доступных
      this.pieces = this.pieces.filter((p) => p.id !== piece.id);

      // Устанавливаем начальную позицию курсора
      this.cursorPosition = { x: event.clientX, y: event.clientY };

      // Добавляем обработчики событий
      window.addEventListener('mousemove', this.onDrag);
      window.addEventListener('mouseup', this.onDrop);
      window.addEventListener('keydown', this.onKeyDown);
      window.addEventListener('mouseleave', this.onMouseLeave);
    },
    onDrag(event) {
      this.cursorPosition = { x: event.clientX, y: event.clientY };
    },
    onDrop(event) {
      // Удаляем обработчики событий
      window.removeEventListener('mousemove', this.onDrag);
      window.removeEventListener('mouseup', this.onDrop);
      window.removeEventListener('keydown', this.onKeyDown);
      window.removeEventListener('mouseleave', this.onMouseLeave);

      // Вычисляем позицию дропа относительно зоны ответа
      const answerZoneRect = this.$refs.answerZone.$el.getBoundingClientRect();
      const x = event.clientX - answerZoneRect.left - this.draggingPiece.offsetX;
      const y = event.clientY - answerZoneRect.top - this.draggingPiece.offsetY;

      // Проверяем, находится ли дроп внутри зоны ответа
      if (
        event.clientX >= answerZoneRect.left &&
        event.clientX <= answerZoneRect.right &&
        event.clientY >= answerZoneRect.top &&
        event.clientY <= answerZoneRect.bottom
      ) {
        // Устанавливаем позицию фигурки
        this.draggingPiece.position = { x, y };

        // Привязываем позицию к сетке
        const cellSize = this.$refs.answerZone.cellSize;
        this.draggingPiece.position.x = Math.floor(this.draggingPiece.position.x / cellSize) * cellSize;
        this.draggingPiece.position.y = Math.floor(this.draggingPiece.position.y / cellSize) * cellSize;

        // Проверяем, подходит ли позиция
        if (this.$refs.answerZone.isPositionSuitable(this.draggingPiece)) {
          // Добавляем фигурку в размещённые
          this.placedPieces.push(this.draggingPiece);
        } else {
          // Возвращаем фигурку в стартовую зону
          this.pieces.push({ ...this.draggingPiece, position: null });
        }
      } else {
        // Возвращаем фигурку в стартовую зону
        this.pieces.push({ ...this.draggingPiece, position: null });
      }

      // Сбрасываем состояние перетаскивания
      this.isDragging = false;
      this.draggingPiece = null;
    },
    onKeyDown(event) {
      if (this.isDragging && this.draggingPiece) {
        if (event.key === 'a' || event.key === 'A') {
          this.draggingPiece.rotation = (this.draggingPiece.rotation - 90 + 360) % 360;
        } else if (event.key === 'd' || event.key === 'D') {
          this.draggingPiece.rotation = (this.draggingPiece.rotation + 90) % 360;
        }
      }
    },
    onMouseLeave() {
      // Возвращаем фигурку в стартовую зону
      this.pieces.push({ ...this.draggingPiece, position: null });
      this.isDragging = false;
      this.draggingPiece = null;

      // Удаляем обработчики событий
      window.removeEventListener('mousemove', this.onDrag);
      window.removeEventListener('mouseup', this.onDrop);
      window.removeEventListener('keydown', this.onKeyDown);
      window.removeEventListener('mouseleave', this.onMouseLeave);
    },
  },
};
</script>

<style>
.game-container {
  display: flex;
  gap: 20px;
  position: relative;
}

.controls {
  position: fixed;
  bottom: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.8);
  padding: 10px;
}

.dragging-piece {
  position: fixed;
  pointer-events: none;
  z-index: 1000;
}

body {
  user-select: none;
}
</style>
