<template>
  <v-app>
    <AppNavbar />
    <v-main>
      <router-view />
    </v-main>
    <AppFooter />
  </v-app>
</template>

<script>
import AppNavbar from './components/Navbar.vue';
import AppFooter from './components/Footer.vue';

export default {
  name: 'App',
  components: {
    AppNavbar,
    AppFooter
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.v-main {
  flex: 1;
  padding: 20px 0;
}
</style>

