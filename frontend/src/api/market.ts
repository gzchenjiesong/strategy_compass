import request from '@/utils/request'

export const marketApi = {
  getOverview: () => request.get('/v3/market/overview'),
  getIndices: () => request.get('/v3/market/indices'),
  getIndexQuote: (symbol: string, market?: string) =>
    request.get(`/v1/data/quotes/index/${symbol}`, { params: { market } }),
  getIndexKlines: (symbol: string, market?: string, limit?: number) =>
    request.get(`/v1/data/klines/index/${symbol}`, { params: { market, limit } }),
}
