<!-- src/App.vue -->
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
    </svg>
    <button @click="checkVictory">Проверить Победу</button>
    <div v-if="victory" class="victory-message">
      Поздравляем! Вы победили!
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'; // Удален импорт 'computed'
import PuzzlePiece from './components/PuzzlePiece.vue';
import { pieces as initialPieces } from './data/pieces.js';

export default {
  name: 'App',
  components: {
    PuzzlePiece,
  },
  setup() {
    // Размер сетки
    const gridSize = 30;

    // Размер SVG
    const svgWidth = 800;
    const svgHeight = 600;

    // Количество ячеек по горизонтали и вертикали
    const columns = Math.floor(svgWidth / gridSize);
    const rows = Math.floor(svgHeight / gridSize);

    // Инициализация фигурок с начальной зоной 'start'
    const pieces = ref(
      initialPieces.map(piece => ({
        ...piece,
        zone: 'start',
        position: { ...piece.initialPosition }, // Используем 'initialPosition'
      }))
    );

    // Отладочный вывод начальных фигурок
    console.log('Initial Pieces:', pieces.value);

    // Функция обновления фигурки
    const handleUpdatePiece = updatedPiece => {
      console.log('Handling update for piece:', updatedPiece);
      const index = pieces.value.findIndex(p => p.id === updatedPiece.id);
      if (index === -1) return;

      // Сохранение старой позиции для возможного отката
      const oldPosition = { ...pieces.value[index].position };
      const oldRotation = pieces.value[index].rotation;
      const oldReflection = pieces.value[index].isReflected;

      // Создание временной фигурки с обновлёнными данными
      const tempPiece = { ...pieces.value[index], ...updatedPiece };

      // Проверка, находится ли фигурка внутри границ SVG
      if (!isWithinBounds(tempPiece)) {
        // Восстановление старой позиции
        pieces.value[index].position = oldPosition;
        pieces.value[index].rotation = oldRotation;
        pieces.value[index].isReflected = oldReflection;
        console.log('Position out of bounds. Reverting to old position.');
        return; // Не обновляем позицию
      }

      // Проверка, перекрывает ли фигурка другие фигурки
      if (isOverlapping(tempPiece)) {
        // Восстановление старой позиции
        pieces.value[index].position = oldPosition;
        pieces.value[index].rotation = oldRotation;
        pieces.value[index].isReflected = oldReflection;
        console.log('Overlap detected. Reverting to old position.');
        return; // Не обновляем позицию
      }

      // Если проверки прошли успешно, обновляем фигурку
      pieces.value[index] = tempPiece;

      // Перемещаем фигурку в конец массива для отображения поверх других
      const [movedPiece] = pieces.value.splice(index, 1);
      pieces.value.push(movedPiece);

      console.log('Piece updated:', tempPiece);
    };

    // Проверка, находится ли фигурка внутри границ SVG
    const isWithinBounds = piece => {
      const transformedShape = getTransformedShape(piece);
      for (const block of transformedShape) {
        if (
          block.x < 0 ||
          block.x >= columns ||
          block.y < 0 ||
          block.y >= rows
        ) {
          return false;
        }
      }
      return true;
    };

    // Проверка, перекрывает ли фигурка другие фигурки
    const isOverlapping = piece => {
      const transformedShape = getTransformedShape(piece);
      const occupied = new Set();

      // Собираем все занятые позиции, кроме проверяемой фигурки
      pieces.value.forEach(p => {
        if (p.id !== piece.id) {
          const shape = getTransformedShape(p);
          shape.forEach(block => {
            occupied.add(`${block.x},${block.y}`);
          });
        }
      });

      // Проверяем, пересекается ли текущая фигурка с занятыми позициями
      for (const block of transformedShape) {
        if (occupied.has(`${block.x},${block.y}`)) {
          return true;
        }
      }

      return false;
    };

    // Проверка победы
    const victory = ref(false);
    const checkVictory = () => {
      // Желаемый размер 3x11
      const requiredCells = 3 * 11;
      let filledCells = 0;

      // Создаём сетку для проверки заполненности
      const grid = Array.from({ length: rows }, () =>
        Array(columns).fill(false)
      );

      for (const piece of pieces.value) {
        if (piece.zone !== 'answer') continue; // Рассматриваем только фигурки в зоне ответа

        const transformedShape = getTransformedShape(piece);
        for (const block of transformedShape) {
          if (
            block.x >= 0 &&
            block.x < columns &&
            block.y >= 0 &&
            block.y < rows
          ) {
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

    // Функция получения трансформированной формы
    const getTransformedShape = piece => {
      const angle = piece.rotation % 360;
      const isReflected = piece.isReflected;
      let transformed = piece.shape.map(block => ({ ...block }));

      // Применение вращения
      for (let i = 0; i < Math.floor((angle / 90) % 4); i++) {
        transformed = transformed.map(block => ({
          x: block.y,
          y: -block.x,
        }));
      }

      // Применение отражения
      if (isReflected) {
        transformed = transformed.map(block => ({
          x: -block.x,
          y: block.y,
        }));
      }

      // Смещение по позиции и округление до ближайшей ячейки
      transformed = transformed.map(block => ({
        x: Math.round(block.x + piece.position.x / gridSize),
        y: Math.round(block.y + piece.position.y / gridSize),
      }));

      return transformed;
    };

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
