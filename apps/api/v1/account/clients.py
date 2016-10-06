from chinaapi.sina.weibo.open import Client as SinaClient
from chinaapi.renren.open import Client as RenrenClient

sina_weibo_client = SinaClient()

sina_weibo_client.set_access_token('access_token')  # 填上取得的token（可通过OAuth2取得）

# 获取用户信息，对应的接口是：users/show
r = sina_weibo_client.users.show(uid=123456)
print(r.name)  # 显示用户名

# 发布带图片的微博，对应的接口是：statuses/upload
with open('pic.jpg', 'rb') as pic:
    r = sina_weibo_client.statuses.upload(status=u'发布的内容', pic=pic)
    print(r.id)  # 显示发布成功的微博的编号（即mid）：1234567890123456

renren_client = RenrenClient()
renren_client.set_access_token('access_token')  # 填上取得的access_token

# 获取用户信息，对应的接口是：/v2/user/get
r = renren_client.user.get(userId=334258249)
print(r.name)  # 显示用户名

# 上传照片至用户相册，对应的接口是：/v2/photo/upload
with open('pic.jpg', 'rb') as pic:
    r = renren_client.photo.upload(file=pic)
print(r.id)  # 显示照片的ID


