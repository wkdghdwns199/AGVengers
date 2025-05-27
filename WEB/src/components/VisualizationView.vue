<script setup>
import { ref, onMounted } from "vue";
import {
  collection,
  query,
  where,
  onSnapshot,
  getDocs,
  Timestamp,
} from "firebase/firestore";
import { db } from "../firebase";

import GaugeChart from "./GaugeChart.vue";
import FleetMapChart from "./FleetMapChart.vue";

const classificationProgress = ref(0);
const todayLogCount = ref(0);
const recentLogs = ref([]);
const warehouseCounts = ref({});

const fetchActivityData = async () => {
  const activityColRef = collection(db, "auto_activities");
  const volumeColRef = collection(db, "logistics_volume");

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(today.getDate() + 1);

  // const todayTimestamp = today.getTime();
  const todayUtc = new Date(
    Date.UTC(today.getFullYear(), today.getMonth(), today.getDate())
  );
  const todayTimestamp = todayUtc.getTime();

  // auto_activities 실시간 구독
  onSnapshot(activityColRef, async (querySnapshot) => {
    const dropsByWarehouse = {
      red: 0,
      blue: 0,
      green: 0,
      yellow: 0,
      purple: 0,
      orange: 0,
    };
    let totalDropsToday = 0;
    const logs = [];

    querySnapshot.forEach((doc) => {
      const data = doc.data();
      if (!data.command) return;

      let timeStamp = 0;
      if (data.time?.toDate) {
        timeStamp = data.time.toDate().getTime();
      } else {
        timeStamp = new Date(data.time).getTime();
      }

      logs.push({
        id: doc.id,
        receive_IP: data.receive_IP,
        command: data.command,
        dest_color: data.dest_color,
        time: data.time,
      });

      if (data.command === "drop") {
        if (timeStamp >= todayTimestamp) {
          totalDropsToday++;
          dropsByWarehouse[data.dest_color]++;
        }
      }
    });

    // logistics_volume 컬렉션에서 오늘 날짜 범위 쿼리
    const volumeQuery = query(
      volumeColRef,
      where("date", ">=", Timestamp.fromDate(today)),
      where("date", "<", Timestamp.fromDate(tomorrow))
    );
    const volumeSnapshot = await getDocs(volumeQuery);

    let todayVolume = 0;
    volumeSnapshot.forEach((doc) => {
      const data = doc.data();
      todayVolume = data.volume || 0;
    });

    const progressValue =
      todayVolume > 0
        ? Math.min(100, Math.round((totalDropsToday / todayVolume) * 100))
        : 0;

    classificationProgress.value = progressValue;
    todayLogCount.value = totalDropsToday;
    recentLogs.value = logs.sort((a, b) => {
      const timeA =
        typeof a.time?.toDate === "function"
          ? a.time.toDate().getTime()
          : new Date(a.time).getTime();
      const timeB =
        typeof b.time?.toDate === "function"
          ? b.time.toDate().getTime()
          : new Date(b.time).getTime();
      return timeB - timeA;
    });
    warehouseCounts.value = dropsByWarehouse;
  });
};

onMounted(fetchActivityData);
</script>

<template>
  <div class="container">
    <h1>
      <img class="logo" src="../assets/agv_logo.png" alt="AGVengers Logo" />
      AGVengers - 물류 현황 대시보드
    </h1>
    <div class="main-content">
      <!-- 왼쪽: 게이지 + 오늘 물류량 + 최근 로그 -->
      <div class="left-panel">
        <div class="gauge-wrapper">
          <GaugeChart :progress="classificationProgress" />
          <div class="gauge-label">분류 진행도</div>
        </div>
        <div class="info-row">
          <div class="today-volume">
            <h3>금일 물류량 (Drop)</h3>
            <div class="count">{{ todayLogCount }}</div>
          </div>
          <div class="recent-logs">
            <h3>최근 추가 로그</h3>
            <ul>
              <li v-for="log in recentLogs" :key="log.id">
                <strong>
                  {{
                    typeof log.time === "string"
                      ? log.time.slice(11, 19)
                      : log.time.toDate().toISOString().slice(11, 19)
                  }}:
                </strong>
                {{ log.receive_IP }} - {{ log.command }} - {{ log.dest_color }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 지도 -->
      <div class="right-panel">
        <FleetMapChart :warehouseData="warehouseCounts" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.logo {
  height: 2.2em;
  vertical-align: middle;
  margin-right: 0.6em;
}

.container {
  width: 95vw;
  height: 90vh;
  max-height: 90vh;
  margin: 1rem auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: Arial, sans-serif;
}

.main-content {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 1rem;
}

.left-panel {
  /* width: 570px; */
  width: 30%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-sizing: border-box;
  height: 100%;
}

.gauge-wrapper {
  height: 400px;
  width: 100%;
  background: white;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.gauge-label {
  margin-top: 0.5rem;
  font-weight: 600;
  color: #444;
}

.info-row {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.today-volume {
  background: #ececec;
  border-radius: 12px;
  padding: 1rem;
  text-align: center;
  font-weight: bold;
  font-size: 1.1rem;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.05);
  width: 100% !important;
  min-width: 0;
  box-sizing: border-box;
  word-break: break-word;
}

.recent-logs {
  background: #fafafa;
  border-radius: 12px;
  padding: 1rem;
  overflow-y: auto;
  flex-grow: 1;
  box-shadow: inset 0 0 5px rgba(0, 0, 0, 0.05);
  width: 100% !important;
  min-width: 0;
  box-sizing: border-box;
  word-break: break-word;
}

.recent-logs h3 {
  margin-bottom: 1rem;
  font-weight: 600;
}

.recent-logs ul {
  list-style-type: none;
  margin: 0;
  padding-left: 0;
}

.recent-logs li {
  margin-bottom: 0.6rem;
  font-size: 0.9rem;
  color: #444;
}

.right-panel {
  /* width: calc(100% - 580px); */
  width: 70%;
  padding: 0.5rem;
  background: white;
  border-radius: 12px;
  box-sizing: border-box;
  overflow: hidden;
  display: flex;
  height: 100%;
}
</style>
