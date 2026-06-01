import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
});

// Request Interceptor to append Authorization Token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Response Interceptor to catch 401 Unauthorized
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('email');
      // Redirect to login if not already there
      if (!window.location.pathname.endsWith('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (form: FormData) => {
    const response = await axios.post(`${API_BASE}/auth/login`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  register: async (data: any) => {
    const response = await api.post('/auth/register', data);
    return response.data;
  },
  requestReset: async (email: string) => {
    const response = await api.post('/auth/reset-password', { email });
    return response.data;
  },
  confirmReset: async (data: any) => {
    const response = await api.post('/auth/reset-password/confirm', data);
    return response.data;
  }
};

export const dashboardService = {
  getMetrics: async () => {
    const response = await api.get('/dashboard');
    return response.data;
  }
};

export const projectService = {
  list: async (search?: string) => {
    const response = await api.get('/projects', { params: { q: search } });
    return response.data;
  },
  create: async (data: { name: string; description?: string }) => {
    const response = await api.post('/projects', data);
    return response.data;
  }
};

export const assetService = {
  list: async (projectId?: number, search?: string) => {
    const response = await api.get('/assets', { params: { project_id: projectId, q: search } });
    return response.data;
  },
  create: async (data: { project_id: number; type: string; target_url_or_path: string; credentials?: string; schedule_cron?: string }) => {
    const response = await api.post('/assets', data);
    return response.data;
  }
};

export const scanService = {
  start: async (assetId: number) => {
    const response = await api.post('/scans/start', { asset_id: assetId });
    return response.data;
  },
  startBulk: async (assetIds: number[]) => {
    const response = await api.post('/scans/assets', assetIds);
    return response.data;
  }
};

export const findingService = {
  list: async (params: { project_id?: number; severity?: string; status?: string; q?: string; limit?: number; offset?: number }) => {
    const response = await api.get('/findings', { params });
    return response.data;
  },
  update: async (id: number, data: { status: string; remediation_notes?: string; owner_id?: number }) => {
    const response = await api.patch(`/findings/${id}`, data);
    return response.data;
  },
  exportAudit: async (format: 'json' | 'csv') => {
    const response = await api.get(`/findings/export`, {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }
};

export const reportService = {
  list: async (projectId?: number) => {
    const response = await api.get('/reports', { params: { project_id: projectId } });
    return response.data;
  },
  generate: async (projectId: number, format: 'PDF' | 'HTML' | 'MD') => {
    const response = await api.post('/reports/generate', { project_id: projectId, type: format });
    return response.data;
  },
  download: async (id: number) => {
    const response = await api.get(`/reports/download/${id}`, { responseType: 'blob' });
    return response.data;
  }
};
