import request from '@/utils/request'

export const authApi = {
  wechatCallback: (code: string, invitationCode?: string) =>
    request.post('/v1/auth/wechat/callback', { code, invitation_code: invitationCode }),
  wechatBind: (openid: string, nickname: string, avatarUrl: string, invitationCode: string) =>
    request.post('/v1/auth/wechat/bind', { openid, nickname, avatar_url: avatarUrl, invitation_code: invitationCode }),
  getMe: () => request.get('/v1/auth/me'),
}
