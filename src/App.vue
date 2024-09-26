<!-- src/App.vue -->
<template>
  <div class="game-container" ref="gameContainer">
    <StartZone
      :pieces="pieces"
      @start-drag="onStartDrag"
      ref="startZone"
    />
    <AnswerZone
      :placedPieces="placedPieces"
      :startZoneRect="startZoneRect"
      ref="answerZone"
      @add-piece="onAddPiece"
      @remove-piece="onRemovePiece"
      @return-piece-to-start="onReturnPieceToStart"
    />
    <!-- Display dragging piece -->
    <div v-if="isDragging" class="dragging-piece" :style="draggingPieceStyle">
      <PuzzlePiece :piece="draggingPiece" />
    </div>
    <!-- Controls hint -->
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
      startZoneRect: null,
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
  mounted() {
    // Get the bounding rectangle of the start zone
    this.$nextTick(() => {
      const startZoneElement = this.$refs.startZone.$el;
      this.startZoneRect = startZoneElement.getBoundingClientRect();
    });
  },
  methods: {
    onStartDrag(piece, event) {
      this.isDragging = true;
      this.draggingPiece = JSON.parse(JSON.stringify(piece)); // Deep copy
      this.draggingPiece.offsetX = event.offsetX;
      this.draggingPiece.offsetY = event.offsetY;

      // Remove piece from pieces array
      this.pieces = this.pieces.filter((p) => p.id !== piece.id);

      // Set initial cursor position
      this.cursorPosition = { x: event.clientX, y: event.clientY };

      // Add event listeners
      window.addEventListener('mousemove', this.onDrag);
      window.addEventListener('mouseup', this.onDrop);
      window.addEventListener('keydown', this.onKeyDown);
      window.addEventListener('mouseleave', this.onMouseLeave);
    },
    onDrag(event) {
      this.cursorPosition = { x: event.clientX, y: event.clientY };
    },
    onDrop(event) {
      // Remove event listeners
      window.removeEventListener('mousemove', this.onDrag);
      window.removeEventListener('mouseup', this.onDrop);
      window.removeEventListener('keydown', this.onKeyDown);
      window.removeEventListener('mouseleave', this.onMouseLeave);

      // Calculate drop position relative to answer zone
      const answerZoneRect = this.$refs.answerZone.$el.getBoundingClientRect();
      const x = event.clientX - answerZoneRect.left - this.draggingPiece.offsetX;
      const y = event.clientY - answerZoneRect.top - this.draggingPiece.offsetY;

      // Set the position of the piece
      this.draggingPiece.position = { x, y };

      // Snap position to grid
      const cellSize = this.$refs.answerZone.cellSize;
      this.draggingPiece.position.x = Math.round(this.draggingPiece.position.x / cellSize) * cellSize;
      this.draggingPiece.position.y = Math.round(this.draggingPiece.position.y / cellSize) * cellSize;

      // Check if drop is inside the answer zone
      if (
        event.clientX >= answerZoneRect.left &&
        event.clientX <= answerZoneRect.right &&
        event.clientY >= answerZoneRect.top &&
        event.clientY <= answerZoneRect.bottom
      ) {
        // Check if position is suitable
        if (this.$refs.answerZone.isPositionSuitable(this.draggingPiece)) {
          // Add piece to placedPieces
          this.placedPieces.push(this.draggingPiece);
        } else {
          // Return piece to start zone
          this.pieces.push({ ...this.draggingPiece, position: null });
        }
      } else {
        // Return piece to start zone
        this.pieces.push({ ...this.draggingPiece, position: null });
      }

      // Reset dragging state
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
      // Return piece to start zone
      this.pieces.push({ ...this.draggingPiece, position: null });
      this.isDragging = false;
      this.draggingPiece = null;

      // Remove event listeners
      window.removeEventListener('mousemove', this.onDrag);
      window.removeEventListener('mouseup', this.onDrop);
      window.removeEventListener('keydown', this.onKeyDown);
      window.removeEventListener('mouseleave', this.onMouseLeave);
    },
    onAddPiece(piece) {
      this.placedPieces.push(piece);
    },
    onRemovePiece(index) {
      this.placedPieces.splice(index, 1);
    },
    onReturnPieceToStart(piece) {
      // Return piece to start zone
      this.pieces.push({ ...piece, position: null });
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
