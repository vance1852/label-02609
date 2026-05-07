<template>
  <div class="leaves-page">
    <div class="page-header">
      <h2 class="page-title">我的请假</h2>
      <el-button type="primary" @click="openApplyDialog">
        <el-icon><Plus /></el-icon>
        提交请假
      </el-button>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-select v-model="searchStatus" placeholder="请假状态" clearable style="width: 140px" @change="fetchLeaves">
          <el-option label="待审批" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      
      <el-table :data="leaves" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="leave_type_text" label="请假类型" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getLeaveTypeTag(row.leave_type)" size="small">{{ row.leave_type_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="start_date" label="开始日期" min-width="110" align="center" />
        <el-table-column prop="end_date" label="结束日期" min-width="110" align="center" />
        <el-table-column prop="days" label="天数" min-width="60" align="center">
          <template #default="{ row }">{{ getDays(row) }}天</template>
        </el-table-column>
        <el-table-column prop="reason" label="请假原因" min-width="180" align="center">
          <template #default="{ row }">{{ row.reason || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status_text" label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver_comment" label="审批意见" min-width="150" align="center">
          <template #default="{ row }">{{ row.approver_comment || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" min-width="160" align="center" />
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @change="fetchLeaves"
      />
    </div>
    
    <el-dialog v-model="applyDialogVisible" title="提交请假申请" width="500px" destroy-on-close>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="form.leave_type" placeholder="请选择请假类型" style="width: 100%">
            <el-option label="事假" value="personal" />
            <el-option label="病假" value="sick" />
            <el-option label="年假" value="annual" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="请假原因" prop="reason">
          <el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入请假原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="applyDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import api from '@/api'

const loading = ref(false)
const leaves = ref([])
const searchStatus = ref(null)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const applyDialogVisible = ref(false)
const formRef = ref()
const submitting = ref(false)
const form = reactive({
  leave_type: '',
  dateRange: [],
  reason: ''
})

const rules = {
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择请假日期', trigger: 'change' }]
}

const getLeaveTypeTag = (type) => {
  const map = { personal: 'primary', sick: 'danger', annual: 'success' }
  return map[type] || 'info'
}

const getStatusTag = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getDays = (row) => {
  const start = new Date(row.start_date)
  const end = new Date(row.end_date)
  const diff = (end - start) / (1000 * 60 * 60 * 24)
  return Math.round(diff) + 1
}

const disabledDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7
}

const fetchLeaves = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (searchStatus.value) {
      params.status = searchStatus.value
    }
    const res = await api.leave.getMyLeaves(params)
    leaves.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const resetSearch = () => {
  searchStatus.value = null
  pagination.page = 1
  fetchLeaves()
}

const openApplyDialog = () => {
  Object.assign(form, {
    leave_type: '',
    dateRange: [],
    reason: ''
  })
  applyDialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    await api.leave.apply({
      leave_type: form.leave_type,
      start_date: form.dateRange[0],
      end_date: form.dateRange[1],
      reason: form.reason
    })
    ElMessage.success('请假申请提交成功')
    applyDialogVisible.value = false
    fetchLeaves()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchLeaves()
})
</script>

<style lang="scss" scoped>
</style>
