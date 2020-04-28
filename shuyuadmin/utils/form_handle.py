from django.forms import ModelForm


def create_model_form(admin_class, add=False, show=False):

    class Meta:
        model = admin_class.model  # 指定类
        if admin_class.list_display:
            fields = admin_class.list_display
        else:
            fields = '__all__'  # 指定字段
        # exclude = admin_class.readonly_fields  # 排除指定的字段，也不会生成form对象
        if add:
            exclude = []

    def __new__(cls, *args, **kwargs):
        # 方法2：在实例化类对象（model_form()）的时候给input框增加样式
        for field_name, field_obj in cls.base_fields.items():
            print(field_name, field_obj)
            # # 单选
            # if isinstance(field_obj, TypedChoiceField):
            #     field_obj.widget.attrs.update({'id': 'demo-chosen-select'})
            # # 多选
            # elif isinstance(field_obj, ModelMultipleChoiceField):
            #     field_obj.widget.attrs.update({'id': 'demo-cs-multiselect'})
            #     field_obj.widget.attrs.update({'multiple': ''})
            #     field_obj.widget.attrs.update({'tabindex': '4'})
            # else:
            field_obj.widget.attrs.update({'class': 'form-control selectpicker'})  #　给当前字段对象增加样式
            #
            # if field_obj.label=='Content':
            #     # 设置textarea样式
            #     field_obj.widget.attrs.update({'cols':'100','rows':'10','class':'form-control'})
            #
            # # 筛选出教师角色为教师的对象
            # if field_name == 'teachers':
            #     field_obj._queryset = field_obj._queryset.filter(role__title='讲师')
            #
            # if field_name == 'consultant':
            #     field_obj._queryset = field_obj._queryset.filter(role__title='销售')
            #     pass
            #
            if show:
                field_obj.widget.attrs.update({'disabled': 'disabled'})

            if field_name in admin_class.readonly_fields:
                # 但是设置为disabled后，form表单不会提交数据
                if add:
                    pass
                else:
                    field_obj.widget.attrs.update({'readonly': 'readonly'})
        return ModelForm.__new__(cls)

    dynamic_form = type("DynamicModelForm", (ModelForm,), {'Meta': Meta, '__new__': __new__})

    return dynamic_form
