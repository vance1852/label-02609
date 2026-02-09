<template>
  <div class="users-page">
    <div class="page-header">
      <h2 class="page-title">员工管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加员工
      </el-button>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索姓名/工号/用户名"
          clearable
          style="width: 240px"
          @clear="fetchUsers"
          @keyup.enter="fetchUsers"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="fetchUsers">搜索</el-button>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      
      <el-table :data="users" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="employee_no" label="工号" min-width="80" align="center" />
        <el-table-column prop="real_name" label="姓名" min-width="80" align="center" />
        <el-table-column prop="username" label="用户名" min-width="100" align="center" />
        <el-table-column prop="department_name" label="部门" min-width="100" align="center">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="has_face" label="人脸" min-width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.has_face ? 'success' : 'info'" size="small">
              {{ row.has_face ? '已录入' : '未录入' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" min-width="60" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="220" align="center" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" plain @click="openFaceDialog(row)">
              {{ row.has_face ? '更换照片' : '录入人脸' }}
            </el-button>
            <el-button size="small" type="warning" plain @click="openDialog(row)">编辑</el-button>
            <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchUsers"
      />
    </div>
    
    <!-- 用户表单弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑员工' : '添加员工'" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="isEdit" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" :prop="isEdit ? '' : 'password'">
          <el-input v-model="form.password" type="password" :placeholder="isEdit ? '留空则不修改' : '请输入密码'" show-password />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="工号" prop="employee_no">
          <el-input v-model="form.employee_no" :disabled="isEdit" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="部门" prop="department_id">
          <el-select v-model="form.department_id" placeholder="请选择部门" clearable style="width: 100%">
            <el-option v-for="d in departments" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isEdit" label="状态">
          <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 人脸录入弹窗 -->
    <el-dialog v-model="faceDialogVisible" :title="currentUser?.has_face ? '更换人脸照片' : '录入人脸'" width="500px" destroy-on-close>
      <div class="face-upload-content">
        <p class="upload-info">员工: {{ currentUser?.real_name }} ({{ currentUser?.employee_no }})</p>
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept="image/*"
          :on-change="handleFileChange"
          :on-exceed="() => ElMessage.warning('只能上传一张图片')"
          drag
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">请上传清晰的正面人脸照片，支持 jpg/png 格式</div>
          </template>
        </el-upload>
        <div v-if="previewUrl" class="preview-image">
          <img :src="previewUrl" />
        </div>
      </div>
      <template #footer>
        <el-button @click="faceDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" :disabled="!selectedFile" @click="handleUploadFace">
          上传
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Search, Plus } from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const users = ref([])
const departments = ref([])
const searchKeyword = ref('')
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  id: null,
  username: '',
  password: '',
  real_name: '',
  employee_no: '',
  department_id: null,
  role: 'user',
  is_active: true
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  employee_no: [{ required: true, message: '请输入工号', trigger: 'blur' }]
}

const faceDialogVisible = ref(false)
const currentUser = ref(null)
const selectedFile = ref(null)
const previewUrl = ref('')
const uploading = ref(false)

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await api.users.list({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchKeyword.value || undefined
    })
    users.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const res = await api.departments.all()
    departments.value = res.data
  } catch (e) {}
}

const resetSearch = () => {
  searchKeyword.value = ''
  pagination.page = 1
  fetchUsers()
}

const openDialog = (row = null) => {
  isEdit.value = !!row
  if (row) {
    Object.assign(form, { ...row, password: '' })
  } else {
    Object.assign(form, {
      id: null, username: '', password: '', real_name: '',
      employee_no: '', department_id: null, role: 'user', is_active: true
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      const data = { ...form }
      if (!data.password) delete data.password
      await api.users.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await api.users.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定删除员工 ${row.real_name} 吗？`, '提示', { type: 'warning' })
  await api.users.delete(row.id)
  ElMessage.success('删除成功')
  fetchUsers()
}

const openFaceDialog = (row) => {
  currentUser.value = row
  selectedFile.value = null
  previewUrl.value = ''
  faceDialogVisible.value = true
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  previewUrl.value = URL.createObjectURL(file.raw)
}

const handleUploadFace = async () => {
  if (!selectedFile.value) return
  uploading.value = true
  try {
    await api.users.uploadFace(currentUser.value.id, selectedFile.value)
    ElMessage.success('人脸录入成功')
    faceDialogVisible.value = false
    fetchUsers()
  } finally {
    uploading.value = false
  }
}

onMounted(() => {
  fetchUsers()
  fetchDepartments()
})
</script>

<style lang="scss" scoped>
.face-upload-content {
  text-align: center;
  
  .upload-info {
    margin-bottom: 16px;
    color: #606266;
    font-size: 14px;
  }
  
  .preview-image {
    margin-top: 16px;
    
    img {
      max-width: 200px;
      border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }
  }
}
</style>
