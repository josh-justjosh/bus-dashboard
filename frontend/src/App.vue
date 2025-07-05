<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* Global Styles for the entire application */
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100vh; /* Set height to 100% of viewport height (not min-height) */
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  /* Centering the content */
  display: flex;
  flex-direction: column; /* Use flexbox to stack vertically */
  justify-content: center; /* Horizontally center */
  align-items: flex-start; /* Align content to the top (vertically) */
  background-color: #1a1a1a; /* Very dark background */
  color: #e0e0e0; /* Lighter text for good contrast */
  box-sizing: border-box; /* Ensure padding/border are included in element's total width/height */
}

#app {
  width: 100%; /* Take full width of body */
  height: 100%; /* Take full height of body */
  padding: 0; /* Remove padding here, as it will be managed by inner components */
  font-weight: normal;

  /* Add flex to #app to correctly distribute its children (the RouterView content) */
  display: flex;
  flex-direction: column;
  align-items: center; /* Center content horizontally within #app */
  box-sizing: border-box; /* Ensure padding/border are included in element's total width/height */
}

/* Optional: Basic reset for consistency */
*, *::before, *::after {
  box-sizing: border-box;
}
</style>