<template>
  <div class="login-page">
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
    
    <div class="login-container">
      <!-- 左侧品牌区 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="50" cy="35" r="20" stroke="currentColor" stroke-width="3" fill="none"/>
              <path d="M20 85 C20 60 80 60 80 85" stroke="currentColor" stroke-width="3" fill="none"/>
              <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="2" opacity="0.3"/>
            </svg>
          </div>
          <h1 class="brand-title">人脸识别考勤系统</h1>
          <p class="brand-subtitle">Face Recognition Attendance System</p>
          <div class="brand-features">
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>智能人脸识别</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>实时考勤统计</span>
            </div>
            <div class="feature-item">
              <el-icon><Check /></el-icon>
              <span>多维度数据分析</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧登录区 -->
      <div class="form-section">
        <div class="form-wrapper">
          <div class="form-header">
            <h2>欢迎回来</h2>
            <p>请登录您的账户</p>
          </div>
          
          <el-form
            ref="formRef"
            :model="form"
            :rules="rules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                class="custom-input"
              >
                <template #prefix>
                  <el-icon class="input-icon"><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                class="custom-input"
                show-password
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon class="input-icon"><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-btn"
                @click="handleLogin"
              >
                <span v-if="!loading">登 录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="form-footer">
            <p class="login-tip">登录后可进入管理后台</p>
            <router-link to="/attendance" class="face-attendance-link">
              <el-icon><Camera /></el-icon>
              <span>人脸打卡入口</span>
            </router-link>
          </div>
        </div>
        
        <div class="copyright">
          © 2024 Face Attendance System. All rights reserved.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #0f0f23;
}

// 动态背景
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
      
      &.shape-1 {
        width: 400px;
        height: 400px;
        top: -100px;
        left: -100px;
        animation-delay: 0s;
      }
      
      &.shape-2 {
        width: 300px;
        height: 300px;
        top: 50%;
        right: -50px;
        animation-delay: -5s;
      }
      
      &.shape-3 {
        width: 200px;
        height: 200px;
        bottom: -50px;
        left: 30%;
        animation-delay: -10s;
      }
      
      &.shape-4 {
        width: 150px;
        height: 150px;
        top: 30%;
        left: 50%;
        animation-delay: -15s;
      }
    }
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(20px, -20px) rotate(5deg); }
  50% { transform: translate(-10px, 20px) rotate(-5deg); }
  75% { transform: translate(-20px, -10px) rotate(3deg); }
}

// 登录容器
.login-container {
  position: relative;
  z-index: 1;
  display: flex;
  width: 900px;
  min-height: 560px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

// 左侧品牌区
.brand-section {
  flex: 1;
  padding: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  
  .brand-content {
    text-align: center;
    color: #fff;
  }
  
  .brand-icon {
    width: 100px;
    height: 100px;
    margin: 0 auto 24px;
    color: #a78bfa;
    
    svg {
      width: 100%;
      height: 100%;
    }
  }
  
  .brand-title {
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 8px;
    background: linear-gradient(135deg, #fff, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .brand-subtitle {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 40px;
  }
  
  .brand-features {
    text-align: left;
    
    .feature-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 0;
      color: rgba(255, 255, 255, 0.8);
      font-size: 14px;
      
      .el-icon {
        width: 24px;
        height: 24px;
        background: rgba(167, 139, 250, 0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #a78bfa;
        font-size: 12px;
      }
    }
  }
}

// 右侧表单区
.form-section {
  flex: 1;
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  
  .form-wrapper {
    max-width: 320px;
    margin: 0 auto;
    width: 100%;
  }
  
  .form-header {
    margin-bottom: 32px;
    
    h2 {
      font-size: 28px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 8px;
    }
    
    p {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.5);
    }
  }
}

// 表单样式
.login-form {
  .el-form-item {
    margin-bottom: 24px;
  }
  
  .custom-input {
    :deep(.el-input__wrapper) {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 4px 16px;
      box-shadow: none;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: rgba(167, 139, 250, 0.5);
      }
      
      &.is-focus {
        border-color: #a78bfa;
        background: rgba(167, 139, 250, 0.1);
        box-shadow: 0 0 0 4px rgba(167, 139, 250, 0.1);
      }
    }
    
    :deep(.el-input__inner) {
      color: #fff;
      
      &::placeholder {
        color: rgba(255, 255, 255, 0.4);
      }
    }
    
    .input-icon {
      color: rgba(255, 255, 255, 0.5);
      font-size: 18px;
    }
  }
  
  .login-btn {
    width: 100%;
    height: 48px;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    border: none;
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 40px -10px rgba(99, 102, 241, 0.5);
    }
    
    &:active {
      transform: translateY(0);
    }
  }
}

// 表单底部
.form-footer {
  margin-top: 24px;
  text-align: center;
  
  .login-tip {
    font-size: 13px;
    color: rgba(255, 255, 255, 0.4);
    margin-bottom: 16px;
  }
  
  .face-attendance-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: rgba(167, 139, 250, 0.15);
    border: 1px solid rgba(167, 139, 250, 0.3);
    border-radius: 12px;
    color: #a78bfa;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    
    .el-icon {
      font-size: 18px;
    }
    
    &:hover {
      background: rgba(167, 139, 250, 0.25);
      border-color: rgba(167, 139, 250, 0.5);
      transform: translateY(-2px);
    }
  }
}

// 版权信息
.copyright {
  margin-top: auto;
  padding-top: 24px;
  text-align: center;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.3);
}

// 响应式
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    width: 90%;
    max-width: 400px;
    min-height: auto;
  }
  
  .brand-section {
    padding: 32px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    .brand-features {
      display: none;
    }
  }
  
  .form-section {
    padding: 32px;
  }
}
</style>
