# project

To start app
<code>
docker-compose build
docker-compose up
</code>

### Админ-панель
у проекта есть админ-панель, которая находится по адресу 158.160.119.73:8081/admin.
В админке можно изменить статус встречи.
у встречи есть состояния:

**CREATED** - встреча была создана
**ARRIVED** - представитель прибыл на место встречи
**IN_PROGRESS** - представить в пути
**DONE** - встреча проведена
**CANCELED** - встреча отменена
