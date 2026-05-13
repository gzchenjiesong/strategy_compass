import pytest
import tempfile
import os
from app import create_app, db


@pytest.fixture
def app():
    """创建测试应用"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret-key',
    })

    # 创建数据库表
    with app.app_context():
        db.create_all()

    yield app

    # 清理
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """创建测试运行器"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """创建认证头"""
    # 这里可以添加用户创建和认证逻辑
    # 暂时返回空字典
    return {}


@pytest.fixture
def sample_user(app):
    """创建示例用户"""
    with app.app_context():
        from app.models.user import User
        user = User(
            wechat_id='test_wechat_id',
            nickname='Test User',
            avatar='https://example.com/avatar.jpg'
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_index(app):
    """创建示例指数"""
    with app.app_context():
        from app.models.index import Index
        index = Index(
            code='000001',
            name='上证指数',
            market='A',
            category='market'
        )
        db.session.add(index)
        db.session.commit()
        return index