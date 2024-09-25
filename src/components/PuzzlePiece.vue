<!-- src/components/PuzzlePiece.vue -->
<template>
  <svg
    :width="width"
    :height="height"
    :style="{ overflow: 'visible' }"
  >
    <g :transform="'rotate(' + (piece.rotation || 0) + ' ' + centerX + ' ' + centerY + ')'">
      <rect
        v-for="(block, index) in piece.shape"
        :key="index"
        :x="block.x * cellSize"
        :y="block.y * cellSize"
        :width="cellSize"
        :height="cellSize"
        :fill="piece.color"
        stroke="#000"
      />
    </g>
  </svg>
</template>

<script>
export default {
  name: 'PuzzlePiece',
  props: {
    piece: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      cellSize: 30, // Размер одного блока в пикселях
    };
  },
  computed: {
    width() {
      const xs = this.piece.shape.map((block) => block.x);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      return (maxX - minX + 1) * this.cellSize;
    },
    height() {
      const ys = this.piece.shape.map((block) => block.y);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);
      return (maxY - minY + 1) * this.cellSize;
    },
    centerX() {
      return this.width / 2;
    },
    centerY() {
      return this.height / 2;
    },
  },
};
</script>

<style scoped>
svg {
  overflow: visible;
}
</style>
