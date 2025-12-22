// src/api.js
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для добавления токена
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor для обработки ошибок 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API для аутентификации
export const authAPI = {
  register: async (username, password, name) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('name', name);
    
    const response = await axios.post(`${API_URL}/register`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post(`${API_URL}/login`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  },

  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

// API для расписания
export const scheduleAPI = {
  getSchedule: async (dateStr) => {
    const response = await api.get(`/schedule/${dateStr}`);
    return response.data;
  },

  createOrGetSchedule: async (dateStr) => {
    const response = await api.post(`/schedule/${dateStr}`);
    return response.data;
  },

  updateLesson: async (lessonId, data) => {
    const formData = new FormData();
    if (data.subject) formData.append('subject', data.subject);
    if (data.teacher) formData.append('teacher', data.teacher);
    if (data.room) formData.append('room', data.room);
    
    const response = await api.put(`/lessons/${lessonId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  deleteLesson: async (lessonId) => {
    const response = await api.delete(`/lessons/${lessonId}`);
    return response.data;
  },

  getDates: async () => {
    const response = await api.get('/dates');
    return response.data;
  },
};

// API для файлов
export const filesAPI = {
  uploadFile: async (lessonId, files) => {
    const formData = new FormData();
    formData.append('lesson_id', lessonId.toString());
    
    // Для одного файла
    if (!Array.isArray(files)) {
      files = [files];
    }
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadToLesson: async (lessonId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`/lessons/${lessonId}/files`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getFileInfo: async (fileId) => {
    const response = await api.get(`/files/${fileId}`);
    return response.data;
  },

  downloadFile: async (fileId) => {
    const response = await api.get(`/files/download/${fileId}`, {
      responseType: 'blob',
    });
    
    // Создаем ссылку для скачивания
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `file_${fileId}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  deleteFile: async (fileId) => {
    const response = await api.delete(`/files/${fileId}`);
    return response.data;
  },
};

export default api;