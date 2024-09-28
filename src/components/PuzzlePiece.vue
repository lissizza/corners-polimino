<!-- src/components/PuzzlePiece.vue -->
<template>
  <g
    :transform="currentTransform"
    @mousedown="onMouseDown"
    @dblclick="onDoubleClick"
    pointer-events="all"
  >
    <rect
      v-for="(block, index) in transformedShape"
      :key="index"
      :x="block.x * gridSize"
      :y="block.y * gridSize"
      :width="gridSize"
      :height="gridSize"
      :fill="piece.color"
      stroke="#000"
    />
    <!-- Табличка с клавишами при перетаскивании -->
    <g v-if="isDragging" class="controls">
      <rect x="0" y="-30" width="100" height="30" fill="#fff" stroke="#000" />
      <text x="10" y="-10" font-size="12" fill="#000">A: Влево</text>
      <text x="60" y="-10" font-size="12" fill="#000">D: Вправо</text>
    </g>
  </g>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'PuzzlePiece',
  props: {
    piece: {
      type: Object,
      required: true,
    },
    gridSize: {
      type: Number,
      required: true,
    },
  },
  emits: ['update-piece'],
  setup(props, { emit }) {
    const isDragging = ref(false);
    const draggingPosition = ref(null); // Временная позиция при перетаскивании

    const rotation = ref(props.piece.rotation || 0);
    const isReflected = ref(props.piece.isReflected || false);

    // Трансформированная форма фигурки
    const transformedShape = computed(() => {
      let shape = props.piece.shape.map(block => ({ ...block }));

      // Применение вращения
      for (let i = 0; i < Math.floor((rotation.value / 90) % 4); i++) {
        shape = shape.map(block => ({
          x: block.y,
          y: -block.x,
        }));
      }

      // Применение отражения
      if (isReflected.value) {
        shape = shape.map(block => ({
          x: -block.x,
          y: block.y,
        }));
      }

      return shape;
    });

    // Основной трансформ (положение, вращение, отражение)
    const transform = computed(() => {
      // Рассчитываем точку вращения (центр фигуры)
      const pivotX = props.piece.shape[0].x * props.gridSize;
      const pivotY = props.piece.shape[0].y * props.gridSize;

      return `translate(${props.piece.position.x}, ${props.piece.position.y}) rotate(${rotation.value}, ${pivotX}, ${pivotY}) scale(${isReflected.value ? -1 : 1}, 1)`;
    });

    // Текущий трансформ: либо основная позиция, либо временная при перетаскивании
    const currentTransform = computed(() => {
      if (draggingPosition.value) {
        // Временная позиция при перетаскивании
        const pivotX = props.piece.shape[0].x * props.gridSize;
        const pivotY = props.piece.shape[0].y * props.gridSize;
        return `translate(${draggingPosition.value.x}, ${draggingPosition.value.y}) rotate(${rotation.value}, ${pivotX}, ${pivotY}) scale(${isReflected.value ? -1 : 1}, 1)`;
      } else {
        // Основная позиция
        return transform.value;
      }
    });

    // Обработчик нажатия мыши для начала перетаскивания
    const onMouseDown = event => {
      event.preventDefault();
      isDragging.value = true;

      // Получаем родительский SVG элемент
      const svg = event.currentTarget.ownerSVGElement;
      const svgRect = svg.getBoundingClientRect();

      // Начальная позиция курсора относительно SVG
      const startX = event.clientX - svgRect.left;
      const startY = event.clientY - svgRect.top;

      // Начальная позиция фигурки
      const initialPos = { ...props.piece.position };

      const onMouseMove = e => {
        const currentX = e.clientX - svgRect.left;
        const currentY = e.clientY - svgRect.top;

        // Вычисляем смещение
        const dx = currentX - startX;
        const dy = currentY - startY;

        // Обновляем временную позицию фигурки
        draggingPosition.value = { x: initialPos.x + dx, y: initialPos.y + dy };
      };

      const onMouseUp = () => {
        isDragging.value = false;
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);

        if (draggingPosition.value) {
          // Привязка к сетке (snap-to-grid)
          const snappedX = Math.round(draggingPosition.value.x / props.gridSize) * props.gridSize;
          const snappedY = Math.round(draggingPosition.value.y / props.gridSize) * props.gridSize;
          draggingPosition.value = { x: snappedX, y: snappedY };

          // Отправляем обновлённое состояние фигурки
          emit('update-piece', {
            ...props.piece,
            position: { x: snappedX, y: snappedY },
            rotation: rotation.value,
            isReflected: isReflected.value,
          });

          // Очистка временной позиции
          draggingPosition.value = null;
        }
      };

      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    };

    // Обработчик двойного клика для отражения фигурки
    const onDoubleClick = () => {
      isReflected.value = !isReflected.value;
      emit('update-piece', {
        ...props.piece,
        isReflected: isReflected.value,
      });
    };

    // Обработчик клавиш для вращения фигурки
    const onKeyDown = event => {
      if (!isDragging.value) return;
      if (event.key === 'a' || event.key === 'A') {
        rotation.value = (rotation.value - 90) % 360;
        if (rotation.value < 0) rotation.value += 360;
        console.log(`Rotated left: ${rotation.value} degrees`); // Отладка
        emit('update-piece', {
          ...props.piece,
          rotation: rotation.value,
        });
      }
      if (event.key === 'd' || event.key === 'D') {
        rotation.value = (rotation.value + 90) % 360;
        console.log(`Rotated right: ${rotation.value} degrees`); // Отладка
        emit('update-piece', {
          ...props.piece,
          rotation: rotation.value,
        });
      }
    };

    // Добавление и удаление обработчиков событий клавиатуры
    onMounted(() => {
      window.addEventListener('keydown', onKeyDown);
    });

    onBeforeUnmount(() => {
      window.removeEventListener('keydown', onKeyDown);
    });

    return {
      isDragging,
      draggingPosition,
      rotation,
      isReflected,
      transformedShape,
      transform,
      currentTransform,
      onMouseDown,
      onDoubleClick,
    };
  },
};
</script>

<style scoped>
.controls {
  cursor: pointer;
}
</style>
