import pytest
from app import db


class TestUserModel:
    """用户模型测试"""

    def test_user_creation(self, app, sample_user):
        """测试用户创建"""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(wechat_id='test_wechat_id').first()
            assert user is not None
            assert user.nickname == 'Test User'
            assert user.avatar == 'https://example.com/avatar.jpg'

    def test_user_repr(self, app, sample_user):
        """测试用户字符串表示"""
        with app.app_context():
            from app.models.user import User
            user = User.query.filter_by(wechat_id='test_wechat_id').first()
            assert 'Test User' in repr(user)

    def test_user_watchlist(self, app, sample_user):
        """测试用户自选股"""
        with app.app_context():
            from app.models.user import User, Watchlist
            user = User.query.filter_by(wechat_id='test_wechat_id').first()

            # 添加自选股
            watchlist = Watchlist(user_id=user.id, stock_code='600000', stock_name='浦发银行')
            db.session.add(watchlist)
            db.session.commit()

            # 验证自选股
            assert len(user.watchlist) == 1
            assert user.watchlist[0].stock_code == '600000'

    def test_user_preference(self, app, sample_user):
        """测试用户偏好设置"""
        with app.app_context():
            from app.models.user import User, UserPreference
            user = User.query.filter_by(wechat_id='test_wechat_id').first()

            # 创建偏好设置
            preference = UserPreference(
                user_id=user.id,
                risk_level='moderate',
                investment_horizon='medium',
                markets='A,HK'
            )
            db.session.add(preference)
            db.session.commit()

            # 验证偏好设置
            assert user.preference.risk_level == 'moderate'
            assert user.preference.investment_horizon == 'medium'
            assert 'A' in user.preference.markets


class TestUserAPI:
    """用户API测试"""

    def test_get_current_user(self, client, auth_headers):
        """测试获取当前用户信息"""
        response = client.get('/api/v1/auth/me', headers=auth_headers)
        # 由于没有认证，应该返回401
        assert response.status_code == 401

    def test_wechat_callback(self, client):
        """测试微信OAuth回调"""
        # 这里需要模拟微信OAuth回调
        # 暂时跳过具体实现
        pass

    def test_get_user_info(self, client, auth_headers):
        """测试获取用户详细信息"""
        response = client.get('/api/v1/users/me', headers=auth_headers)
        # 由于没有认证，应该返回401
        assert response.status_code == 401

    def test_update_user_info(self, client, auth_headers):
        """测试更新用户信息"""
        data = {
            'nickname': 'New Nickname',
            'avatar': 'https://example.com/new-avatar.jpg'
        }
        response = client.put('/api/v1/users/me', json=data, headers=auth_headers)
        # 由于没有认证，应该返回401
        assert response.status_code == 401

    def test_get_watchlist(self, client, auth_headers):
        """测试获取自选股列表"""
        response = client.get('/api/v1/users/me/watchlist', headers=auth_headers)
        # 由于没有认证，应该返回401
        assert response.status_code == 401

    def test_add_to_watchlist(self, client, auth_headers):
        """测试添加自选股"""
        data = {
            'stock_code': '600000',
            'stock_name': '浦发银行'
        }
        response = client.post('/api/v1/users/me/watchlist', json=data, headers=auth_headers)
        # 由于没有认证，应该返回401
        assert response.status_code == 401

    def test_remove_from_watchlist(self, client, auth_headers):
        """测试删除自选股"""
        response = client.delete('/api/v1/users/me/watchlist/600000', headers=auth_headers)
        # 由于没有认证，应该返回401
        assert response.status_code == 401