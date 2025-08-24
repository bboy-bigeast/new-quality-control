function copyToClipboard() {
    const text = document.getElementById('copy-text-content').textContent;
    navigator.clipboard.writeText(text).then(() => {
        alert('已复制到剪贴板！');
    }).catch(err => {
        console.error('复制失败:', err);
        alert('复制失败，请手动复制文本内容');
    });
}
