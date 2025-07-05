<script setup>
import { ref, onMounted, onUnmounted, shallowRef, computed } from 'vue';
import CathedralQuarter from './CathedralQuarter.vue';
import BusStation from './BusStation.vue';

// Use shallowRef for component instances to avoid unnecessary deep reactivity
const currentViewComponent = shallowRef(CathedralQuarter);
// Removed currentViewName as it's no longer displayed
let cycleInterval = null;
const cycleDuration = 15000; // 15 seconds

// For progress bar:
const remainingTime = ref(cycleDuration); // Milliseconds, starts full
let progressInterval = null; // New interval for very frequent progress bar updates

// Computed property to calculate the width percentage for the progress bar
const progressWidth = computed(() => {
  return (remainingTime.value / cycleDuration) * 100;
});

const startCycling = () => {
  stopCycling(); // Clear any existing intervals to prevent duplicates

  // Initialize remaining time and start the progress bar update interval
  remainingTime.value = cycleDuration;
  progressInterval = setInterval(() => {
    remainingTime.value -= 50; // Update every 50ms for a smoother bar animation
    if (remainingTime.value <= 0) {
      remainingTime.value = cycleDuration; // Reset when time runs out (will be immediately reset by cycleInterval too)
    }
  }, 50); // This interval runs frequently to update the bar smoothly

  // Start the component cycling
  cycleInterval = setInterval(() => {
    if (currentViewComponent.value === CathedralQuarter) {
      currentViewComponent.value = BusStation;
    } else {
      currentViewComponent.value = CathedralQuarter;
    }
    // Reset remaining time when component switches, causing the progress bar to restart
    remainingTime.value = cycleDuration;
    // console.log(`Switched view.`); // Removed specific name logging as text is gone
  }, cycleDuration);
};

const stopCycling = () => {
  if (cycleInterval) {
    clearInterval(cycleInterval);
  }
  if (progressInterval) { // Clear the progress bar interval
    clearInterval(progressInterval);
  }
};

// Start cycling when the component is mounted
onMounted(() => {
  startCycling();
});

// Stop cycling when the component is unmounted to prevent memory leaks
onUnmounted(() => {
  stopCycling();
});
</script>

<template>
  <div class="cycling-home-view">
    <header class="dashboard-header">
      <h1>Derby Bus Departures</h1>
      </header>
    <main class="component-display">
      <component :is="currentViewComponent" />
    </main>
    <div class="progress-bar-container">
      <div class="progress-bar" :style="{ width: progressWidth + '%' }"></div>
    </div>
  </div>
</template>

<style scoped>
.cycling-home-view {
  display: flex;
  flex-direction: column;
  width: 100%;
  align-items: center;
  padding: 20px; /* Overall padding for the view */
  min-height: 100vh; /* Make sure it takes full viewport height */
  justify-content: space-between; /* Distributes space: header top, content middle, progress bar bottom */
  box-sizing: border-box; /* Include padding in element's total width and height */
}

.dashboard-header {
  text-align: center;
  margin-bottom: 30px;
  background-color: #1a1a1a;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  width: fit-content;
  max-width: 90%;
  margin-left: auto;
  margin-right: auto;
}

.dashboard-header h1 {
  color: #42b983; /* Green accent color */
  margin-bottom: 0; /* No margin below h1 as the info paragraph is removed */
  font-size: 2.5em;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

/* Removed styles for .current-view-info, .view-name, .countdown */

.component-display {
  width: 100%;
  display: flex;
  justify-content: center;
  flex-grow: 1; /* Allows the component area to expand and take available vertical space */
  margin-bottom: 20px; /* Space between the main content and the progress bar */
}

/* NEW: Progress Bar Styles */
.progress-bar-container {
  width: 90%; /* Match the width of your main content area */
  max-width: 1200px; /* Match the max-width of your main content area */
  height: 8px; /* Height of the progress bar */
  background-color: #333; /* Background color of the bar track */
  border-radius: 4px; /* Rounded corners for the bar */
  overflow: hidden; /* Ensures the inner bar doesn't overflow its container */
  margin-top: 20px; /* Space from the content above */
  box-shadow: 0 2px 5px rgba(0,0,0,0.5); /* Subtle shadow for depth */
}

.progress-bar {
  height: 100%;
  background-color: #42b983; /* Fill color of the progress bar */
  width: 100%; /* Starts at 100% and decreases */
  transition: width 0.05s linear; /* Smooth transition for width changes */
}
</style>