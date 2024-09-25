<!-- src/components/StartZone.vue -->
<template>
    <div class="start-zone">
      <div class="pieces-container">
        <div
          v-for="piece in availablePieces"
          :key="piece.id"
          class="available-piece"
          @mousedown.left="onDragStart(piece, $event)"
          :style="getPieceStyle(piece)"
        >
          <PuzzlePiece :piece="piece" />
        </div>
      </div>
    </div>
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
    data() {
      return {
        availablePieces: this.pieces,
      };
    },
    watch: {
      pieces(newPieces) {
        this.availablePieces = newPieces;
      },
    },
    methods: {
      onDragStart(piece, event) {
        this.$emit('start-drag', piece, event);
      },
      getPieceStyle(piece) {
        return {
          cursor: 'grab',
          transform: `rotate(${piece.rotation || 0}deg)`,
        };
      },
    },
  };
  </script>
  
  <style scoped>
  .start-zone {
    width: 300px;
    height: 400px;
    border: 2px solid #ccc;
    background-color: #f9f9f9;
    overflow: auto;
  }
  
  .pieces-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px;
  }
  
  .available-piece {
    cursor: grab;
  }
  </style>
  