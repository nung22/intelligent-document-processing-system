export interface Invoice {
  invoiceId: string;
  vendor: string;
  total: number;
}

export interface UploadResponse {
  uploadUrl: string;
  key: string;
}