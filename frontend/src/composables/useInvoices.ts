import { ref } from 'vue';
import axios from 'axios';
import type { Invoice, UploadResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export function useInvoices() {
  const invoices = ref<Invoice[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const isUploading = ref(false);

  const fetchInvoices = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await axios.get<Invoice[]>(API_BASE_URL);
      // Sort descending by ID
      invoices.value = response.data.sort((a, b) => 
        b.invoiceId.localeCompare(a.invoiceId)
      );
    } catch (err) {
      console.error(err);
      error.value = 'Failed to load invoices.';
    } finally {
      isLoading.value = false;
    }
  };

  const uploadInvoice = async (file: File) => {
    isUploading.value = true;
    error.value = null;
    try {
      // Get Pre-signed URL
      const { data } = await axios.get<UploadResponse>(`${API_BASE_URL}upload-url`, {
        params: { 
          filename: file.name,
          contentType: file.type
        }
      });

      // Upload binary to S3
      await axios.put(data.uploadUrl, file, {
        headers: { 'Content-Type': file.type }
      });

      setTimeout(fetchInvoices, 3000);
      
    } catch (err) {
      console.error(err);
      error.value = 'Upload failed. Please try again.';
      throw err;
    } finally {
      isUploading.value = false;
    }
  };

  return {
    invoices,
    isLoading,
    isUploading,
    error,
    fetchInvoices,
    uploadInvoice
  };
}