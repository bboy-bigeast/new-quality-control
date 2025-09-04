/**
 * 通用剪贴板工具类 - 提供跨浏览器兼容的复制功能
 * 支持多种复制方法，确保在不同设备和浏览器上都能正常工作
 */

class ClipboardUtils {
    /**
     * 检查浏览器是否支持现代剪贴板API
     */
    static isClipboardAPISupported() {
        return navigator.clipboard && typeof navigator.clipboard.writeText === 'function';
    }

    /**
     * 检查浏览器是否支持传统的execCommand复制方法
     */
    static isExecCommandSupported() {
        return document.queryCommandSupported && document.queryCommandSupported('copy');
    }

    /**
     * 使用现代Clipboard API复制文本
     */
    static async copyWithClipboardAPI(text) {
        try {
            await navigator.clipboard.writeText(text);
            return { success: true, method: 'clipboard-api' };
        } catch (error) {
            console.warn('Clipboard API复制失败:', error);
            return { success: false, error, method: 'clipboard-api' };
        }
    }

    /**
     * 使用传统的execCommand方法复制文本
     */
    static copyWithExecCommand(text) {
        try {
            // 创建临时textarea元素
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.top = 0;
            textarea.style.left = 0;
            textarea.style.opacity = 0;
            
            document.body.appendChild(textarea);
            textarea.select();
            textarea.setSelectionRange(0, textarea.value.length);
            
            const success = document.execCommand('copy');
            document.body.removeChild(textarea);
            
            return { success, method: 'exec-command' };
        } catch (error) {
            console.warn('execCommand复制失败:', error);
            return { success: false, error, method: 'exec-command' };
        }
    }

    /**
     * 使用临时元素和选择方法复制文本（降级方案）
     */
    static copyWithSelection(text) {
        try {
            const tempElement = document.createElement('div');
            tempElement.textContent = text;
            tempElement.style.whiteSpace = 'pre-wrap';
            tempElement.style.position = 'fixed';
            tempElement.style.top = 0;
            tempElement.style.left = 0;
            tempElement.style.opacity = 0;
            
            document.body.appendChild(tempElement);
            
            const range = document.createRange();
            range.selectNodeContents(tempElement);
            
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            
            let success = false;
            try {
                success = document.execCommand('copy');
            } catch (e) {
                console.warn('选择复制方法失败:', e);
            }
            
            selection.removeAllRanges();
            document.body.removeChild(tempElement);
            
            return { success, method: 'selection' };
        } catch (error) {
            console.warn('选择复制方法失败:', error);
            return { success: false, error, method: 'selection' };
        }
    }

    /**
     * 通用的复制文本方法，自动选择最佳方案
     */
    static async copyText(text, options = {}) {
        const {
            showSuccess = true,
            showError = true,
            successMessage = '已复制到剪贴板！',
            errorMessage = '复制失败，请手动复制文本内容',
            fallbackToPrompt = true
        } = options;

        // 尝试现代Clipboard API
        if (this.isClipboardAPISupported()) {
            const result = await this.copyWithClipboardAPI(text);
            if (result.success) {
                if (showSuccess) this.showNotification(successMessage, 'success');
                return result;
            }
        }

        // 尝试传统execCommand方法
        if (this.isExecCommandSupported()) {
            const result = this.copyWithExecCommand(text);
            if (result.success) {
                if (showSuccess) this.showNotification(successMessage, 'success');
                return result;
            }
        }

        // 尝试选择方法
        const selectionResult = this.copyWithSelection(text);
        if (selectionResult.success) {
            if (showSuccess) this.showNotification(successMessage, 'success');
            return selectionResult;
        }

        // 所有方法都失败，提供降级方案
        if (fallbackToPrompt) {
            const userConfirmed = confirm(`${errorMessage}\n\n文本内容:\n${text}\n\n是否要手动复制？`);
            if (userConfirmed) {
                // 自动选择文本以便用户手动复制
                this.selectTextForManualCopy(text);
            }
        } else if (showError) {
            this.showNotification(errorMessage, 'error');
        }

        return { success: false, method: 'fallback' };
    }

    /**
     * 显示通知消息
     */
    static showNotification(message, type = 'info') {
        // 尝试使用Bootstrap的toast（如果可用）
        if (typeof bootstrap !== 'undefined' && bootstrap.Toast) {
            const toastElement = document.createElement('div');
            toastElement.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
            toastElement.setAttribute('role', 'alert');
            toastElement.setAttribute('aria-live', 'assertive');
            toastElement.setAttribute('aria-atomic', 'true');
            
            toastElement.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            document.body.appendChild(toastElement);
            new bootstrap.Toast(toastElement, { delay: 3000 }).show();
            
            // 自动移除toast元素
            setTimeout(() => {
                if (toastElement.parentNode) {
                    toastElement.parentNode.removeChild(toastElement);
                }
            }, 3500);
        } else {
            // 降级到alert
            alert(message);
        }
    }

    /**
     * 选择文本以便用户手动复制
     */
    static selectTextForManualCopy(text) {
        const tempTextarea = document.createElement('textarea');
        tempTextarea.value = text;
        tempTextarea.style.position = 'fixed';
        tempTextarea.style.top = '50%';
        tempTextarea.style.left = '50%';
        tempTextarea.style.transform = 'translate(-50%, -50%)';
        tempTextarea.style.width = '80%';
        tempTextarea.style.height = '100px';
        tempTextarea.style.zIndex = '10000';
        
        document.body.appendChild(tempTextarea);
        tempTextarea.select();
        
        // 添加关闭按钮
        const closeButton = document.createElement('button');
        closeButton.textContent = '关闭';
        closeButton.style.position = 'fixed';
        closeButton.style.top = 'calc(50% + 60px)';
        closeButton.style.left = '50%';
        closeButton.style.transform = 'translateX(-50%)';
        closeButton.style.zIndex = '10001';
        closeButton.onclick = () => {
            document.body.removeChild(tempTextarea);
            document.body.removeChild(closeButton);
        };
        
        document.body.appendChild(closeButton);
    }

    /**
     * 检测移动设备
     */
    static isMobileDevice() {
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    }

    /**
     * 获取浏览器兼容性信息
     */
    static getCompatibilityInfo() {
        return {
            clipboardAPI: this.isClipboardAPISupported(),
            execCommand: this.isExecCommandSupported(),
            isMobile: this.isMobileDevice(),
            userAgent: navigator.userAgent
        };
    }
}

// 全局导出
window.ClipboardUtils = ClipboardUtils;

// 提供简化的全局函数用于向后兼容
window.copyToClipboard = async function(text, options = {}) {
    return await ClipboardUtils.copyText(text, options);
};

// 自动初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('ClipboardUtils已加载，兼容性信息:', ClipboardUtils.getCompatibilityInfo());
});
