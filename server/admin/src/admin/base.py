from typing import Any
import io

from sqladmin import Admin
from starlette.datastructures import FormData, UploadFile
from starlette.requests import Request


class PatchedAdmin(Admin):
    """
    AdminSQL 내부 로직 커스팀 목적으로 구현된 클래스
    """
    async def _handle_form_data(self, request: Request, obj: Any = None) -> FormData:
        """
        Handle form data and modify in case of UploadFile.
        This is needed since in edit page
        there's no way to show current file of object.
        """

        form = await request.form()
        form_data: list[tuple[str, str | UploadFile]] = []
        for key, value in form.multi_items():
            if not isinstance(value, UploadFile):
                form_data.append((key, value))
                continue

            should_clear = form.get(key + "_checkbox")
            empty_upload = len(await value.read(1)) != 1
            await value.seek(0)
            if should_clear:
                form_data.append((key, UploadFile(io.BytesIO(b""))))
            elif empty_upload and obj and getattr(obj, key):
                f = getattr(obj, key)  # In case of update, imitate UploadFile

                if not isinstance(f, UploadFile):
                    # 파일 관련 데이터가 UploadFile이 아닌 다른 데이터인 경우
                    form_data.append((key, f))
                    continue

                form_data.append((key, UploadFile(filename=f.name, file=f.open())))
            else:
                form_data.append((key, value))
        return FormData(form_data)
