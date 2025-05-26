<template>
  <div class="map-container">
    <svg
      viewBox="0 0 500 500"
      width="100%"
      height="100%"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- 트랙 경로 -->
      <path
        d="
          M 100 100
          H 400
          A 40 40 0 0 1 440 140
          V 360
          A 40 40 0 0 1 400 400
          H 100
          A 40 40 0 0 1 60 360
          V 140
          A 40 40 0 0 1 100 100
          Z
        "
        stroke="black"
        stroke-width="12"
        fill="none"
        stroke-linejoin="round"
        stroke-linecap="round"
      />

      <!-- 창고 위치와 원 -->
      <g v-for="(count, color) in warehouseData" :key="color">
        <rect
          :x="positions[color]?.x"
          :y="positions[color]?.y"
          width="50"
          height="50"
          :fill="color"
          stroke="#333"
          stroke-width="2"
          rx="8"
          ry="8"
          opacity="1"
        />
        <text
          :x="positions[color]?.x + 25"
          :y="positions[color]?.y + 27"
          font-size="20"
          font-weight="bold"
          fill="white"
          text-anchor="middle"
          dominant-baseline="middle"
        >
          {{ count }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { reactive } from "vue";

const props = defineProps({
  warehouseData: {
    type: Object,
    default: () => ({}),
  },
});

// 이미지 기준 창고 위치 좌표 (SVG 500x500 기준)
const positions = reactive({
  orange: { x: 220, y: 75 }, // 위쪽 중앙 (주황)
  green: { x: 35, y: 160 }, // 좌측 상단 (초록)
  purple: { x: 35, y: 290 }, // 좌측 하단 (보라)
  blue: { x: 130, y: 375 }, // 하단 왼쪽 (파랑)
  red: { x: 300, y: 375 }, // 하단 오른쪽 (빨강)
  yellow: { x: 415, y: 220 }, // 우측 중앙 (노랑)
});
</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  background-color: white;
  user-select: none;
}
</style>
