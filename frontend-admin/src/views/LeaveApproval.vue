<template>
  <div class="leave-approval-page">
    <div class="page-header">
      <h2 class="page-title">请假审批</h2>
      <el-radio-group v-model="activeTab" @change="handleTabChange">
        <el-radio-button label="pending">待审批</el-radio-button>
        <el-radio-button label="approved">已通过</el-radio-button>
        <el-radio-button label="rejected">已驳回</el-radio-button>
        <el-radio-button label="">全部</el-radio-button>
      </el-radio-group>
    </div>
    
    <div class="card">
      <div class="search-bar">
        <el-select v-model="searchUser" placeholder="选择员工" clearable style="width: 160px" @change="fetchLeaves">
          <el-option v-for="u in userOptions" :key="u.id" :label="u.real_name" :value="u.id" />
        </el-select>
        <el-button @click="resetSearch">重置</el-button>
      </div>
      
      <el-table :data="leaves" stripe v-loading="loading" border style="width: 100%">
        <el-table-column prop="employee_no" label="工号" min-width="80" align="center" />
        <el-table-column prop="user_name" label="姓名" min-width="80" align="center" />
        <el-table-column prop="department_name" label="部门" min-width="100" align="center">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
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
        <el-table-column prop="created_at" label="申请时间" min-width="160" align="center" />
        <el-table-column label="操作" min-width="180" align="center" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button size="small" type="success" plain @click="openApproveDialog(row, true)">通过</el-button>
              <el-button size="small" type="danger" plain @click="openApproveDialog(row, false)">驳回</el-button>
            </template>
            <template v-else>
              <el-button size="small" type="primary" plain @click="openDetailDialog(row)">查看</el-button>
            </template>
          </template>
        </el-table-column>
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
    
    <el-dialog v-model="approveDialogVisible" :title="isApprove ? '通过请假' : '驳回请假'" width="500px" destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="申请人">{{ currentLeave?.user_name }}</el-descriptions-item>
        <el-descriptions-item label="请假类型">{{ currentLeave?.leave_type_text }}</el-descriptions-item>
        <el-descriptions-item label="请假日期">{{ currentLeave?.start_date }} 至 {{ currentLeave?.end_date }}</el-descriptions-item>
        <el-descriptions-item label="请假原因">{{ currentLeave?.reason || '-' }}</el-descriptions-item>
      </el-descriptions>
      <el-form :model="form" label-width="80px" style="margin-top: 20px">
        <el-form-item :label="isApprove ? '审批意见' : '驳回理由'">
          <el-input v-model="form.comment" type="textarea" :rows="3" :placeholder="isApprove ? '可选：填写审批意见' : '请填写驳回理由'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button :type="isApprove ? 'success' : 'danger'" :loading="submitting" @click="handleApprove">
          {{ isApprove ? '确认通过' : '确认驳回' }}
        </el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailDialogVisible" title="请假详情" width="500px" destroy-on-close>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="申请人">{{ currentLeave?.user_name }}</el-descriptions-item>
        <el-descriptions-item label="工号">{{ currentLeave?.employee_no }}</el-descriptions-item>
        <el-descriptions-item label="部门">{{ currentLeave?.department_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="请假类型">{{ currentLeave?.leave_type_text }}</el-descriptions-item>
        <el-descriptions-item label="请假日期">{{ currentLeave?.start_date }} 至 {{ currentLeave?.end_date }}</el-descriptions-item>
        <el-descriptions-item label="请假原因">{{ currentLeave?.reason || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusTag(currentLeave?.status)" size="small">{{ currentLeave?.status_text }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="审批人">{{ currentLeave?.approver_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审批意见">{{ currentLeave?.approver_comment || '-' }}</el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ currentLeave?.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const loading = ref(false)
const leaves = ref([])
const userOptions = ref([])
const activeTab = ref('pending')
const searchUser = ref(null)
const pagination = reactive({ page: 1, pageSize: 10, total: 0 })

const approveDialogVisible = ref(false)
const detailDialogVisible = ref(false)
const currentLeave = ref(null)
const isApprove = ref(true)
const submitting = ref(false)
const form = reactive({ comment: '' })

const getLeaveTypeTag = (type) => {
  const map = { personal: 'primary', sick: 'danger', annual: 'success' }
  return map[type] || 'info'
}

const getStatusTag = (status) => {
  const map = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getDays = (row) => {
  if (!row) return 0
  const start = new Date(row.start_date)
  const end = new Date(row.end_date)
  const diff = (end - start) / (1000 * 60 * 60 * 24)
  return Math.round(diff) + 1
}

const fetchLeaves = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status: activeTab.value || undefined,
      user_id: searchUser.value || undefined
    }
    const res = await api.leave.getAllLeaves(params)
    leaves.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const fetchUsers = async () => {
  try {
    const res = await api.users.list({ page: 1, page_size: 1000 })
    userOptions.value = res.data.list
  } catch (e) {}
}

const handleTabChange = () => {
  pagination.page = 1
  fetchLeaves()
}

const resetSearch = () => {
  searchUser.value = null
  activeTab.value = 'pending'
  pagination.page = 1
  fetchLeaves()
}

const openApproveDialog = (row, approve) => {
  currentLeave.value = row
  isApprove.value = approve
  form.comment = ''
  approveDialogVisible.value = true
}

const openDetailDialog = (row) => {
  currentLeave.value = row
  detailDialogVisible.value = true
}

const handleApprove = async () => {
  if (!isApprove.value && !form.comment.trim()) {
    ElMessage.warning('请填写驳回理由')
    return
  }
  
  submitting.value = true
  try {
    const apiMethod = isApprove.value ? api.leave.approve : api.leave.reject
    await apiMethod(currentLeave.value.id, { comment: form.comment })
    ElMessage.success(isApprove.value ? '已通过请假申请' : '已驳回请假申请')
    approveDialogVisible.value = false
    fetchLeaves()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchLeaves()
  fetchUsers()
})
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
