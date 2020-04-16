from django.db import models
from shuyuadmin.models import MyUser, Role, Menu, Permission


def create_all_menu_dic():
    """
    将所有的菜单生成一个字典，生成对菜单一级和二级都默认不生效，配合权限进行控制
    :return:
    """
    all_menu_dic = {}
    # 先生成一级菜单
    for m in Menu.objects.all().filter(parent=None).order_by('sort_index'):
        if not m.open:
            continue
        tmp_dic = {}
        tmp_dic.update(m.__dict__)
        tmp_dic['status'] = False
        tmp_dic['children'] = []
        del tmp_dic['_state']
        menu_dic = {
            m.id: tmp_dic
        }
        all_menu_dic.update(menu_dic)

    # 添加二级菜单
    for m in Menu.objects.all().order_by('sort_index'):
        if not m.open:
            continue
        tmp_dic = {}
        tmp_dic.update(m.__dict__)
        tmp_dic['status'] = False
        tmp_dic['children'] = []
        del tmp_dic['_state']
        menu_dic = {
            m.id: tmp_dic
        }

        if m.parent and m.parent.open:
            all_menu_dic[m.parent_id]['children'].append(menu_dic)
    return all_menu_dic


def get_permissions_menu(user_obj):
    """
    根据用户获取角色，根据角色获取权限，根据权限的菜单id 设置该用户拥有的菜单权限的status为True
    :param user_obj:
    :return:
    """
    import copy
    my_menu_dic = copy.deepcopy(create_all_menu_dic())
    # 获取对应的角色
    for one_role in user_obj.roles.all():
        for one_permission in one_role.permissions.all():
            one_menu = one_permission.menu
            if one_menu.parent_id:
                if not my_menu_dic.get(one_menu.parent_id):
                    continue
                for m in my_menu_dic[one_menu.parent_id].get('children'):
                    if one_menu.id in m:
                        m[one_menu.id]['app_name'] = one_permission.app_name
                        m[one_menu.id]['table_name'] = one_permission.table_name
                        # 如果一个权限有权限，即能访问该菜单
                        if m[one_menu.id].get('status'):
                            continue
                        if one_permission.open and one_menu.open:
                            m[one_menu.id]['status'] = True
                            my_menu_dic[one_menu.parent_id]['status'] = True
    return my_menu_dic
