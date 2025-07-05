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
  min-height: 100vh; /* Ensure body takes full viewport height */
  font-family: -apple-system, BlinkMacMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  /* Centering the content: Removed flexbox from here.
     The centering will now be handled by 'margin: auto' on the main content element. */
  background-color: #1a1a1a; /* Very dark background */
  color: #e0e0e0; /* Lighter text for good contrast */
}

/* Optional: Basic reset for consistency */
*, *::before, *::after {
  box-sizing: border-box;
}
</style>