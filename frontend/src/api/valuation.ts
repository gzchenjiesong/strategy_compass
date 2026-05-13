import request from '@/utils/request'

export const valuationApi = {
  getIndexValuation: (symbol: string, windowYears?: number) =>
    request.get(`/v4/valuation/index/${symbol}`, { params: { window_years: windowYears } }),
  getStockValuation: (symbol: string, market?: string, windowYears?: number) =>
    request.get(`/v4/valuation/stock/${symbol}`, { params: { market, window_years: windowYears } }),
  getMarketValuation: () => request.get('/v4/valuation/market'),
}
