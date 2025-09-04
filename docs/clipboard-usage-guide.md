# 剪贴板功能使用指南

## 概述

本项目提供了统一的剪贴板复制功能，支持跨浏览器兼容性和移动设备适配。所有复制功能都通过 `static/js/clipboard-utils.js` 文件提供。

## 核心功能

### copyToClipboard(text, options)

主要的复制函数，支持多种配置选项：

```javascript
copyToClipboard(text, {
    successMessage: '复制成功',      // 成功提示消息
    errorMessage: '复制失败',        // 失败提示消息  
    showToast: true,                // 是否显示提示
    toastPosition: 'top-right',     // 提示位置
    fallbackToSelect: true,         // 是否降级到选择方法
    mobileFriendly: true            // 是否启用移动设备优化
});
```

## 使用方法

### 1. 基本使用

```javascript
// 简单复制
copyToClipboard('要复制的文本');

// 带配置的复制
copyToClipboard('要复制的文本', {
    successMessage: '文本已复制',
    errorMessage: '复制失败，请手动复制'
});
```

### 2. 在模板中使用

在Django模板中，可以使用自定义模板标签：

```html
{% load clipboard_tags %}

<!-- 复制按钮 -->
{% clipboard_button text="要复制的文本" class="btn btn-info" %}

<!-- 复制图标 -->
{% clipboard_icon text="要复制的文本" %}

<!-- 复制文本区域 -->
{% clipboard_textarea text="要复制的文本" rows="3" %}

<!-- 自定义复制函数 -->
<button onclick="{% clipboard_copy_function '要复制的文本' %}">复制</button>
```

### 3. 在管理后台使用

在Django Admin中，使用新的copy_text方法：

```python
def copy_text(self, request, queryset):
    text = "\n".join([str(obj) for obj in queryset])
    return JsonResponse({
        'success': True,
        'message': '数据已准备复制',
        'text': text
    })
copy_text.short_description = "复制选中项"
```

## 配置选项

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| successMessage | string | '复制成功' | 成功时的提示消息 |
| errorMessage | string | '复制失败' | 失败时的提示消息 |
| showToast | boolean | true | 是否显示提示消息 |
| toastPosition | string | 'top-right' | 提示消息位置 |
| fallbackToSelect | boolean | true | 是否启用降级方案 |
| mobileFriendly | boolean | true | 是否启用移动设备优化 |

## 浏览器兼容性

- ✅ Chrome 43+
- ✅ Firefox 41+  
- ✅ Safari 10+
- ✅ Edge 12+
- ✅ iOS Safari 10+
- ✅ Android Browser 4.4+

## 移动设备支持

自动检测移动设备并提供优化的复制体验：
- 触摸设备上的长按提示
- 自动选择文本区域
- 友好的错误处理

## 错误处理

系统提供完善的错误处理机制：
- 权限拒绝时的友好提示
- 不支持的浏览器降级方案
- 详细的错误日志记录

## 最佳实践

1. **始终提供配置选项**：使用完整的配置以确保最佳用户体验
2. **处理错误情况**：确保有适当的错误处理机制
3. **移动设备优化**：考虑移动设备的特殊需求
4. **用户反馈**：提供清晰的成功/失败反馈

## 示例

### 完整配置示例

```javascript
function copyProductInfo(name, batch, supplier) {
    const text = `产品: ${name}\n批号: ${batch}\n供应商: ${supplier}`;
    copyToClipboard(text, {
        successMessage: '产品信息已复制',
        errorMessage: '复制失败，请手动复制文本',
        showToast: true,
        toastPosition: 'top-right',
        fallbackToSelect: true,
        mobileFriendly: true
    });
}
```

### 模板标签示例

```html
{% load clipboard_tags %}

<div class="product-info">
    <h4>{{ product.name }}</h4>
    <p>批号: {{ product.batch }}</p>
    <p>供应商: {{ product.supplier }}</p>
    
    <!-- 使用模板标签 -->
    {% clipboard_button 
        text="产品: {{ product.name }}\n批号: {{ product.batch }}\n供应商: {{ product.supplier }}"
        class="btn btn-sm btn-outline-info"
        success_message="产品信息已复制"
    %}
</div>
