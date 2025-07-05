<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const departures = ref([]);
const error = ref(null);
const isFetching = ref(false);
let pollingInterval = null;

const updateKey = ref(0); // Used to force TransitionGroup re-render on data change

const fetchDepartures = async () => {
  if (isFetching.value) return; // Prevent multiple simultaneous fetches
  isFetching.value = true;
  error.value = null;

  try {
    const response = await fetch('http://localhost:8000/departures/bus_station');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    const hasChanges = JSON.stringify(departures.value) !== JSON.stringify(data);

    departures.value = data;
    if (hasChanges) {
      updateKey.value++; // Increment key to re-render TransitionGroup and trigger animations
      console.log("Bus Station departures data updated, triggering animation.");
    } else {
      console.log("No significant data changes detected for Bus Station.");
    }

  } catch (err) {
    console.error("Error fetching Bus Station departures:", err);
    error.value = "Failed to load Bus Station departures. Please try again later. (Check backend)";
  } finally {
    isFetching.value = false;
  }
};

const startPolling = () => {
  fetchDepartures(); // Initial fetch
  pollingInterval = setInterval(fetchDepartures, 60000); // Poll every 60 seconds
};

onMounted(() => {
  startPolling();
});

onUnmounted(() => {
  if (pollingInterval) {
    clearInterval(pollingInterval);
  }
});

watch(departures, (newVal, oldVal) => {
  // Can be used for more complex comparison or reactions if needed.
});
</script>

<template>
  <main>
    <h1>Bus Station Departures</h1>
    <h2>Current Departures:</h2>

    <p v-if="isFetching && departures.length === 0" class="loading-message">
        Initial loading of Bus Station data...
    </p>
    <p v-else-if="error" class="error-message">{{ error }}</p>

    <div v-else>
      <div v-if="departures.length > 0" class="table-container">
        <table>
          <thead>
            <tr>
              <th>Stop</th>
              <th>Service</th>
              <th>Destination</th>
              <th>Scheduled</th>
              <th>Expected</th>
              <th>Operator</th>
            </tr>
          </thead>
          <TransitionGroup name="list" tag="tbody" :key="updateKey">
              <tr v-for="(departure, index) in departures" :key="departure.service + departure.scheduled + departure.expected + departure.destination + index">
                  <td>{{ departure.stop ? (departure.stop.icon || departure.stop.indicator || departure.stop.bay) : '' }}</td>
                  <td>{{ departure.service }}</td>
                  <td>
                      {{ departure.destination }}
                      <span v-if="departure.via" class="via-text">via {{ departure.via }}</span>
                      <span v-if="departure.notes" class="notes-text">{{ departure.notes }}</span>
                  </td>
                  <td>{{ departure.scheduled }}</td>
                  <td :class="{'expected-earlier': departure.expected_dt < departure.scheduled_dt, 'expected-later': departure.expected_dt > departure.scheduled_dt && departure.expected_dt - departure.scheduled_dt > 1 * 60 * 1000}">
                      {{ departure.expected || 'N/A' }}
                  </td>
                  <td>{{ departure.operator }}</td>
              </tr>
          </TransitionGroup>
        </table>
      </div>
      <p v-else class="no-departures">No departures found for Bus Station.</p>
    </div>
  </main>
</template>

<style scoped>
/* Main Container Styling - copied from CathedralQuarter.vue for consistency */
main {
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  /* Removed: margin: 40px auto; */

  color: #f0f0f0;
  background-color: #282828;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);

  /* NEW: Make main a flex container to manage its internal height */
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* Allow it to grow within .component-display */
  min-height: 0; /* Important for flex items to shrink */
}

h1, h2 {
  color: #fff;
  text-align: center;
  margin-bottom: 25px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

.table-container {
  overflow-x: auto;
  overflow-y: hidden; /* Hide vertical overflow */
  margin-top: 20px;
  border: 1px solid #444;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);

  /* NEW: Adjusted max-height to show more rows */
  max-height: 650px; /* Increased from 600px, consistent with CathedralQuarter.vue */
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95em;
  min-width: 700px;
}

th, td {
  padding: 14px 18px;
  text-align: left;
  border-bottom: 1px solid #3a3a3a;
  white-space: nowrap;
}

th {
  background-color: #333;
  font-weight: bold;
  color: #e0e0e0;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

tr:nth-of-type(even) {
  background-color: #2e2e2e;
}

tr:hover {
  background-color: #3b3b3b;
}

td:first-child, th:first-child {
  padding-left: 25px;
}
td:last-child, th:last-child {
  padding-right: 25px;
}

.via-text {
  display: block;
  font-style: italic;
  font-size: 0.85em;
  color: #bbb;
  margin-top: 3px;
}

.notes-text {
  display: block;
  font-size: 0.8em;
  color: #aaa;
  margin-top: 3px;
}

.error-message {
  color: #ff8a80;
  background-color: #420000;
  border: 1px solid #7f0000;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  margin-top: 20px;
}

.loading-message, .no-departures {
  text-align: center;
  font-size: 1.1em;
  color: #ccc;
  margin-top: 20px;
}

.expected-earlier {
  color: #8bc34a;
  font-weight: bold;
}

.expected-later {
  color: #ef5350;
  font-weight: bold;
}

/* --- TransitionGroup Styles --- */
.list-enter-active {
  transition: all 0.5s ease;
}

.list-leave-active {
  transition: all 0.5s ease;
  max-height: 50px;
  overflow: hidden;
}

.list-move {
  transition: transform 0.5s ease;
}

.list-enter-from {
  opacity: 0;
  max-height: 0;
  transform: translateY(-20px);
}

.list-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  border-bottom: none;
  transform: translateY(20px);
}
</style>