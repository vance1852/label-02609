<template>
  <div class="my-leave-page">
    <div class="page-header">
      <h2 class="page-title">我的请假</h2>
      <el-button type="primary" @click="showDialog = true">
        <el-icon><Plus /></el-icon>提交请假
      </el-button>
    </div>

    <div class="card">
      <div class="search-bar">
        <el-select v-model="filterStatus" placeholder="审批状态" clearable style="width: 130px">
          <el-option label="待审批" value="pending" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
        <el-button type="primary" @click="fetchLeaves">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </div>

      <el-table :data="leaves" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="leave_type_text" label="请假类型" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="leaveTypeTag(row.leave_type)" size="small">{{ row.leave_type_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="起止日期" min-width="180" align="center">
          <template #default="{ row }">{{ row.start_date }} 至 {{ row.end_date }}</template>
        </el-table-column>
        <el-table-column prop="reason" label="请假原因" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status_text" label="审批状态" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="approver_name" label="审批人" min-width="80" align="center">
          <template #default="{ row }">{{ row.approver_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="approval_comment" label="审批意见" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.approval_comment || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" min-width="160" align="center" />
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

    <el-dialog v-model="showDialog" title="提交请假申请" width="520px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="请假类型" prop="leave_type">
          <el-select v-model="form.leave_type" placeholder="请选择请假类型" style="width: 100%">
            <el-option label="事假" value="personal" />
            <el-option label="病假" value="sick" />
            <el-option label="年假" value="annual" />
          </el-select>
        </el-form-item>
        <el-form-item label="起止日期" prop="dateRange">
          <el-date-picker
            v-model="form.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="请假原因" prop="reason">
          <el-input v-model="form.reason" type="textarea" :rows="3" placeholder="请输入请假原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const submitting = ref(false)
const showDialog = ref(false)
const leaves = ref([])
const filterStatus = ref('')
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const formRef = ref(null)
const form = reactive({
  leave_type: '',
  dateRange: [],
  reason: ''
})

const rules = {
  leave_type: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
  dateRange: [{ required: true, message: '请选择起止日期', trigger: 'change' }],
  reason: [{ required: true, message: '请输入请假原因', trigger: 'blur' }]
}

const leaveTypeTag = (type) => {
  const map = { personal: 'warning', sick: 'danger', annual: 'success' }
  return map[type] || 'info'
}

const statusTag = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const fetchLeaves = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filterStatus.value) {
      params.status = filterStatus.value
    }
    const res = await api.leave.my(params)
    leaves.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterStatus.value = ''
  pagination.page = 1
  fetchLeaves()
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    await api.leave.create({
      leave_type: form.leave_type,
      start_date: form.dateRange[0],
      end_date: form.dateRange[1],
      reason: form.reason
    })
    ElMessage.success('请假申请提交成功')
    showDialog.value = false
    form.leave_type = ''
    form.dateRange = []
    form.reason = ''
    fetchLeaves()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchLeaves()
})
</script>
