<template>
  <div class="departments-page">
    <div class="page-header">
      <h2 class="page-title">部门管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon>
        添加部门
      </el-button>
    </div>
    
    <div class="card">
      <el-table :data="departments" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="id" label="ID" min-width="60" align="center" />
        <el-table-column prop="name" label="部门名称" min-width="120" align="center" />
        <el-table-column prop="description" label="描述" min-width="150" align="center">
          <template #default="{ row }">{{ row.description || '-' }}</template>
        </el-table-column>
        <el-table-column prop="user_count" label="员工数" min-width="80" align="center" />
        <el-table-column prop="created_at" label="创建时间" min-width="120" align="center">
          <template #default="{ row }">
            {{ row.created_at?.split('T')[0] }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="140" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button size="small" type="primary" plain @click="openDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" plain @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 16px; justify-content: flex-end;"
        @change="fetchDepartments"
      />
    </div>
    
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑部门' : '添加部门'" width="500px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入部门描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const departments = ref([])
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({ id: null, name: '', description: '' })

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const fetchDepartments = async () => {
  loading.value = true
  try {
    const res = await api.departments.list({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    departments.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const openDialog = (row = null) => {
  isEdit.value = !!row
  if (row) {
    Object.assign(form, row)
  } else {
    Object.assign(form, { id: null, name: '', description: '' })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await api.departments.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await api.departments.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchDepartments()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm(`确定删除部门 ${row.name} 吗？`, '提示', { type: 'warning' })
  try {
    await api.departments.delete(row.id)
    ElMessage.success('删除成功')
    fetchDepartments()
  } catch (e) {}
}

onMounted(() => {
  fetchDepartments()
})
</script>
