<script setup>
import { computed } from "vue";

const props = defineProps({
  progress: { type: Number, default: 50, required: true },
});

const barColor = "#4677f5";

const arcPath = computed(() => {
  const angle = (props.progress * 180) / 100;
  const rad = (angle * Math.PI) / 180;

  const cx = 240;
  const cy = 280;
  const r = 200;

  const startX = cx - r;
  const startY = cy;

  const endX = cx + r * Math.cos(rad - Math.PI);
  const endY = cy + r * Math.sin(rad - Math.PI);

  const largeArc = angle > 180 ? 1 : 0;

  return `M ${startX} ${startY} A ${r} ${r} 0 ${largeArc} 1 ${endX} ${endY}`;
});
</script>

<template>
    <div class="gauge-container">
      <svg viewBox="0 0 480 300" width="480" height="300">
        <!-- 배경 원호 -->
        <path
          d="M40 280 A200 200 0 0 1 440 280"
          stroke="#eee"
          stroke-width="30"
          fill="none"
          stroke-linecap="round"
        />
        <!-- 진행도 원호 -->
        <path
          :stroke="barColor"
          stroke-width="30"
          fill="none"
          :d="arcPath"
          stroke-linecap="round"
        />
        <!-- 중앙 텍스트 -->
        <text x="240" y="230" text-anchor="middle" font-weight="bold" font-size="100" >
            <tspan>{{ progress }}</tspan><tspan font-size="50">%</tspan>
        </text>
      </svg>
    </div>
  </template>
  

  
  <style scoped>
  .gauge-container {
    display: flex;
    justify-content: center;
    align-items: center;
  }
  </style>