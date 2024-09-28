<template>
  <div id="app">
    <h1>Геометрическая Головоломка</h1>
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

      <!-- Текстовая Метка Зоны Start -->
      <text x="10" y="20" font-size="16" fill="#333">Стартовая Зона</text>

      <!-- Занятые клетки (для отладки) -->
      <g class="occupied-cells">
        <rect
          v-for="(cell, index) in occupiedCells"
          :key="index"
          :x="cell.x * gridSize"
          :y="cell.y * gridSize"
          :width="gridSize"
          :height="gridSize"
          fill="rgba(255, 0, 0, 0.5)"
        />
      </g>

      <!-- Фигурки -->
      <g>
        <PuzzlePiece
          v-for="piece in pieces"
          :key="piece.id"
          :piece="piece"
          :gridSize="gridSize"
          @update-piece="handleUpdatePiece"
        />
      </g>

      <!-- Подсказка по клавишам управления в левом нижнем углу -->
      <g class="controls-hint">
        <rect x="10" :y="svgHeight - 40" width="200" height="30" fill="#fff" stroke="#000" />
        <text x="20" :y="svgHeight - 20" font-size="12" fill="#000">A: Влево, D: Вправо</text>
      </g>
    </svg>
    <button @click="checkVictory">Проверить Победу</button>
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
    const svgWidth = 800;
    const svgHeight = 600;
    const columns = Math.floor(svgWidth / gridSize);
    const rows = Math.floor(svgHeight / gridSize);

    const pieces = ref(
      initialPieces.map(piece => ({
        ...piece,
        zone: 'start',
        position: { ...piece.initialPosition },
      }))
    );

    const handleUpdatePiece = updatedPiece => {
      console.log('Attempting to update piece:', updatedPiece);
      const index = pieces.value.findIndex(p => p.id === updatedPiece.id);
      if (index === -1) return;

      // Создание временной фигурки с обновлёнными данными
      const tempPiece = { ...pieces.value[index], ...updatedPiece };

      // Проверка на выход за границы
      if (!isWithinBounds(tempPiece)) {
        console.log('Position out of bounds, reverting to old position.');
        return; // Не обновляем позицию, если фигура выходит за границы
      }

      // Проверка на пересечение с другими фигурами
      if (isOverlapping(tempPiece)) {
        console.log('Overlap detected, reverting to old position.');
        return; // Не обновляем позицию, если обнаружено пересечение
      }

      // Если проверки пройдены, обновляем фигурку
      pieces.value[index] = { ...updatedPiece }; // Обновляем объект полностью, чтобы Vue отследил изменение

      // Перемещаем фигурку в конец массива для отображения поверх других
      const [movedPiece] = pieces.value.splice(index, 1);
      pieces.value.push(movedPiece);

      console.log('Piece successfully updated:', updatedPiece);
    };

    const isWithinBounds = piece => {
      const transformedShape = getTransformedShape(piece);
      for (const block of transformedShape) {
        // Приводим координаты в сетку для проверки, находятся ли они в пределах допустимого диапазона
        const gridX = Math.floor(block.x / gridSize);
        const gridY = Math.floor(block.y / gridSize);

        if (gridX < 0 || gridX >= columns || gridY < 0 || gridY >= rows) {
          console.log(`Block out of bounds: (${gridX}, ${gridY})`);
          return false;
        }
      }
      return true;
    };

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
          console.log(`Block overlaps at: (${gridX}, ${gridY})`);
          return true;
        }
      }

      return false;
    };

    const victory = ref(false);
    const checkVictory = () => {
      const requiredCells = 3 * 11;
      let filledCells = 0;

      const grid = Array.from({ length: rows }, () => Array(columns).fill(false));

      for (const piece of pieces.value) {
        if (piece.zone !== 'answer') continue;

        const transformedShape = getTransformedShape(piece);
        for (const block of transformedShape) {
          if (block.x >= 0 && block.x < columns && block.y >= 0 && block.y < rows) {
            grid[block.y][block.x] = true;
            filledCells++;
          }
        }
      }

      if (filledCells === requiredCells) {
        victory.value = true;
      } else {
        victory.value = false;
        alert('Не все клетки заполнены!');
      }
    };

    const getTransformedShape = piece => {
      // Копируем начальную форму блоков
      let transformed = piece.shape.map(block => ({ ...block }));

      // Применение отражения, если фигура была отражена
      if (piece.isReflected) {
        transformed = transformed.map(block => ({
          x: -block.x -1,  // Отражение по оси X
          y: block.y,
        }));
      }

      // Применение вращения относительно верхнего левого угла
      const angle = (piece.rotation % 360 + 360) % 360;

      transformed = transformed.map(block => {
        let newX, newY;

        switch (angle) {
          case 90:
            newX = - block.y -1;
            newY = block.x;
            break;
          case 180:
            newX = -block.x -1;
            newY = -block.y -1;
            break;
          case 270:
            newX = block.y;
            newY = -block.x -1;
            break;
          default:
            newX = block.x;
            newY = block.y;
        }

        return { x: newX, y: newY };
      });

      // Смещение всех блоков в зависимости от текущей позиции фигуры (в пикселях)
      transformed = transformed.map(block => ({
        x: block.x * gridSize + piece.position.x,
        y: block.y * gridSize + piece.position.y,
      }));

      console.log(`Transformed shape for piece ${piece.id}:`, transformed);
      return transformed;
    };

    // Предварительное вычисление всех transformedShapes
    const transformedShapes = computed(() => {
      const shapes = {};
      pieces.value.forEach(piece => {
        shapes[piece.id] = getTransformedShape(piece);
      });
      return shapes;
    });

    const occupiedCells = computed(() => {
      const occupied = [];
      pieces.value.forEach(piece => {
        const transformedShape = getTransformedShape(piece);
        transformedShape.forEach(block => {
          // Перевод координат блоков в индексы сетки
          const gridX = Math.floor(block.x / gridSize);
          const gridY = Math.floor(block.y / gridSize);

          // Проверяем, что координаты находятся в пределах сетки
          if (gridX >= 0 && gridX < columns && gridY >= 0 && gridY < rows) {
            occupied.push({ x: gridX, y: gridY });
          }
        });
      });
      console.log('Occupied cells:', occupied);
      return occupied;
    });

    return {
      svgWidth,
      svgHeight,
      gridSize,
      columns,
      rows,
      pieces,
      handleUpdatePiece,
      checkVictory,
      victory,
      occupiedCells,
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
