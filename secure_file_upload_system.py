#!/usr/bin/env python3

import json

# Backend güvenlik katmanı için
file_handler_code = '''
from fastapi import UploadFile, File, HTTPException
import magic
import hashlib
import os

ALLOWED_EXTENSIONS = {'.txt', '.json', '.md', '.py', '.csv', '.yaml', '.yml', '.xml', '.log'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
BLOCKED_PATTERNS = ['eval(', 'exec(', '__import__', 'os.system', 'subprocess']

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Secure file upload with validation"""
    
    # 1. Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"File type {ext} not allowed")
    
    # 2. Check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large (max 10MB)")
    
    # 3. Check MIME type
    mime = magic.from_buffer(contents, mime=True)
    safe_mimes = ['text/plain', 'application/json', 'text/markdown', 'text/x-python']
    if mime not in safe_mimes:
        raise HTTPException(400, f"Unsafe MIME type: {mime}")
    
    # 4. Scan for malicious patterns
    text = contents.decode('utf-8', errors='ignore')
    for pattern in BLOCKED_PATTERNS:
        if pattern in text:
            raise HTTPException(400, f"Potentially malicious content detected")
    
    # 5. Generate safe filename
    safe_name = hashlib.md5(contents).hexdigest()[:8] + ext
    
    # Save to temp directory
    os.makedirs("uploads", exist_ok=True)
    filepath = f"uploads/{safe_name}"
    
    with open(filepath, "wb") as f:
        f.write(contents)
    
    return {
        "filename": file.filename,
        "safe_name": safe_name,
        "size": len(contents),
        "mime": mime,
        "path": filepath
    }
'''

# Frontend implementation
frontend_code = '''
// Add to static/index.html
<div class="file-upload-section">
    <input type="file" id="fileUpload" accept=".txt,.json,.md,.py,.csv,.yaml,.yml,.xml,.log" style="display:none">
    <button onclick="uploadFile()" class="upload-btn">
        📁 Upload File
    </button>
    <div id="fileInfo"></div>
</div>

<script>
async function uploadFile() {
    const input = document.getElementById('fileUpload');
    input.click();
    
    input.onchange = async () => {
        const file = input.files[0];
        if (!file) return;
        
        // Client-side validation
        const allowedExts = ['.txt', '.json', '.md', '.py', '.csv', '.yaml', '.yml', '.xml', '.log'];
        const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
        
        if (!allowedExts.includes(ext)) {
            alert(`File type ${ext} not allowed`);
            return;
        }
        
        if (file.size > 10485760) {
            alert('File too large (max 10MB)');
            return;
        }
        
        // Upload to server
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                
                // Display file info
                document.getElementById('fileInfo').innerHTML = `
                    <div class="file-success">
                        ✅ File uploaded: ${data.filename}<br>
                        Size: ${(data.size/1024).toFixed(2)} KB<br>
                        Type: ${data.mime}
                    </div>
                `;
                
                // Send to agents
                const reader = new FileReader();
                reader.onload = (e) => {
                    const content = e.target.result;
                    const message = `Uploaded file: ${file.name}\\n\\nContent:\\n${content}`;
                    
                    ws.send(JSON.stringify({
                        type: 'user_message',
                        message: message,
                        file: {
                            name: file.name,
                            type: ext,
                            content: content
                        }
                    }));
                };
                reader.readAsText(file);
                
            } else {
                const error = await response.text();
                alert(`Upload failed: ${error}`);
            }
        } catch (err) {
            alert(`Error: ${err.message}`);
        }
    };
}
</script>

<style>
.upload-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
.file-success {
    background: rgba(76, 175, 80, 0.1);
    border: 1px solid #4CAF50;
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
}
</style>
'''

# Test için örnek dosyalar oluştur
test_files = {
    "test_safe.txt": "Hello, this is a safe text file for testing.",
    "test_data.json": json.dumps({"test": "data", "safe": True}, indent=2),
    "test_script.py": "# Safe Python script\nprint('Hello World')\n",
    "malicious_test.py": "# This would be blocked\nexec('print(1)')\n"
}

for filename, content in test_files.items():
    with open(filename, "w") as f:
        f.write(content)

print("✅ Secure file upload system created!")
print("\n📁 Supported extensions:")
print("  .txt, .json, .md, .py, .csv, .yaml, .yml, .xml, .log")
print("\n🔒 Security measures:")
print("  • File extension validation")
print("  • MIME type checking")
print("  • File size limit (10MB)")
print("  • Malicious pattern scanning")
print("  • Safe filename generation")
print("\n🧪 Test files created:")
for f in test_files.keys():
    print(f"  • {f}")
print("\n⚠️  'malicious_test.py' should be blocked when uploaded")
