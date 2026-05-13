import request from '@/utils/request'

export const newsApi = {
  getNews: (params?: { limit?: number; before_id?: number; filter?: string }) =>
    request.get('/v2/news', { params }),

  getImportantNews: (limit?: number) =>
    request.get('/v2/news/important', { params: { limit } }),

  getStats: () =>
    request.get('/v2/news/stats'),

  getMacroEvents: (params?: { limit?: number; country?: string }) =>
    request.get('/v2/news/macro', { params }),
}
