from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla.view import ModelView

from app.database.models import MeetStatusEnum
from app.database.requests import *
from app.api.tools.sms import send_sms

session = db_session()


class MainAdminView(AdminIndexView):
    ...


class UserAdmin(ModelView):
    form_columns = ('first_name', 'last_name', 'phone', 'password')
    column_list = ('id', 'first_name', 'last_name', 'phone', 'jwt_id')


class EmployeeAdmin(ModelView):
    form_columns = ('first_name', 'last_name', 'phone', 'work_location', 'skills')
    column_list = ('id', 'first_name', 'last_name', 'phone', 'work_location', 'rate', 'skills')


class ProductAdmin(ModelView):
    form_columns = ('name', 'description', 'documents')
    column_list = ('id', 'name', 'description', 'documents')


class MeetAdmin(ModelView):
    form_columns = ('user', 'employee', 'product', 'date', 'status', 'address', 'rate')
    column_list = ('id', 'user.full_name', 'employee.full_name', 'product.name', 'date', 'status', 'address', 'rate')

    def on_model_change(self, form, model, is_created):
        user = get_user_by_id(form.data['user'].id)

        if is_created:
            send_sms(phone=user.phone, message='Вы назначили встречу')

            if form.data['status'] == MeetStatusEnum.DONE.value:
                raise Exception('You should create meet before it is DONE')

        meet_id = model.id
        meet = get_meet_by_id(meet_id=meet_id)
        emp = get_employee(meet.employee_id)
        change_meet_status(meet_id=meet_id, status=form.data['status'])

        if form.data['status'] == MeetStatusEnum.DONE.value:
            documents = get_product_documents(meet.product_id)
            set_user_documents(meet.user_id, documents)

            send_sms(phone=user.phone, message='Встреча завершена.')

        if form.data['status'] == MeetStatusEnum.ARRIVED.value:
            send_sms(phone=user.phone, message=f'Представитель {emp.full_name} уже на месте! {emp.phone}')

        if form.data['status'] == MeetStatusEnum.IN_PROGRESS.value:
            send_sms(phone=user.phone, message='Встреча через 1 час')

        if form.data['status'] == MeetStatusEnum.CANCELED.value:
            send_sms(phone=user.phone, message='Встреча отменена')

        self._refresh_cache()
        return super().on_model_change(form, model, is_created)

    def _handle_view(self, name, **kwargs):
        self._refresh_cache()
        return super()._handle_view(name, **kwargs)


class DocumentAdmin(ModelView):
    form_columns = ('name', 'life_time', 'ref_url')
    column_list = ('id', 'name', 'life_time', 'ref_url')


class UserDocumentAdmin(ModelView):
    form_columns = ('user_id', 'document_id', 'expire')
    column_list = ('user_id', 'document_id', 'expire')


admin = Admin(index_view=MainAdminView())
admin.add_view(UserAdmin(User, session))
admin.add_view(EmployeeAdmin(Employee, session))
admin.add_view(ProductAdmin(Product, session))
admin.add_view(DocumentAdmin(Document, session))
admin.add_view(MeetAdmin(Meet, session))
admin.add_view(UserDocumentAdmin(UserDocument, session))
