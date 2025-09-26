#!/usr/bin/env python3

with open("static/index.html", "r") as f:
    html = f.read()

# Modal HTML ekle (body tag'inden hemen sonra)
modal_html = '''
    <!-- File Upload Modal -->
    <div id="fileModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 10px; width: 500px;">
            <h3 style="margin-bottom: 20px;">File Uploaded</h3>
            <div id="filePreview" style="max-height: 300px; overflow-y: auto; background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-family: monospace; font-size: 12px; white-space: pre-wrap;"></div>
            <div style="display: flex; justify-content: space-between;">
                <button onclick="closeFileModal()" style="padding: 10px 20px; background: #ccc; border: none; border-radius: 5px; cursor: pointer;">Cancel</button>
                <button onclick="sendFileContent()" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">Send to Agents</button>
            </div>
        </div>
    </div>
'''

# Body tag'inden sonra ekle
html = html.replace('<body>', '<body>\n' + modal_html)

# JavaScript'i güncelle
new_js = '''
    let uploadedFileContent = '';
    let uploadedFileName = '';
    
    function handleFileUpload() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.txt,.json,.md,.py,.csv';
        input.onchange = (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            uploadedFileName = file.name;
            const reader = new FileReader();
            reader.onload = (event) => {
                uploadedFileContent = event.target.result;
                // Show modal with preview
                document.getElementById('filePreview').textContent = uploadedFileContent.substring(0, 2000) + (uploadedFileContent.length > 2000 ? '\\n\\n... (truncated)' : '');
                document.getElementById('fileModal').style.display = 'block';
            };
            reader.readAsText(file);
        };
        input.click();
    }
    
    function closeFileModal() {
        document.getElementById('fileModal').style.display = 'none';
    }
    
    function sendFileContent() {
        // Send as a structured message
        const message = `I've uploaded ${uploadedFileName}. Please analyze this file and proceed with the task.`;
        
        ws.send(JSON.stringify({
            type: 'user_message',
            message: message,
            attachment: {
                filename: uploadedFileName,
                content: uploadedFileContent
            }
        }));
        
        // Show in chat
        document.getElementById('messageInput').value = `Uploaded: ${uploadedFileName}`;
        closeFileModal();
    }
'''

# Replace the old handleFileUpload function
import re
pattern = r'function handleFileUpload\(\).*?\n    \}'
html = re.sub(pattern, new_js.strip(), html, flags=re.DOTALL)

with open("static/index.html", "w") as f:
    f.write(html)

print("✅ File upload modal added!")
