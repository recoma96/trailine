from fastapi import FastAPI
from sqladmin import Admin, ModelView

from trailine_model.base import engine
from trailine_model.models.user import User

app = FastAPI()
admin = Admin(app, engine)

class UserAdmin(ModelView, model=User):
    # 생성 및 수정 폼에서 created_at과 updated_at 필드를 제외합니다.
    form_excluded_columns = [User.created_at, User.updated_at]
    can_delete = False
    column_list = [
        User.id,
        User.email,
        User.nickname,
        User.is_active,
        User.can_access_admin,
        User.last_login_at,
        User.created_at,
        User.updated_at
    ]

admin.add_view(UserAdmin)
