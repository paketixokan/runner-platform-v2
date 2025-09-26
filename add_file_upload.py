#!/usr/bin/env python3

html_update = '''
<!-- Add to input-toolbar in templates/dashboard.html -->
<input type="file" id="fileUpload" accept=".txt,.json,.md,.py" style="display:none">
<button class="tool-btn" onclick="document.getElementById('fileUpload').click()">
    <span class="icon">📁</span> Upload
</button>
'''

js_code = '''
document.getElementById('fileUpload').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async (event) => {
        const content = event.target.result;
        const message = `File uploaded: ${file.name}\\n\\nContent:\\n${content}`;
        
        // Send to agents
        ws.send(JSON.stringify({
            type: 'user_message',
            message: message
        }));
    };
    reader.readAsText(file);
});
'''

print("File upload code ready")
print("Add this to your frontend")
