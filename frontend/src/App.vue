<script setup lang="ts">
const nav = ['首页聚合', '我的冰箱', '食谱库', '我的食谱', '卷宗']
</script>

<template>
  <header class="nav">
    <span class="logo">剩宴事务所</span>
    <nav>
      <a v-for="n in nav" :key="n" href="#">{{ n }}</a>
    </nav>
    <span class="user">👤</span>
  </header>
  <main class="main">
    <h1>剩宴事务所</h1>
    <p>家庭食材管理 + AI 菜谱推荐 · V1 脚手架就位</p>
    <p class="hint">后端 /health：<a href="/api/health">/api/health</a></p>
  </main>
</template>

<style>
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, -apple-system, sans-serif; color: #222; }
.nav {
  display: flex; gap: 1rem; align-items: center;
  padding: 1rem 1.5rem; border-bottom: 1px solid #eee;
}
.logo { font-weight: 700; }
.nav nav { display: flex; gap: 1rem; flex: 1; }
.nav nav a { color: #555; text-decoration: none; }
.nav .user { margin-left: auto; }
.main { padding: 2rem 1.5rem; }
.hint { color: #888; font-size: 0.9rem; }
</style>
