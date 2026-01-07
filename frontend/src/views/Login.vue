<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAuthStore } from '../stores/auth'

const password = ref('')
const loading = ref(false)
const error = ref(false)
const router = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  if (!password.value) {
    return
  }

  loading.value = true
  error.value = false

  try {
    const success = await authStore.login(password.value)
    if (success) {
      toast.success('Access Granted')
      router.replace('/')
    }
    else {
      error.value = true
      password.value = ''
      //   toast.error('Invalid Passcode') // 在命令请求的时候自动返回了错误信息

      // 这里的 shake 动画通过 class 类名触发，需要在 CSS 或 Tailwind config 中定义
      // 简单起见，我们重置 error 状态以允许下次触发动画（如果需要）
      setTimeout(() => error.value = false, 500)
    }
  }
  catch {
    error.value = true
  }
  finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 flex items-center justify-center bg-gray-950 text-gray-100 selection:bg-white/20 selection:text-white">
    <!-- 背景装饰 -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-[20%] -left-[10%] w-[50%] h-[50%] bg-blue-500/5 blur-[120px] rounded-full" />
      <div class="absolute bottom-[10%] right-[10%] w-[30%] h-[30%] bg-purple-500/5 blur-[100px] rounded-full" />
    </div>

    <div class="w-full max-w-sm px-8 space-y-12 relative z-10">
      <!-- Logo / Title -->
      <div class="text-center space-y-3">
        <h1 class="text-3xl font-light tracking-[0.2em] text-white/90 font-serif">
          GLEAN
        </h1>
        <div class="h-px w-12 bg-white/20 mx-auto" />
      </div>

      <!-- Input Area -->
      <div class="relative group">
        <input
          v-model="password"
          autofocus
          type="password"
          placeholder="ENTER PASSCODE"
          class="w-full bg-transparent border-b border-white/20 py-4 text-center text-xl tracking-[0.5em]
                 outline-none transition-all duration-300
                 placeholder:text-white/10 placeholder:tracking-widest placeholder:text-sm
                 focus:border-white/60 focus:bg-white/5"
          :class="{ 'border-red-500/50 text-red-400': error }"
          @keydown.enter="handleLogin"
        >

        <!-- Loading Indicator -->
        <div v-if="loading" class="absolute right-0 top-1/2 -translate-y-1/2">
          <div class="w-5 h-5 border-2 border-white/20 border-t-white/80 rounded-full animate-spin" />
        </div>
      </div>

      <!-- Footer Hint -->
      <div class="text-center opacity-0 transition-opacity duration-700 delay-500" :class="{ 'opacity-30': !loading }">
        <p class="text-xs tracking-widest font-light">
          PRESS ENTER TO UNLOCK
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-4px); }
  20%, 40%, 60%, 80% { transform: translateX(4px); }
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}
</style>
