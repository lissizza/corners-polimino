<!-- src/components/AnswerZone.vue -->
<template>
    <div class="answer-zone" ref="answerZone">
      <!-- Отображение размещённых фигурок -->
      <div
        v-for="piece in placedPieces"
        :key="piece.id"
        class="placed-piece"
        :style="getPieceStyle(piece)"
      >
        <PuzzlePiece :piece="piece" />
      </div>
      <!-- Отображение сетки -->
      <svg :width="width" :height="height" class="answer-svg">
        <g>
          <g v-for="(row, rowIndex) in grid" :key="'row' + rowIndex">
            <rect
              v-for="(cell, colIndex) in row"
              :key="'cell' + rowIndex + '-' + colIndex"
              :x="colIndex * cellSize"
              :y="rowIndex * cellSize"
              :width="cellSize"
              :height="cellSize"
              fill="#fff"
              stroke="#eee"
            />
          </g>
        </g>
      </svg>
    </div>
  </template>
  
  <script>
  import PuzzlePiece from './PuzzlePiece.vue';
  
  export default {
    name: 'AnswerZone',
    components: {
      PuzzlePiece,
    },
    props: {
      placedPieces: {
        type: Array,
        required: true,
      },
    },
    data() {
      return {
        rows: 3,
        cols: 11,
        cellSize: 30,
      };
    },
    computed: {
      width() {
        return this.cols * this.cellSize;
      },
      height() {
        return this.rows * this.cellSize;
      },
      grid() {
        return Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
      },
    },
    methods: {
      getPieceStyle(piece) {
        return {
          position: 'absolute',
          top: `${piece.position.y}px`,
          left: `${piece.position.x}px`,
          transform: `rotate(${piece.rotation || 0}deg)`,
        };
      },
      isPositionSuitable(piece) {
        const occupiedCells = this.getOccupiedCells(piece);
  
        for (let block of piece.shape) {
          const rotatedBlock = this.getRotatedBlock(block, piece.rotation);
  
          const blockX = piece.position.x + rotatedBlock.x * this.cellSize + this.cellSize / 2;
          const blockY = piece.position.y + rotatedBlock.y * this.cellSize + this.cellSize / 2;
  
          const col = Math.floor(blockX / this.cellSize);
          const row = Math.floor(blockY / this.cellSize);
  
          if (row < 0 || row >= this.rows || col < 0 || col >= this.cols) {
            return false;
          }
  
          if (occupiedCells[row][col]) {
            return false;
          }
        }
  
        return true;
      },
      getOccupiedCells(excludePiece) {
        const occupied = Array.from({ length: this.rows }, () => Array(this.cols).fill(false));
  
        this.placedPieces.forEach((piece) => {
          if (excludePiece && piece.id === excludePiece.id) {
            return;
          }
  
          piece.shape.forEach((block) => {
            const rotatedBlock = this.getRotatedBlock(block, piece.rotation);
            const blockX = piece.position.x + rotatedBlock.x * this.cellSize + this.cellSize / 2;
            const blockY = piece.position.y + rotatedBlock.y * this.cellSize + this.cellSize / 2;
  
            const col = Math.floor(blockX / this.cellSize);
            const row = Math.floor(blockY / this.cellSize);
  
            if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
              occupied[row][col] = true;
            }
          });
        });
  
        return occupied;
      },
      getRotatedBlock(block, rotation) {
        const angle = (rotation % 360 + 360) % 360; // Нормализуем угол
        let x = block.x;
        let y = block.y;
  
        switch (angle) {
          case 0:
            return { x, y };
          case 90:
            return { x: -y, y: x };
          case 180:
            return { x: -x, y: -y };
          case 270:
            return { x: y, y: -x };
          default: {
            // Для нестандартных углов (если они будут) используем матрицу поворота
            const rad = (Math.PI / 180) * angle;
            const cos = Math.cos(rad);
            const sin = Math.sin(rad);
            return {
              x: Math.round(x * cos - y * sin),
              y: Math.round(x * sin + y * cos),
            };
          }
        }
      },
      getAnswer() {
        const matrix = Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
        this.placedPieces.forEach((piece) => {
          piece.shape.forEach((block) => {
            const rotatedBlock = this.getRotatedBlock(block, piece.rotation);
            const blockX = piece.position.x + rotatedBlock.x * this.cellSize + this.cellSize / 2;
            const blockY = piece.position.y + rotatedBlock.y * this.cellSize + this.cellSize / 2;
  
            const col = Math.floor(blockX / this.cellSize);
            const row = Math.floor(blockY / this.cellSize);
  
            if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
              matrix[row][col] = 1;
            }
          });
        });
        return matrix;
      },
    },
  };
  </script>
  
  <style scoped>
  .answer-zone {
    width: 330px; /* 11 * 30 */
    height: 90px; /* 3 * 30 */
    border: 2px solid #000;
    background-color: #f0f0f0;
    position: relative;
  }
  
  .placed-piece {
    position: absolute;
  }
  
  .answer-svg {
    position: absolute;
    top: 0;
    left: 0;
    z-index: -1; /* Помещаем сетку под фигурками */
  }
  
  svg {
    overflow: visible;
  }
  </style>
  