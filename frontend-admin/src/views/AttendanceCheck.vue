<template>
  <div class="attendance-page">
    <!-- 动态背景 -->
    <div class="bg-animation">
      <div class="bg-gradient"></div>
      <div class="bg-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
      </div>
    </div>
    
    <div class="attendance-container">
      <!-- 头部 -->
      <div class="page-header">
        <div class="header-top">
          <div class="header-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="15" y="10" width="70" height="55" rx="8" stroke="currentColor" stroke-width="3" fill="none"/>
              <circle cx="50" cy="37" r="12" stroke="currentColor" stroke-width="3" fill="none"/>
              <circle cx="50" cy="80" r="8" stroke="currentColor" stroke-width="3" fill="none"/>
              <line x1="50" y1="65" x2="50" y2="72" stroke="currentColor" stroke-width="3"/>
            </svg>
          </div>
          <h1 class="page-title">人脸考勤</h1>
        </div>
        <p class="page-time">{{ currentTime }}</p>
      </div>
      
      <!-- 摄像头区域 -->
      <div class="camera-card">
        <div class="camera-wrapper">
          <video ref="videoRef" autoplay playsinline v-show="!capturedImage"></video>
          <canvas ref="canvasRef" style="display: none;"></canvas>
          <img v-if="capturedImage" :src="capturedImage" class="captured-image" />
          
          <!-- 加载状态 -->
          <div v-if="!cameraReady && !capturedImage" class="camera-loading">
            <div class="loading-spinner"></div>
            <p>正在启动摄像头...</p>
          </div>
          
          <!-- 人脸识别框 -->
          <div v-if="cameraReady && !capturedImage" class="face-guide">
            <div class="guide-corner tl"></div>
            <div class="guide-corner tr"></div>
            <div class="guide-corner bl"></div>
            <div class="guide-corner br"></div>
          </div>
        </div>
        
        <p class="camera-tip">请将面部对准摄像头，系统将自动识别您的身份</p>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <template v-if="!capturedImage">
            <button class="action-btn check-in" :disabled="!cameraReady || processing" @click="capture('check-in')">
              <span class="btn-icon">☀</span>
              <span class="btn-text">签到</span>
            </button>
            <button class="action-btn check-out" :disabled="!cameraReady || processing" @click="capture('check-out')">
              <span class="btn-icon">🌙</span>
              <span class="btn-text">签退</span>
            </button>
          </template>
          <template v-else>
            <button class="action-btn retry" @click="resetCapture">
              <span class="btn-icon">↻</span>
              <span class="btn-text">重新拍照</span>
            </button>
          </template>
        </div>
      </div>
      
      <!-- 结果展示 -->
      <transition name="fade">
        <div v-if="result" class="result-card" :class="result.success ? 'success' : 'error'">
          <div class="result-icon">{{ result.success ? '✓' : '✗' }}</div>
          <div class="result-content">
            <h3 class="result-title">{{ result.message }}</h3>
            <div v-if="result.data" class="result-details">
              <p><span>姓名:</span> {{ result.data.user_name }}</p>
              <p v-if="result.data.employee_no"><span>工号:</span> {{ result.data.employee_no }}</p>
              <p v-if="result.data.check_in_time"><span>签到时间:</span> {{ result.data.check_in_time }}</p>
              <p v-if="result.data.check_out_time"><span>签退时间:</span> {{ result.data.check_out_time }}</p>
              <p v-if="result.data.status"><span>状态:</span> {{ result.data.status }}</p>
            </div>
          </div>
        </div>
      </transition>
      
      <!-- 返回链接 -->
      <div class="back-link">
        <a @click="goBack"><span>←</span> {{ isLoggedIn ? '返回首页' : '返回登录' }}</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import api from '@/api'

const router = useRouter()
const userStore = useUserStore()
const videoRef = ref()
const canvasRef = ref()
const cameraReady = ref(false)
const capturedImage = ref('')
const processing = ref(false)
const result = ref(null)
const currentTime = ref('')
let stream = null
let timeInterval = null

const isLoggedIn = computed(() => userStore.isLoggedIn)

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480, facingMode: 'user' }
    })
    videoRef.value.srcObject = stream
    cameraReady.value = true
  } catch (e) {
    ElMessage.error('无法访问摄像头，请检查权限设置')
  }
}

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
}

const capture = async (type) => {
  if (!cameraReady.value) return
  const video = videoRef.value
  const canvas = canvasRef.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  const ctx = canvas.getContext('2d')
  ctx.drawImage(video, 0, 0)
  capturedImage.value = canvas.toDataURL('image/jpeg', 0.8)
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8))
  const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' })
  processing.value = true
  result.value = null
  try {
    const res = type === 'check-in' ? await api.attendance.publicCheckIn(file) : await api.attendance.publicCheckOut(file)
    result.value = { success: true, message: res.message, data: res.data }
  } catch (e) {
    result.value = { success: false, message: e.response?.data?.detail || e.response?.data?.message || '操作失败', data: null }
  } finally {
    processing.value = false
  }
}

const resetCapture = () => {
  capturedImage.value = ''
  result.value = null
}

const goBack = () => {
  if (isLoggedIn.value) {
    router.push('/')
  } else {
    router.push('/login')
  }
}

onMounted(async () => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  setTimeout(() => startCamera(), 500)
})

onUnmounted(() => {
  stopCamera()
  if (timeInterval) clearInterval(timeInterval)
})
</script>

<style lang="scss" scoped>
.attendance-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #0f0f23;
  padding: 20px;
}

.bg-animation {
  position: absolute;
  inset: 0;
  z-index: 0;
  .bg-gradient {
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(ellipse at 20% 50%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 50%, rgba(168, 85, 247, 0.15) 0%, transparent 50%),
      radial-gradient(ellipse at 50% 100%, rgba(59, 130, 246, 0.1) 0%, transparent 50%);
  }
  .bg-shapes {
    position: absolute;
    inset: 0;
    overflow: hidden;
    .shape {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.1));
      animation: float 20s ease-in-out infinite;
      &.shape-1 { width: 400px; height: 400px; top: -100px; left: -100px; }
      &.shape-2 { width: 300px; height: 300px; top: 50%; right: -50px; animation-delay: -5s; }
      &.shape-3 { width: 200px; height: 200px; bottom: -50px; left: 30%; animation-delay: -10s; }
      &.shape-4 { width: 150px; height: 150px; top: 30%; left: 50%; animation-delay: -15s; }
    }
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(20px, -20px) rotate(5deg); }
  50% { transform: translate(-10px, 20px) rotate(-5deg); }
  75% { transform: translate(-20px, -10px) rotate(3deg); }
}

.attendance-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 600px;
}

.page-header {
  text-align: center;
  margin-bottom: 24px;
  .header-top {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 4px;
  }
  .header-icon {
    width: 32px;
    height: 32px;
    color: #a78bfa;
    svg { width: 100%; height: 100%; }
  }
  .page-title {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
  }
  .page-time {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.8);
    font-variant-numeric: tabular-nums;
  }
}

.camera-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
  padding: 24px;
  margin-bottom: 24px;
}

.camera-wrapper {
  position: relative;
  background: #000;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 16px;
  video, .captured-image { width: 100%; display: block; border-radius: 16px; }
  .camera-loading {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.8);
    color: #fff;
    .loading-spinner {
      width: 48px;
      height: 48px;
      border: 3px solid rgba(167, 139, 250, 0.3);
      border-top-color: #a78bfa;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-bottom: 16px;
    }
    p { font-size: 14px; color: rgba(255, 255, 255, 0.85); }
  }
  .face-guide {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 200px;
    height: 260px;
    pointer-events: none;
    .guide-corner {
      position: absolute;
      width: 30px;
      height: 30px;
      border-color: #a78bfa;
      border-style: solid;
      border-width: 0;
      &.tl { top: 0; left: 0; border-top-width: 3px; border-left-width: 3px; border-radius: 8px 0 0 0; }
      &.tr { top: 0; right: 0; border-top-width: 3px; border-right-width: 3px; border-radius: 0 8px 0 0; }
      &.bl { bottom: 0; left: 0; border-bottom-width: 3px; border-left-width: 3px; border-radius: 0 0 0 8px; }
      &.br { bottom: 0; right: 0; border-bottom-width: 3px; border-right-width: 3px; border-radius: 0 0 8px 0; }
    }
  }
}

.camera-tip {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 20px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  .action-btn {
    flex: 1;
    max-width: 180px;
    height: 56px;
    border: none;
    border-radius: 16px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: all 0.3s ease;
    .btn-icon { font-size: 20px; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
    &.check-in {
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      &:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 40px -10px rgba(16, 185, 129, 0.5); }
    }
    &.check-out {
      background: linear-gradient(135deg, #f59e0b, #d97706);
      color: #fff;
      &:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 10px 40px -10px rgba(245, 158, 11, 0.5); }
    }
    &.retry {
      background: rgba(255, 255, 255, 0.1);
      border: 1px solid rgba(255, 255, 255, 0.2);
      color: #fff;
      max-width: 200px;
      &:hover { background: rgba(255, 255, 255, 0.15); border-color: rgba(167, 139, 250, 0.5); }
    }
  }
}

.result-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  .result-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    flex-shrink: 0;
  }
  .result-content {
    flex: 1;
    .result-title { font-size: 18px; font-weight: 600; color: #fff; margin-bottom: 8px; }
    .result-details p {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.85);
      margin: 4px 0;
      span { color: rgba(255, 255, 255, 0.6); margin-right: 8px; }
    }
  }
  &.success {
    border-color: rgba(16, 185, 129, 0.4);
    .result-icon { background: rgba(16, 185, 129, 0.25); color: #6ee7b7; }
  }
  &.error {
    border-color: rgba(239, 68, 68, 0.4);
    .result-icon { background: rgba(239, 68, 68, 0.25); color: #fca5a5; }
  }
}

.back-link {
  text-align: center;
  a {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: rgba(255, 255, 255, 0.75);
    font-size: 15px;
    cursor: pointer;
    transition: color 0.3s ease;
    &:hover { color: #a78bfa; }
    span { font-size: 18px; }
  }
}

.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
