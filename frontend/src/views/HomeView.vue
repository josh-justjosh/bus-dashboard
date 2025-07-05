<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const departures = ref([]);
const error = ref(null);
const isFetching = ref(false);
let pollingInterval = null;

const updateKey = ref(0);

const fetchDepartures = async () => {
  if (isFetching.value) return;
  isFetching.value = true;
  error.value = null;

  try {
    const response = await fetch('http://localhost:8000/departures');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    const hasChanges = JSON.stringify(departures.value) !== JSON.stringify(data);

    departures.value = data;
    if (hasChanges) {
      updateKey.value++;
      console.log("Departures data updated, triggering animation.");
    } else {
      console.log("No significant data changes detected.");
    }

  } catch (err) {
    console.error("Error fetching departures:", err);
    error.value = "Failed to load bus departures. Please try again later. (Check backend)";
  } finally {
    isFetching.value = false;
  }
};

const startPolling = () => {
  fetchDepartures();
  pollingInterval = setInterval(fetchDepartures, 60000);
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
    <h1>Bus Departures Dashboard</h1>
    <h2>Departures:</h2>

    <p v-if="isFetching && departures.length === 0" class="loading-message">
        Initial loading of data...
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
              <tr v-for="(departure, index) in departures" :key="departure.service + departure.scheduled + departure.expected + departure.destination">
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
      <p v-else class="no-departures">No departures found.</p>
    </div>
  </main>
</template>

<style scoped>
/* Main Container Styling */
main {
  padding: 20px;
  max-width: 1200px;
  width: 100%;
  margin: 40px auto;
  color: #f0f0f0;
  background-color: #282828;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}

h1, h2 {
  color: #fff;
  text-align: center;
  margin-bottom: 25px;
  text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

/* Table Container for better overflow handling */
.table-container {
  overflow-x: auto;
  margin-top: 20px;
  border: 1px solid #444;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

/* Table Styling */
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

/* Corrected row styling for TransitionGroup */
/* Apply to tr elements directly, which are now children of TransitionGroup */
.list-move, /* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px); /* Adjust to slide from top/bottom */
}

/* Ensure leaving items take up no space and don't affect layout flow */
.list-leave-active {
  position: absolute; /* Take out of flow during animation */
  width: 100%; /* Important for absolute positioning in a table cell context */
}

/* Corrected row styling for TransitionGroup */
/* These target the <tr> elements inside the TransitionGroup */
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

/* The element that is leaving the DOM */
.list-leave-active {
  position: absolute; /* This might still cause issues for tables, as it removes from flow */
  /* Let's try an alternative for tables: height transition */
  transition: all 0.5s ease;
}
/* This often causes issues with table alignment. Let's try to remove position:absolute. */
/* Alternative for leaving elements in tables: height + opacity */
.list-leave-active {
  transition: all 0.5s ease; /* Keep the transition property */
}

/* When a row leaves, collapse its height and fade it out */
.list-leave-to {
  opacity: 0;
  height: 0 !important; /* Force height to 0 to collapse the row */
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  border-bottom: none !important;
  overflow: hidden; /* Hide content as height collapses */
}

/* Ensure rows keep their proper table-row display during transitions */
.list-item {
    display: table-row; /* Explicitly set display for table rows if needed */
}

/* Re-apply nth-of-type and hover directly to tr, as TransitionGroup will manage them */
/* Use a slightly more specific selector if necessary, but these should work */
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

/* Specific styling for 'via' and 'notes' text */
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

/* Error Message Styling */
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

/* Loading/No Departures Message Styling */
.loading-message, .no-departures {
  text-align: center;
  font-size: 1.1em;
  color: #ccc;
  margin-top: 20px;
}

/* Conditional styling for expected times */
.expected-earlier {
  color: #8bc34a;
  font-weight: bold;
}

.expected-later {
  color: #ef5350;
  font-weight: bold;
}

/* --- TransitionGroup Styles --- */
/* For elements that are entering */
.list-enter-active {
  transition: all 0.5s ease;
}

/* For elements that are leaving */
.list-leave-active {
  transition: all 0.5s ease;
  /* Use height transition for table rows to maintain alignment */
  max-height: 50px; /* Adjust based on typical row height */
  overflow: hidden;
}

/* For elements that are being moved (when items are added/removed elsewhere) */
.list-move {
  transition: transform 0.5s ease;
}

/* Initial state for entering elements */
.list-enter-from {
  opacity: 0;
  max-height: 0; /* Start with no height */
  transform: translateY(-20px); /* Optional: slight slide from top */
}

/* Final state for leaving elements */
.list-leave-to {
  opacity: 0;
  max-height: 0; /* Collapse height to 0 */
  padding-top: 0;
  padding-bottom: 0;
  border-bottom: none;
  transform: translateY(20px); /* Optional: slight slide down as it leaves */
}
</style>