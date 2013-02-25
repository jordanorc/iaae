from django import template

register = template.Library()

@register.filter()
def results(view, object_list):
    list_display = view.list_display
    for object in object_list:
        for display in list_display:
            if not getattr(object, display, None):
                value = getattr(view, display, None)
                if value:
                    setattr(object, display, value(object))
                else:
                    setattr(object, display, None)
    return object_list


@register.filter()
def get_attribute(object, attr):
    return getattr(object, attr)