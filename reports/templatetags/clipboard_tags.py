from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def clipboard_button(text, button_text="复制", button_class="btn btn-outline-info btn-sm", 
                    icon_class="bi bi-clipboard", title="复制信息", **kwargs):
    """
    生成一个复制按钮，使用通用的复制功能
    参数:
    - text: 要复制的文本内容
    - button_text: 按钮显示的文本
    - button_class: 按钮的CSS类
    - icon_class: 图标的CSS类
    - title: 按钮的title属性
    - **kwargs: 额外的HTML属性
    """
    attrs = ' '.join([f'{k}="{v}"' for k, v in kwargs.items()])
    
    button_html = f'''
    <button type="button" class="{button_class}" onclick="copyToClipboard('{text}')" 
            title="{title}" {attrs}>
        <i class="{icon_class}"></i> {button_text}
    </button>
    '''
    
    return mark_safe(button_html)


@register.simple_tag
def clipboard_icon(text, icon_class="bi bi-clipboard", title="复制信息", **kwargs):
    """
    生成一个复制图标按钮
    参数:
    - text: 要复制的文本内容
    - icon_class: 图标的CSS类
    - title: 按钮的title属性
    - **kwargs: 额外的HTML属性
    """
    attrs = ' '.join([f'{k}="{v}"' for k, v in kwargs.items()])
    
    icon_html = f'''
    <button type="button" class="btn btn-link p-0 border-0" onclick="copyToClipboard('{text}')" 
            title="{title}" {attrs}>
        <i class="{icon_class}"></i>
    </button>
    '''
    
    return mark_safe(icon_html)


@register.simple_tag
def clipboard_textarea(text, textarea_id="clipboard-text", **kwargs):
    """
    生成一个隐藏的textarea用于复制复杂内容
    参数:
    - text: 要复制的文本内容
    - textarea_id: textarea的ID
    - **kwargs: 额外的HTML属性
    """
    attrs = ' '.join([f'{k}="{v}"' for k, v in kwargs.items()])
    
    textarea_html = f'''
    <textarea id="{textarea_id}" style="position: absolute; left: -9999px; top: -9999px;" {attrs}>
        {text}
    </textarea>
    '''
    
    return mark_safe(textarea_html)


@register.simple_tag
def clipboard_copy_function(element_id, button_text="复制", **kwargs):
    """
    生成复制特定元素内容的函数调用
    参数:
    - element_id: 包含要复制文本的元素的ID
    - button_text: 按钮显示的文本
    - **kwargs: 额外的HTML属性
    """
    attrs = ' '.join([f'{k}="{v}"' for k, v in kwargs.items()])
    
    function_html = f'''
    <button type="button" onclick="copyElementContent('{element_id}')" {attrs}>
        {button_text}
    </button>
    <script>
    function copyElementContent(elementId) {{
        const element = document.getElementById(elementId);
        if (element) {{
            copyToClipboard(element.textContent || element.value);
        }}
    }}
    </script>
    '''
    
    return mark_safe(function_html)
