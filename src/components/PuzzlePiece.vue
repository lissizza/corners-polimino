<template>
  <g :transform="currentTransform" @mousedown="onMouseDown" @dblclick="onDoubleClick" pointer-events="all">
    <defs>
      <radialGradient
        v-for="(block, index) in piece.shape"
        :key="index"
        :id="'gradient-' + piece.id + '-' + index"
        cx="50%"
        cy="50%"
        r="100%"
      >
        <stop offset="25%" :stop-color="piece.color" />
        <stop offset="95%" stop-color="#000" />
      </radialGradient>
    </defs>

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
    };
  },
};
</script>
