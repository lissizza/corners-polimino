<template>
  <g :transform="currentTransform" @mousedown="onMouseDown" @dblclick="onDoubleClick" pointer-events="all">
    <!-- Определение градиентов для блоков -->
    <defs>
      <radialGradient
        v-for="(block, index) in piece.shape"
        :key="index"
        :id="'gradient-' + piece.id + '-' + index"
        cx="50%"
        cy="50%"
        r="70%"
        fx="50%"
        fy="50%"
      >
        <stop offset="0%" :stop-color="lightenColor(piece.color)" />
        <stop offset="50%" :stop-color="piece.color" />
        <stop offset="100%" :stop-color="darkenColor(piece.color)" />
      </radialGradient>
    </defs>

    <!-- Рендеринг блоков фигурки с использованием градиента -->
    <rect
      v-for="(block, index) in piece.shape"
      :key="index"
      :x="block.x * gridSize"
      :y="block.y * gridSize"
      :width="gridSize"
      :height="gridSize"
      :fill="'url(#gradient-' + piece.id + '-' + index + ')'"
      stroke="#000"
    />
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
    // Helper function to darken the color
    const darkenColor = (color) => {
      let c = color.slice(1); // Remove '#'
      let rgb = parseInt(c, 16); // Convert hex to integer
      let r = (rgb >> 16) - 50; // Red channel
      let g = ((rgb >> 8) & 0x00FF) - 50; // Green channel
      let b = (rgb & 0x0000FF) - 50; // Blue channel

      // Limit values between 0 and 255
      r = r < 0 ? 0 : r;
      g = g < 0 ? 0 : g;
      b = b < 0 ? 0 : b;

      return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
    };

    // Helper function to lighten the color
    const lightenColor = (color) => {
      let c = color.slice(1); // Remove '#'
      let rgb = parseInt(c, 16); // Convert hex to integer
      let r = (rgb >> 16) + 50; // Red channel
      let g = ((rgb >> 8) & 0x00FF) + 50; // Green channel
      let b = (rgb & 0x0000FF) + 50; // Blue channel

      // Limit values between 0 and 255
      r = r > 255 ? 255 : r;
      g = g > 255 ? 255 : g;
      b = b > 255 ? 255 : b;

      return `#${(r << 16 | g << 8 | b).toString(16).padStart(6, '0')}`;
    };

    const isDragging = ref(false);
    const draggingPosition = ref(null);

    const rotation = ref(props.piece.rotation || 0);
    const isReflected = ref(props.piece.isReflected || false);

    const currentTransform = computed(() => {
      const snappedX = Math.round((draggingPosition.value ? draggingPosition.value.x : props.piece.position.x) / props.gridSize) * props.gridSize;
      const snappedY = Math.round((draggingPosition.value ? draggingPosition.value.y : props.piece.position.y) / props.gridSize) * props.gridSize;

      return `translate(${snappedX}, ${snappedY}) rotate(${rotation.value}) scale(${isReflected.value ? -1 : 1}, 1)`;
    });

    const onMouseDown = event => {
      event.preventDefault();
      isDragging.value = true;

      const svg = event.currentTarget.ownerSVGElement;
      const svgRect = svg.getBoundingClientRect();

      const startX = event.clientX - svgRect.left;
      const startY = event.clientY - svgRect.top;
      const initialPos = { ...props.piece.position };

      const onMouseMove = e => {
        const currentX = e.clientX - svgRect.left;
        const currentY = e.clientY - svgRect.top;

        const dx = currentX - startX;
        const dy = currentY - startY;

        draggingPosition.value = { x: initialPos.x + dx, y: initialPos.y + dy };
      };

      const onMouseUp = () => {
        isDragging.value = false;
        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);

        if (draggingPosition.value) {
          const snappedX = Math.round(draggingPosition.value.x / props.gridSize) * props.gridSize;
          const snappedY = Math.round(draggingPosition.value.y / props.gridSize) * props.gridSize;

          emit('update-piece', {
            ...props.piece,
            position: { x: snappedX, y: snappedY },
            rotation: rotation.value,
            isReflected: isReflected.value,
          });

          draggingPosition.value = null;
        }
      };

      window.addEventListener('mousemove', onMouseMove);
      window.addEventListener('mouseup', onMouseUp);
    };

    // Обработчик двойного клика для отражения фигурки
    const onDoubleClick = () => {
      isReflected.value = !isReflected.value;

      // Обновление состояния фигуры после отражения
      emit('update-piece', {
        ...props.piece,
        isReflected: isReflected.value,
      });
    };

    const onKeyDown = event => {
      if (!isDragging.value) return;
      if (event.key === 'a' || event.key === 'A') {
        rotation.value = (rotation.value - 90) % 360;
        if (rotation.value < 0) rotation.value += 360;
        emit('update-piece', {
          ...props.piece,
          rotation: rotation.value,
        });
      }
      if (event.key === 'd' || event.key === 'D') {
        rotation.value = (rotation.value + 90) % 360;
        emit('update-piece', {
          ...props.piece,
          rotation: rotation.value,
        });
      }
    };

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
      currentTransform,
      onMouseDown,
      onDoubleClick,
      darkenColor,
      lightenColor,
    };
  },
};
</script>