<template>
  <div id="app">
    <h1>Уголки</h1>
    <p>Соберите из блоков правильный прямоугольник без пустых ячеек и выступов.</p>
    <svg :width="svgWidth" :height="svgHeight" class="game-svg">
      <!-- Сетка -->
      <g class="grid">
        <line
          v-for="i in columns + 1"
          :key="'v' + i"
          :x1="i * gridSize"
          y1="0"
          :x2="i * gridSize"
          :y2="rows * gridSize"
          stroke="#ccc"
        />
        <line
          v-for="i in rows + 1"
          :key="'h' + i"
          x1="0"
          :y1="i * gridSize"
          :x2="columns * gridSize"
          :y2="i * gridSize"
          stroke="#ccc"
        />
      </g>

      <!-- Pieces -->
      <g>
        <PuzzlePiece
          v-for="piece in pieces"
          :key="piece.key"
          :piece="piece"
          :gridSize="gridSize"
          @update-piece="handleUpdatePiece"
        />
      </g>

      <!-- Control hints in the bottom left corner -->
      <g class="controls-hint">
        <rect x="10" :y="svgHeight - 60" width="240" height="50" fill="#fff" stroke="#000" />
        <text x="20" :y="svgHeight - 40" font-size="12" fill="#000">A: Влево, D: Вправо</text>
        <text x="20" :y="svgHeight - 20" font-size="12" fill="#000">Двойной щелчок: Отражение</text>
      </g>

      <!-- Reset button in the bottom right corner -->
      <g class="reset-button">
        <rect x="500" :y="svgHeight - 60" width="90" height="50" fill="#fff" stroke="#000" @click="resetPieces" />
        <text x="520" :y="svgHeight - 30" font-size="12" fill="#000" @click="resetPieces">Сбросить</text>
      </g>
    </svg>

    <div v-if="victory" class="victory-message">
      Поздравляем! Вы победили!
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import PuzzlePiece from './components/PuzzlePiece.vue';
import { pieces as initialPieces } from './data/pieces.js';

export default {
  name: 'App',
  components: {
    PuzzlePiece,
  },
  setup() {
    const gridSize = 30;
    const svgWidth = 600;
    const svgHeight = 600;
    const columns = Math.floor(svgWidth / gridSize);
    const rows = Math.floor(svgHeight / gridSize);

    // Function to initialize pieces in their initial state
    const initializePieces = () => {
      return initialPieces.map((piece, index) => ({
        ...piece,
        zone: 'start',
        position: { ...piece.initialPosition },
        rotation: 0,
        isReflected: false,
        key: Date.now() + index, // Unique key to recreate the component
      }));
    };

    // Creating initial state of pieces
    let pieces = ref(initializePieces());

    // Function to reset all pieces to their initial state
    const resetPieces = () => {
      pieces.value = initializePieces(); // Recreate initial state
    };

    // Handler to update the piece position
    const handleUpdatePiece = updatedPiece => {
      const index = pieces.value.findIndex(p => p.id === updatedPiece.id);
      if (index === -1) return;

      const tempPiece = { ...pieces.value[index], ...updatedPiece };

      if (!isWithinBounds(tempPiece) || isOverlapping(tempPiece)) {
        return;
      }

      pieces.value[index] = { ...updatedPiece };
      const [movedPiece] = pieces.value.splice(index, 1);
      pieces.value.push(movedPiece);

      checkVictory();
    };

    // Check if the piece is within bounds of the grid
    const isWithinBounds = piece => {
      const transformedShape = getTransformedShape(piece);
      for (const block of transformedShape) {
        const gridX = Math.floor(block.x / gridSize);
        const gridY = Math.floor(block.y / gridSize);

        if (gridX < 0 || gridX >= columns || gridY < 0 || gridY >= rows) {
          return false;
        }
      }
      return true;
    };

    // Check if the piece is overlapping with other pieces
    const isOverlapping = piece => {
      const transformedShape = getTransformedShape(piece);
      const occupied = new Set();

      pieces.value.forEach(p => {
        if (p.id !== piece.id) {
          const shape = getTransformedShape(p);
          shape.forEach(block => {
            const gridX = Math.floor(block.x / gridSize);
            const gridY = Math.floor(block.y / gridSize);
            occupied.add(`${gridX},${gridY}`);
          });
        }
      });

      for (const block of transformedShape) {
        const gridX = Math.floor(block.x / gridSize);
        const gridY = Math.floor(block.y / gridSize);
        if (occupied.has(`${gridX},${gridY}`)) {
          return true;
        }
      }

      return false;
    };

    // Check for victory condition
    const victory = ref(false);
    const checkVictory = () => {
      const victoryWidth = 330 / gridSize;
      const victoryHeight = 90 / gridSize;

      const grid = Array.from({ length: rows }, () =>
        Array(columns).fill(false)
      );

      for (const piece of pieces.value) {
        const transformedShape = getTransformedShape(piece);
        for (const block of transformedShape) {
          const gridX = Math.floor(block.x / gridSize);
          const gridY = Math.floor(block.y / gridSize);
          if (gridX >= 0 && gridX < columns && gridY >= 0 && gridY < rows) {
            grid[gridY][gridX] = true;
          }
        }
      }

      for (let y = 0; y <= rows - victoryHeight; y++) {
        for (let x = 0; x <= columns - victoryWidth; x++) {
          let filled = true;

          for (let offsetY = 0; offsetY < victoryHeight; offsetY++) {
            for (let offsetX = 0; offsetX < victoryWidth; offsetX++) {
              if (!grid[y + offsetY][x + offsetX]) {
                filled = false;
                break;
              }
            }
            if (!filled) break;
          }

          if (filled) {
            victory.value = true;
            return;
          }
        }
      }

      victory.value = false;
    };

    // Get transformed shape of the piece
    const getTransformedShape = piece => {
      let transformed = piece.shape.map(block => ({ ...block }));

      if (piece.isReflected) {
        transformed = transformed.map(block => ({
          x: -block.x - 1,
          y: block.y,
        }));
      }

      const angle = (piece.rotation % 360 + 360) % 360;

      transformed = transformed.map(block => {
        let newX, newY;

        switch (angle) {
          case 90:
            newX = -block.y - 1;
            newY = block.x;
            break;
          case 180:
            newX = -block.x - 1;
            newY = -block.y - 1;
            break;
          case 270:
            newX = block.y;
            newY = -block.x - 1;
            break;
          default:
            newX = block.x;
            newY = block.y;
        }

        return { x: newX, y: newY };
      });

      transformed = transformed.map(block => ({
        x: block.x * gridSize + piece.position.x,
        y: block.y * gridSize + piece.position.y,
      }));

      return transformed;
    };

    const transformedShapes = computed(() => {
      const shapes = {};
      pieces.value.forEach(piece => {
        shapes[piece.id] = getTransformedShape(piece);
      });
      return shapes;
    });

    return {
      svgWidth,
      svgHeight,
      gridSize,
      columns,
      rows,
      pieces,
      handleUpdatePiece,
      resetPieces,
      victory,
      transformedShapes,
    };
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  margin: 20px;
  position: relative;
}

.game-svg {
  border: 2px solid #333;
  background-color: #fafafa;
  margin: 20px auto;
}

.grid line {
  stroke: #ccc;
}

.victory-message {
  color: green;
  font-size: 1.5em;
  margin-top: 20px;
}
</style>
