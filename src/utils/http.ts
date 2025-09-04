import axios from 'axios';

/** Shared HTTP client: timeouts, creds, error normalization */
export const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true,
});

// Normalize error messages so tests and UX are consistent
http.interceptors.response.use(
  (r) => r,
  (e) => Promise.reject(new Error(e?.response?.data?.message || 'Request failed'))
);
