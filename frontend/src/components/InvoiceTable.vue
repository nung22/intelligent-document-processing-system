<script setup lang="ts">
import type { Invoice } from '../types';

defineProps<{
  invoices: Invoice[];
  loading: boolean;
}>();
</script>

<template>
  <div class="table-container">
    <div v-if="invoices.length > 0" class="table-wrapper">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
      </div>
      
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Vendor</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.invoiceId">
            <td class="mono">{{ inv.invoiceId.substring(0, 8) }}...</td>
            <td style="text-align: left;">{{ inv.vendor }}</td>
            <td class="amount">${{ inv.total.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-else-if="loading" class="state-container">
      <div class="spinner"></div>
      <p>Loading invoices...</p>
    </div>

    <div v-else class="state-container">
      No invoices found. Upload a document to begin.
    </div>
  </div>
</template>

<style scoped>
.table-container {
  margin-top: 2rem;
  position: relative;
}

.table-wrapper {
  position: relative;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

/* Loading Animation */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
  backdrop-filter: blur(1px);
}

.spinner {
  border: 3px solid #f3f3f3;
  border-top: 3px solid #2563eb;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Table Styles */
table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

th {
  text-align: left;
  padding: 12px 16px;
  background-color: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 0.875rem;
  border-bottom: 1px solid #e2e8f0;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  color: #334155;
}

.mono {
  font-family: monospace;
  color: #64748b;
}

.amount {
  font-weight: 700;
  color: #0f172a;
  text-align: left;
}

/* State Styles */
.state-container {
  text-align: center;
  padding: 3rem;
  color: #94a3b8;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px dashed #cbd5e1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
</style>