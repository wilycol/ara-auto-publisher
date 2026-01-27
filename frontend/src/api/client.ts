import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://192.168.1.4:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
