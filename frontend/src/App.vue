<template>
  <div id="app">
    <AppNavbar />  <!-- ✅ 변경된 이름 적용 -->
    <router-view />
  </div>
</template>

<script>
import AppNavbar from './components/Navbar.vue'; // ✅ 올바른 import

export default {
  name: 'App',
  components: {
    AppNavbar  // ✅ 올바른 컴포넌트 등록
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

