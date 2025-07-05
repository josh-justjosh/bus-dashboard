import { createRouter, createWebHistory } from 'vue-router';
import CyclingHomeView from '../views/CyclingHomeView.vue'; // New cycling home page
import CathedralQuarter from '../views/CathedralQuarter.vue'; // Direct Cathedral Quarter view
import BusStation from '../views/BusStation.vue';           // Direct Bus Station view

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: CyclingHomeView // Set the cycling view as the default home page
    },
    {
      path: '/cq',
      name: 'cathedralQuarter',
      component: CathedralQuarter // Direct link to Cathedral Quarter
    },
    {
      path: '/bs',
      name: 'busStation',
      component: BusStation // Direct link to Bus Station
    }
    // You can add more routes here if needed in the future
  ]
});

export default router;