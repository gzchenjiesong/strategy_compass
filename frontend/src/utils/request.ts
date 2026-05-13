import axios from 'axios'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

request.interceptors.request.use((config) => {
  let token = localStorage.getItem('token')
  // 开发环境强制使用有效 mock token，避免 localStorage 缓存过期 token
  if (import.meta.env.DEV) {
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE4MDk3NjgxMzksImlhdCI6MTc3ODIzMjEzOX0.9o5pfPqDtwtUyVWcw1PI-vLr7zu_MwWBZdjd5EzScs8'
    localStorage.setItem('token', token)
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // 避免在登录页重复跳转
      if (!window.location.pathname.includes('/login')) {
        window.location.replace('/login')
      }
    }
    return Promise.reject(error.response?.data?.error)
  }
)

export default request
