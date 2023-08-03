<template>
  <v-layout>
    <PCNavigator/>
    <v-main class="fill-height">
      <router-view />
    </v-main>

  </v-layout>
</template>

<style scoped>
.v-layout {
  background-color: #dae4f5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.mobile-copyright {
  white-space: pre-line;
}
</style>

<script lang="ts" setup>
import PCNavigator from "./components/PCNavigator.vue";
import router from "./router";
import { init } from "./services/Database";

router.beforeResolve((to, from, next) => {
  if (to.meta?.name) {
    document.title = to.meta.name + " - 企鹅弹幕机";
  }
  next();
});

var url = new URL(document.URL);
init(url.searchParams.get("token") as string).then(() => console.log('[Database] Connected'))

</script>
