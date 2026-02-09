<template>
  <div class="dashboard">
    <div class="page-header">
      <h2 class="page-title">数据概览</h2>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始"
          end-placeholder="结束"
          value-format="YYYY-MM-DD"
          @change="fetchStatistics"
        />
      </div>
    </div>
    
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon><Calendar /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.total_days }}</div>
          <div class="stat-label">打卡总次数</div>
        </div>
      </div>
      <div class="stat-card success">
        <div class="stat-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.normal_days }}</div>
          <div class="stat-label">正常打卡</div>
        </div>
      </div>
      <div class="stat-card warning">
        <div class="stat-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.late_days }}</div>
          <div class="stat-label">迟到次数</div>
        </div>
      </div>
      <div class="stat-card danger">
        <div class="stat-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.early_days }}</div>
          <div class="stat-label">早退次数</div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3>最近考勤记录</h3>
      </div>
      <el-table :data="recentRecords" stripe border style="width: 100%">
        <el-table-column prop="user_name" label="姓名" min-width="80" align="center" />
        <el-table-column prop="employee_no" label="工号" min-width="80" align="center" />
        <el-table-column prop="department_name" label="部门" min-width="100" align="center">
          <template #default="{ row }">{{ row.department_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="attendance_date" label="日期" min-width="100" align="center" />
        <el-table-column prop="record_type_text" label="类型" min-width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.record_type === 'check_in' ? 'success' : 'warning'" size="small">
              {{ row.record_type_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="record_time" label="打卡时间" min-width="100" align="center">
          <template #default="{ row }">{{ row.record_time || '-' }}</template>
        </el-table-column>
        <el-table-column prop="status_text" label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">{{ row.status_text }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Calendar, CircleCheck, Clock, Warning } from '@element-plus/icons-vue'
import api from '@/api'

const dateRange = ref([])
const stats = reactive({
  total_days: 0,
  normal_days: 0,
  late_days: 0,
  early_days: 0,
  absent_days: 0
})
const recentRecords = ref([])

const getStatusType = (status) => {
  const map = { normal: 'success', late: 'warning', early: 'danger' }
  return map[status] || 'info'
}

const fetchStatistics = async () => {
  const params = {}
  if (dateRange.value?.length === 2) {
    params.start_date = dateRange.value[0]
    params.end_date = dateRange.value[1]
  }
  
  try {
    const res = await api.attendance.statistics(params)
    Object.assign(stats, res.data)
  } catch (e) {}
}

const fetchRecentRecords = async () => {
  try {
    const res = await api.attendance.list({ page: 1, page_size: 10 })
    recentRecords.value = res.data.list
  } catch (e) {}
}

onMounted(() => {
  fetchStatistics()
  fetchRecentRecords()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .header-actions {
    display: flex;
    gap: 12px;
  }
  
  .stat-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 24px;
    
    @media (max-width: 1200px) {
      grid-template-columns: repeat(2, 1fr);
    }
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
    
    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      display: flex;
      align-items: center;
      gap: 20px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      border-left: 4px solid #409eff;
      transition: transform 0.3s, box-shadow 0.3s;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
      }
      
      .stat-icon {
        width: 56px;
        height: 56px;
        border-radius: 12px;
        background: rgba(64, 158, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        
        .el-icon {
          font-size: 28px;
          color: #409eff;
        }
      }
      
      .stat-info {
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: #303133;
          line-height: 1.2;
        }
        
        .stat-label {
          font-size: 14px;
          color: #909399;
          margin-top: 4px;
        }
      }
      
      &.success {
        border-left-color: #67c23a;
        .stat-icon {
          background: rgba(103, 194, 58, 0.1);
          .el-icon { color: #67c23a; }
        }
      }
      
      &.warning {
        border-left-color: #e6a23c;
        .stat-icon {
          background: rgba(230, 162, 60, 0.1);
          .el-icon { color: #e6a23c; }
        }
      }
      
      &.danger {
        border-left-color: #f56c6c;
        .stat-icon {
          background: rgba(245, 108, 108, 0.1);
          .el-icon { color: #f56c6c; }
        }
      }
    }
  }
  
  .card-header {
    margin-bottom: 16px;
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }
}
</style>
