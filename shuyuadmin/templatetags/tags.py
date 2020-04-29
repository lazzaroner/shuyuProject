from django.template import Library
from django.utils.safestring import mark_safe
from shuyuadmin.admin_sites import site
from shuyuadmin.models import Menu


register = Library()


@register.simple_tag
def get_table_name(admin_class):
    """
    返回table名
    :param admin_class:
    :return:
    """
    return admin_class.model._meta.verbose_name_plural


@register.simple_tag
def get_table_name2(app_name, table_name):
    """
    返回table名
    :param app_name:
    :param table_name:
    :return:
    """
    return site.enabled_admins[app_name][table_name].model._meta.verbose_name_plural


@register.simple_tag
def get_query_set(admin_class):
    """
    返回admin类对应的model的所有数据
    :param admin_class:
    :return:
    """
    return admin_class.model.objects.all()


@register.simple_tag
def get_row_data(obj, admin_class):
    """
    根据admin配置的显示字段组成要显示的内容
    :param obj:
    :param admin_class:
    :return:
    """
    ret_data = ""
    for column in admin_class.list_display:
        field_obj = obj._meta.get_field(column)
        # 根据字段的choices是否有内容，将值进行转义
        if field_obj.choices:
            column_data = getattr(obj, 'get_%s_display' % column)()
        else:
            column_data = getattr(obj, column)
        if isinstance(column_data, bool):
            if column_data:
                column_data = """<span class="label label-success">{data}</span>""".format(data=column_data)
            else:
                column_data = """<span class="label label-dark">{data}</span>""".format(data=column_data)
        # 判断图标
        if column == 'icon':
            column_data = """<i class="{data}"></i>""".format(data=getattr(obj, column))

        ret_data += "<td>%s</td>" % column_data
    return mark_safe(ret_data)


@register.simple_tag
def get_row_id(obj):
    """
    返回记录的id
    :param obj:
    :return:
    """
    return mark_safe(getattr(obj, 'id'))


@register.simple_tag
def get_filter_data(admin_class):
    """
    根据admin类配置的过滤字段返回下拉框内容（废弃）
    :param admin_class:
    :return:
    """
    base_select_date = """<div class="col-xs-2">
                    <select class="form-control" name="{filter_name}">
                    <option value="">---------</option>
                        {filter_option}
                    </select>
                    </div>
               """
    base_input_date = """<div class="col-xs-2">
                    <input class="form-control" name="{filter_name}" placeholder="请输入{placeholder}" value="{value}">
                    </input>
                    </div>
               """
    ret_data = ""
    # 通过反射将配置的过滤条件组成字符串
    # 对查询条件进行比对，如果有查询条件，记录上次查询的内容
    for column in admin_class.list_filter:
        field_obj = admin_class.model._meta.get_field(column)
        # 设置大小写不敏感的模糊查询
        filter_name = "%s__icontains" % column
        placeholder = column
        filter_option = ""
        if field_obj.choices:
            filter_name = column
            for c in field_obj.choices:
                if admin_class.filter_conditions:
                    if admin_class.filter_conditions.get(filter_name):
                        if c[0] == int(admin_class.filter_conditions.get(filter_name)):
                            filter_option += """<option value="%s" selected>%s</option>""" % (c[0], c[1])
                        else:
                            filter_option += """<option value="%s">%s</option>""" % (c[0], c[1])
                else:
                    filter_option += """<option value="%s">%s</option>""" % (c[0], c[1])
            ret_data += base_select_date.format(base_select_date, filter_name=filter_name, filter_option=filter_option)
        else:
            if admin_class.filter_conditions.get(filter_name):
                ret_data += base_input_date.format(base_input_date, filter_name=filter_name, placeholder=placeholder,
                                                   value=admin_class.filter_conditions.get(filter_name))
            else:
                ret_data += base_input_date.format(base_input_date, filter_name=filter_name, placeholder=placeholder,
                                                   value="")
    return mark_safe(ret_data)


@register.simple_tag
def get_list_filter_title(admin_class, field):
    """
    返回对应字段的中文名称，用于过滤条件的字段名显示
    :param admin_class:
    :param field:
    :return:
    """
    field_obj = admin_class.model._meta.get_field(field)
    return field_obj.verbose_name


@register.simple_tag
def get_list_filter_options(admin_class, field):
    """
    返回列表字段的内容项，用于过滤查询
    :param admin_class:
    :param field:
    :return:
    """
    field_obj = admin_class.model._meta.get_field(field)
    t = r"""<a href="?{key}={value}{urls}" class="btn btn-sm {style}" style="margin-right: 5px">{option}</a>"""
    return_data = ""

    for option in field_obj.choices:
        style = 'btn-default'
        # 如果存在list查询条件，则颜色加深
        url = ""
        for item in admin_class.filter_conditions:
            url += "&&%s=%s" % item

        # 支持一个字段有多个筛选项
        k_v = ('{k}_{v}'.format(k=field, v=option[0]), str(option[0]))
        if k_v in admin_class.filter_conditions:
            style = 'btn-info'
        # 为了使一个字段的多个值都可以进行过滤，将key值进行拼接，类似于choice1_1=1， 即 k_v=v的形式
        return_data += t.format(key='{k}_{v}'.format(k=field, v=option[0]), urls=url,
                                    value=option[0], style=style, option=option[1])
    return mark_safe(return_data)


@register.simple_tag
def get_filter_conditions_url(admin_class):
    """
    将查询条件组成url字符串
    :param admin_class:
    :return:
    """
    url = ""
    for item in admin_class.filter_conditions:
        url += "&&%s=%s" % item
    return url


@register.simple_tag
def get_search_filter_filed_value(filter_conditions):
    """
    根据查询条件，返回q条件的内容
    :param filter_conditions:
    :return:
    """
    for condition in filter_conditions:
        if condition[0] == 'q':
            return condition[1]
    return ''


@register.simple_tag
def get_search_filter_filed_name(admin_class):
    """
    返回admin类配置的search_field的字段名称
    :param admin_class:
    :return:
    """
    return_names = []
    for name in admin_class.search_fields:
        return_names.append(admin_class.model._meta.get_field(name).verbose_name)

    return mark_safe(','.join(return_names))


@register.simple_tag
def check_permission(user_obj, app_name, table_name, url):
    """
    判断是否具有权限
    :param user_obj:
    :param app_name:
    :param table_name:
    :param url:
    :return:
    """
    for one_role in user_obj.roles.all():
        for one_permission in one_role.permissions.all():
            if one_permission.app_name == app_name and one_permission.table_name == table_name and \
                    one_permission.url == url and one_permission.open:
                return True

        return False


@register.simple_tag
def get_menu_active_class(my_menu, table_name, menu_id):
    for sub_menu in my_menu[menu_id]['children']:
        for k,v in sub_menu.items():
            if v['table_name'] == table_name:
                return "active-sub active"
    return ""


@register.simple_tag
def get_menu_url_active_class(my_menu, table_name, menu_id):
    for k, v in my_menu.items():
        for sub_menu in v['children']:
            if menu_id in sub_menu and sub_menu[menu_id]['table_name'] == table_name:
                return "active-link"
    return ""


@register.simple_tag
def get_errors_message(errors, field_name):
    import json
    errors_obj = json.loads(errors)
    message_list = errors_obj.get(field_name)
    if message_list:
        return message_list[0].get('message')
    return ''


@register.simple_tag
def get_field_cn(admin_class, cloumn):
    """
    根据字段名显示中文
    :param admin_class:
    :param cloumn:
    :return:
    """
    return admin_class.field_display_cn.get(cloumn) or cloumn


@register.simple_tag
def check_parent(filter_conditions):
    """
    判断是否显示子菜单
    :param filter_conditions:
    :return:
    """
    if filter_conditions:
        for c in filter_conditions:
            if c[0] == 'parent':
                return False
    return True


@register.simple_tag
def get_cn_label(admin_class, label):
    """
    返回中文名称
    :param admin_class:
    :param label:
    :return:
    """
    label = str(label).replace(' ', '_').lower()
    return admin_class.field_display_cn.get(label) or label
