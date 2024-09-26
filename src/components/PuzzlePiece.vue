<template>
  <svg
    :width="width"
    :height="height"
    :style="{ overflow: 'visible' }"
  >
    <g>
      <rect
        v-for="(block, index) in adjustedRotatedShape"
        :key="index"
        :x="(block.x - minX) * cellSize"
        :y="(block.y - minY) * cellSize"
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
      cellSize: 30,
    };
  },
  computed: {
    rotation() {
      return this.piece.rotation || 0;
    },
    rotatedShape() {
      return this.piece.shape.map((block) => this.getRotatedBlock(block, this.rotation));
    },
    xs() {
      return this.rotatedShape.map((block) => block.x);
    },
    ys() {
      return this.rotatedShape.map((block) => block.y);
    },
    minX() {
      return Math.min(...this.xs);
    },
    minY() {
      return Math.min(...this.ys);
    },
    maxX() {
      return Math.max(...this.xs);
    },
    maxY() {
      return Math.max(...this.ys);
    },
    width() {
      return (this.maxX - this.minX + 1) * this.cellSize;
    },
    height() {
      return (this.maxY - this.minY + 1) * this.cellSize;
    },
    adjustedRotatedShape() {
      // Adjust the rotated shape to start from (minX, minY)
      return this.rotatedShape;
    },
  },
  methods: {
    getRotatedBlock(block, angle) {
      angle = (angle % 360 + 360) % 360; // Normalize angle
      const radians = (Math.PI / 180) * angle;
      const cos = Math.cos(radians);
      const sin = Math.sin(radians);
      const x = block.x * cos - block.y * sin;
      const y = block.x * sin + block.y * cos;
      return { x: Math.round(x), y: Math.round(y) };
    },
  },
};
</script>

<style scoped>
svg {
  overflow: visible;
}
</style>
