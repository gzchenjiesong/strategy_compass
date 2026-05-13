#!/bin/bash
# API check script - verify backend endpoints

set -e

BACKEND_DIR="$(cd "$(dirname "$0")/../backend" && pwd)"
PYTHON="$BACKEND_DIR/venv/bin/python"

cd "$BACKEND_DIR"

export PYTHONPATH="$BACKEND_DIR"
export JWT_SECRET="test-secret"

$PYTHON -c "
import sys
from app import create_app, db
from app.models import *

app = create_app('testing')
with app.app_context():
    db.create_all()
    from app.models.data import IndexInfo
    core = [
        {'symbol': '000001', 'name': '上证指数', 'market': 'A', 'category': 'broad', 'is_core': True},
        {'symbol': '000300', 'name': '沪深300', 'market': 'A', 'category': 'broad', 'is_core': True},
    ]
    for info in core:
        if not IndexInfo.query.filter_by(symbol=info['symbol']).first():
            db.session.add(IndexInfo(**info))
    from app.models.user import InvitationCode
    if not InvitationCode.query.filter_by(code='TEST2026').first():
        db.session.add(InvitationCode(code='TEST2026', max_uses=-1, status='active'))
    db.session.commit()

client = app.test_client()

# Get token first
r = client.post('/api/v1/auth/wechat/callback', json={'code': 'test', 'invitation_code': 'TEST2026'})
assert r.status_code == 200, f'Auth failed: {r.status_code}'
token = r.get_json()['data']['token']
auth_headers = {'Authorization': 'Bearer ' + token}

tests = [
    ('GET', '/health', {}, 200),
    ('GET', '/api/v1/auth/me', auth_headers, 200),
    ('GET', '/api/v1/users/me', auth_headers, 200),
    ('GET', '/api/v1/data/indices', auth_headers, 200),
    ('GET', '/api/v3/market/overview', auth_headers, 200),
    ('GET', '/api/v3/market/indices', auth_headers, 200),
    ('GET', '/api/v2/news', auth_headers, 200),
]

passed = 0
failed = 0

for method, path, headers, expected in tests:
    r = client.get(path, headers=headers)
    status = r.status_code
    if status == expected:
        passed += 1
        print(f'✓ {method} {path} -> {status}')
    else:
        failed += 1
        print(f'✗ {method} {path} -> {status} (expected {expected})')

print(f'\nResults: {passed} passed, {failed} failed')
sys.exit(0 if failed == 0 else 1)
"
