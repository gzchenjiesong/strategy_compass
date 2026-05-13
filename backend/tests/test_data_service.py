import pytest
from app import db


class TestIndexModel:
    """指数模型测试"""

    def test_index_creation(self, app, sample_index):
        """测试指数创建"""
        with app.app_context():
            from app.models.index import Index
            index = Index.query.filter_by(code='000001').first()
            assert index is not None
            assert index.name == '上证指数'
            assert index.market == 'A'
            assert index.category == 'market'

    def test_index_repr(self, app, sample_index):
        """测试指数字符串表示"""
        with app.app_context():
            from app.models.index import Index
            index = Index.query.filter_by(code='000001').first()
            assert '上证指数' in repr(index)

    def test_index_kline(self, app, sample_index):
        """测试指数K线数据"""
        with app.app_context():
            from app.models.index import Index, IndexDailyKline
            index = Index.query.filter_by(code='000001').first()

            # 添加K线数据
            kline = IndexDailyKline(
                index_code=index.code,
                date='2024-01-01',
                open=3000.0,
                high=3100.0,
                low=2950.0,
                close=3050.0,
                volume=1000000
            )
            db.session.add(kline)
            db.session.commit()

            # 验证K线数据
            assert len(index.kline_data) == 1
            assert index.kline_data[0].close == 3050.0

    def test_index_valuation(self, app, sample_index):
        """测试指数估值数据"""
        with app.app_context():
            from app.models.index import Index, IndexValuation
            index = Index.query.filter_by(code='000001').first()

            # 添加估值数据
            valuation = IndexValuation(
                index_code=index.code,
                date='2024-01-01',
                pe=12.5,
                pb=1.2,
                pe_percentile=0.35,
                pb_percentile=0.42
            )
            db.session.add(valuation)
            db.session.commit()

            # 验证估值数据
            assert len(index.valuation_data) == 1
            assert index.valuation_data[0].pe == 12.5


class TestDataAPI:
    """数据API测试"""

    def test_get_indices(self, client):
        """测试获取指数列表"""
        response = client.get('/api/v1/data/indices')
        assert response.status_code == 200
        data = response.get_json()
        assert 'indices' in data

    def test_get_index_kline(self, client, sample_index):
        """测试获取指数K线数据"""
        response = client.get('/api/v1/data/indices/000001/kline')
        # 由于没有数据，应该返回空列表或错误
        assert response.status_code in [200, 404]

    def test_get_index_valuation(self, client, sample_index):
        """测试获取指数估值数据"""
        response = client.get('/api/v1/data/indices/000001/valuation')
        # 由于没有数据，应该返回空列表或错误
        assert response.status_code in [200, 404]

    def test_get_stock_kline(self, client):
        """测试获取股票K线数据"""
        response = client.get('/api/v1/data/stocks/600000/kline')
        # 由于没有数据，应该返回空列表或错误
        assert response.status_code in [200, 404]

    def test_get_board_kline(self, client):
        """测试获取板块K线数据"""
        response = client.get('/api/v1/data/boards/BK0001/kline')
        # 由于没有数据，应该返回空列表或错误
        assert response.status_code in [200, 404]

    def test_get_realtime_quote(self, client):
        """测试获取实时行情数据"""
        response = client.get('/api/v1/data/realtime/000001')
        # 由于没有数据，应该返回空或错误
        assert response.status_code in [200, 404]


class TestDataSync:
    """数据同步测试"""

    def test_data_sync_service(self, app):
        """测试数据同步服务"""
        with app.app_context():
            from app.services.data_sync import DataSyncService
            sync_service = DataSyncService()
            # 这里可以测试数据同步的基本功能
            # 暂时跳过具体实现
            assert sync_service is not None

    def test_cache_service(self, app):
        """测试缓存服务"""
        with app.app_context():
            from app.services.cache import CacheService
            cache_service = CacheService()
            # 这里可以测试缓存服务的基本功能
            # 暂时跳过具体实现
            assert cache_service is not None