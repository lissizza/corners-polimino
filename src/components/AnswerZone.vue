<!-- src/components/AnswerZone.vue -->
<template>
    <div class="answer-zone" ref="answerZone">
      <!-- Display placed pieces -->
      <div
        v-for="(piece, index) in placedPieces"
        :key="piece.id"
        class="placed-piece"
        :style="getPieceStyle(piece)"
        @mousedown.left="onPieceMouseDown(piece, index, $event)"
      >
        <PuzzlePiece :piece="piece" />
      </div>
      <!-- Grid display -->
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
              stroke="#ccc"
            />
          </g>
        </g>
      </svg>
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
      startZoneRect: {
        type: Object,
        required: true,
      },
    },
    data() {
      return {
        rows: 15,
        cols: 15,
        cellSize: 30,
        isDragging: false,
        draggingPiece: null,
        cursorPosition: { x: 0, y: 0 },
        previousPosition: null,
        previousRotation: null,
        draggingPieceIndex: null,
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
      draggingPieceStyle() {
        return {
          position: 'fixed',
          top: `${this.cursorPosition.y - this.draggingPiece.offsetY}px`,
          left: `${this.cursorPosition.x - this.draggingPiece.offsetX}px`,
          pointerEvents: 'none',
          zIndex: 1000,
        };
      },
    },
    methods: {
      getPieceStyle(piece) {
        return {
          position: 'absolute',
          top: `${piece.position.y}px`,
          left: `${piece.position.x}px`,
        };
      },
      onPieceMouseDown(piece, index, event) {
        event.stopPropagation();

        const clickedBlock = this.getClickedBlock(piece, event);
        if (!clickedBlock) return; // Игнорируем клики на невидимые части

        this.isDragging = true;
        this.draggingPiece = { ...piece };
        this.draggingPiece.offsetX = event.offsetX;
        this.draggingPiece.offsetY = event.offsetY;
  
        // Remember the index of the dragging piece
        this.draggingPieceIndex = index;
  
        // Save previous position and rotation
        this.previousPosition = { ...piece.position };
        this.previousRotation = piece.rotation;
  
        // Emit event to parent to remove piece
        this.$emit('remove-piece', index);
  
        // Set initial cursor position
        this.cursorPosition = { x: event.clientX, y: event.clientY };
  
        // Add event listeners
        window.addEventListener('mousemove', this.onDrag);
        window.addEventListener('mouseup', this.onDrop);
        window.addEventListener('keydown', this.onKeyDown);
        window.addEventListener('mouseleave', this.onMouseLeave);
      },
      getClickedBlock(piece, event) {
        const { offsetX, offsetY } = event;
        const rotatedShape = piece.shape.map((block) =>
          this.getRotatedBlock(block, piece.rotation, piece.shape)
        );

        for (let block of rotatedShape) {
          const blockX = block.x * this.cellSize;
          const blockY = block.y * this.cellSize;
          if (
            offsetX >= blockX &&
            offsetX < blockX + this.cellSize &&
            offsetY >= blockY &&
            offsetY < blockY + this.cellSize
          ) {
            return block; // Возвращаем блок, на который кликнули
          }
        }
        return null; // Возвращаем null, если кликнули на невидимую часть
      },
      onDrag(event) {
        const clientX = Math.max(0, Math.min(event.clientX, window.innerWidth));
        const clientY = Math.max(0, Math.min(event.clientY, window.innerHeight));
        this.cursorPosition = { x: clientX, y: clientY };
      },
      onDrop(event) {
        // Remove event listeners
        window.removeEventListener('mousemove', this.onDrag);
        window.removeEventListener('mouseup', this.onDrop);
        window.removeEventListener('keydown', this.onKeyDown);
        window.removeEventListener('mouseleave', this.onMouseLeave);
  
        // Calculate drop position relative to answer zone
        const answerZoneRect = this.$el.getBoundingClientRect();
        const x = event.clientX - answerZoneRect.left - this.draggingPiece.offsetX;
        const y = event.clientY - answerZoneRect.top - this.draggingPiece.offsetY;
  
        // Snap position to grid
        this.draggingPiece.position = {
          x: Math.round(x / this.cellSize) * this.cellSize,
          y: Math.round(y / this.cellSize) * this.cellSize,
        };
  
        // Check if drop is inside the answer zone
        if (
          event.clientX >= answerZoneRect.left &&
          event.clientX <= answerZoneRect.right &&
          event.clientY >= answerZoneRect.top &&
          event.clientY <= answerZoneRect.bottom
        ) {
          // Check if position is suitable
          if (this.isPositionSuitable(this.draggingPiece)) {
            // Emit event to parent to add piece
            this.$emit('add-piece', this.draggingPiece);
          } else {
            // Return piece to previous position
            this.draggingPiece.position = this.previousPosition;
            this.draggingPiece.rotation = this.previousRotation;
            this.$emit('add-piece', this.draggingPiece);
          }
        } else if (
          event.clientX >= this.startZoneRect.left &&
          event.clientX <= this.startZoneRect.right &&
          event.clientY >= this.startZoneRect.top &&
          event.clientY <= this.startZoneRect.bottom
        ) {
          // Dropped in the start zone, reset position and rotation
          this.draggingPiece.position = null;
          this.draggingPiece.rotation = 0;
          this.$emit('return-piece-to-start', this.draggingPiece);
        } else {
          // Drop outside both zones; return piece to previous position
          this.draggingPiece.position = this.previousPosition;
          this.draggingPiece.rotation = this.previousRotation;
          this.$emit('add-piece', this.draggingPiece);
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
        // Return piece to previous position
        this.draggingPiece.position = this.previousPosition;
        this.draggingPiece.rotation = this.previousRotation;
        this.$emit('add-piece', this.draggingPiece);
  
        // Reset dragging state
        this.isDragging = false;
        this.draggingPiece = null;
  
        // Remove event listeners
        window.removeEventListener('mousemove', this.onDrag);
        window.removeEventListener('mouseup', this.onDrop);
        window.removeEventListener('keydown', this.onKeyDown);
        window.removeEventListener('mouseleave', this.onMouseLeave);
      },
      // Проверка, можно ли поставить фигуру в определенную позицию
      isPositionSuitable(piece) {
          const occupiedCells = this.getOccupiedCells(piece);

          for (let block of piece.shape) {
          // Рассчёт координат блока с учетом поворота
          const rotatedBlock = this.getRotatedBlock(block, piece.rotation, piece.shape);

          // Рассчёт абсолютной позиции блока
          const blockX = piece.position.x + rotatedBlock.x * this.cellSize;
          const blockY = piece.position.y + rotatedBlock.y * this.cellSize;

          // Проверка, находится ли блок внутри поля
          const col = Math.floor(blockX / this.cellSize);
          const row = Math.floor(blockY / this.cellSize);

          if (row < 0 || row >= this.rows || col < 0 || col >= this.cols) {
              return false; // Если хотя бы один блок выходит за границы, возвращаем false
          }

          if (occupiedCells[row][col]) {
              return false; // Если блок попадает на занятое место, тоже false
          }
          }

          return true;
      },

      // Получаем массив всех занятых клеток
      getOccupiedCells(excludePiece) {
          const occupied = Array.from({ length: this.rows }, () => Array(this.cols).fill(false));

          this.placedPieces.forEach((piece) => {
          if (excludePiece && piece.id === excludePiece.id) {
              return;
          }

          piece.shape.forEach((block) => {
              const rotatedBlock = this.getRotatedBlock(block, piece.rotation, piece.shape);

              const blockX = piece.position.x + rotatedBlock.x * this.cellSize;
              const blockY = piece.position.y + rotatedBlock.y * this.cellSize;

              const col = Math.floor(blockX / this.cellSize);
              const row = Math.floor(blockY / this.cellSize);

              if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
              occupied[row][col] = true;
              }
          });
          });

          return occupied;
      },

      // Рассчёт координат блока после поворота
      getRotatedBlock(block, angle, shape) {
          angle = (angle % 360 + 360) % 360;

          // Определение границ фигуры (максимальные и минимальные координаты)
          const maxX = Math.max(...shape.map(b => b.x));
          const minX = Math.min(...shape.map(b => b.x));
          const maxY = Math.max(...shape.map(b => b.y));
          const minY = Math.min(...shape.map(b => b.y));

          // Рассчёт относительных координат блока относительно верхнего левого угла
          const relativeX = block.x - minX;
          const relativeY = block.y - minY;

          let newX, newY;

          // Вращаем блок вокруг верхнего левого угла
          switch (angle) {
          case 90:
              newX = maxY - relativeY;
              newY = relativeX;
              break;
          case 180:
              newX = maxX - relativeX;
              newY = maxY - relativeY;
              break;
          case 270:
              newX = relativeY;
              newY = maxX - relativeX;
              break;
          default:
              newX = block.x;
              newY = block.y;
          }

          return { x: newX, y: newY };
      },

      getAnswer() {
        const matrix = Array.from({ length: this.rows }, () => Array(this.cols).fill(0));
        this.placedPieces.forEach((piece) => {
          piece.shape.forEach((block) => {
            const rotatedBlock = this.getRotatedBlock(block, piece.rotation);
  
            const blockCenterX = piece.position.x + (rotatedBlock.x + 0.5) * this.cellSize;
            const blockCenterY = piece.position.y + (rotatedBlock.y + 0.5) * this.cellSize;
  
            const col = Math.floor(blockCenterX / this.cellSize);
            const row = Math.floor(blockCenterY / this.cellSize);
  
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
    width: 450px; /* 15 * 30 */
    height: 450px; /* 15 * 30 */
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
    z-index: -1; /* Place grid under pieces */
  }
  
  .dragging-piece {
    position: fixed;
    pointer-events: none;
    z-index: 1000;
  }
  
  .controls {
    position: fixed;
    bottom: 10px;
    left: 10px;
    background: rgba(255, 255, 255, 0.8);
    padding: 10px;
  }
  
  svg {
    overflow: visible;
  }
  </style>
  