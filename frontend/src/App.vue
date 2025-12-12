<script setup lang="ts">
import { onMounted } from 'vue';
import { useInvoices } from './composables/useInvoices';
import InvoiceTable from './components/InvoiceTable.vue';

const { 
  invoices, 
  isLoading, 
  isUploading, 
  error, 
  fetchInvoices, 
  uploadInvoice 
} = useInvoices();

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files?.length) return;

  const file = target.files[0]
  await uploadInvoice(file!);
  
  // Reset input
  target.value = '';
};

onMounted(() => {
  fetchInvoices();
  // Poll every 10 seconds for updates
  setInterval(fetchInvoices, 10000);
});
</script>

<template>
  <div class="app-layout">
    <header>
      <h1>Invoice Processor</h1>
      <p>Intelligent Document Processing Demo</p>
    </header>

    <main>
      <div v-if="error" class="error-banner">
        {{ error }}
      </div>

      <div class="controls">
        <label class="upload-btn" :class="{ disabled: isUploading }">
          <input 
            type="file" 
            @change="handleFileUpload" 
            accept="image/jpeg,image/png,application/pdf"
            :disabled="isUploading"
          />
          <span v-if="isUploading">Uploading...</span>
          <span v-else>Upload Invoice</span>
        </label>
        
        <button @click="fetchInvoices" class="refresh-btn" :disabled="isLoading">
          Refresh List
        </button>
      </div>

      <InvoiceTable :invoices="invoices" :loading="isLoading" />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: system-ui, -apple-system, sans-serif;
}

header {
  margin-bottom: 2rem;
}

h1 {
  font-size: 1.8rem;
  color: #ffffff;
  margin-bottom: 0.5rem;
}

p {
  color: #708097;
  font-style: italic;
}

.error-banner {
  background-color: #fef2f2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  border: 1px solid #fecaca;
}

.controls {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-bottom: 1.5rem;
}

.upload-btn {
  background-color: #2563eb;
  color: white;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
  display: inline-flex;
  align-items: center;
}

.upload-btn:hover:not(.disabled) {
  background-color: #1d4ed8;
}

.upload-btn.disabled {
  background-color: #94a3b8;
  cursor: not-allowed;
}

.upload-btn input {
  display: none;
}

.refresh-btn {
  background: white;
  border: 1px solid #cbd5e1;
  color: #475569;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.refresh-btn:hover {
  background-color: #f8fafc;
}
</style>