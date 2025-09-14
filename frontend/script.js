// API Base URL - Modify according to your actual deployment address
const API_BASE_URL = 'http://localhost:5001';

// Global variables
let personImageUrl = null;
let garmentImageUrl = null;

// DOM elements
const personPreview = document.getElementById('person-preview');
const personPlaceholder = document.getElementById('person-placeholder');
const personFile = document.getElementById('person-file');
const personPreviewContainer = document.getElementById('person-preview-container');

const garmentPreview = document.getElementById('garment-preview');
const garmentPlaceholder = document.getElementById('garment-placeholder');
const garmentFile = document.getElementById('garment-file');
const garmentType = document.getElementById('garment-type');
const garmentPreviewContainer = document.getElementById('garment-preview-container');

const tryonBtn = document.getElementById('tryon-btn');
const resultSection = document.getElementById('result-section');
const loading = document.getElementById('loading');
const progressText = document.getElementById('progress-text');
const resultImageContainer = document.getElementById('result-image-container');
const resultImage = document.getElementById('result-image');
const errorMessage = document.getElementById('error-message');
const errorDetail = document.getElementById('error-detail');

const downloadBtn = document.getElementById('download-btn');
const tryAgainBtn = document.getElementById('try-again-btn');
const retryBtn = document.getElementById('retry-btn');

// Initialize event listeners
document.addEventListener('DOMContentLoaded', init);

function init() {
    console.log('Initializing...');
    console.log('personPreviewContainer:', personPreviewContainer);
    console.log('garmentPreviewContainer:', garmentPreviewContainer);
    
    // Person photo upload
    if (personPreviewContainer) {
        personPreviewContainer.addEventListener('click', () => {
            console.log('Person preview clicked');
            if (personFile) {
                personFile.click();
            }
        });
    }
    
    if (personFile) {
        personFile.addEventListener('change', (e) => {
            console.log('Person file changed');
            handleFileUpload(e, 'person');
        });
    }
    
    // Garment photo upload
    if (garmentPreviewContainer) {
        garmentPreviewContainer.addEventListener('click', () => {
            console.log('Garment preview clicked');
            if (garmentFile) {
                garmentFile.click();
            }
        });
    }
    
    if (garmentFile) {
        garmentFile.addEventListener('change', (e) => {
            console.log('Garment file changed');
            handleFileUpload(e, 'garment');
        });
    }
    
    // Try-on button
    if (tryonBtn) {
        tryonBtn.addEventListener('click', startTryOn);
    }
    
    // Result area buttons
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadResult);
    }
    if (tryAgainBtn) {
        tryAgainBtn.addEventListener('click', resetAndTryAgain);
    }
    if (retryBtn) {
        retryBtn.addEventListener('click', retryTask);
    }
    
    // Drag and drop functionality
    if (personPreviewContainer) {
        setupDragAndDrop(personPreviewContainer, 'person');
    }
    if (garmentPreviewContainer) {
        setupDragAndDrop(garmentPreviewContainer, 'garment');
    }
}

function setupDragAndDrop(element, type) {
    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.classList.add('dragover');
    });
    
    element.addEventListener('dragleave', () => {
        element.classList.remove('dragover');
    });
    
    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.classList.remove('dragover');
        
        if (e.dataTransfer.files.length) {
            const file = e.dataTransfer.files[0];
            handleDroppedFile(file, type);
        }
    });
}

function handleDroppedFile(file, type) {
    console.log('handleDroppedFile called with type:', type, 'file:', file);
    
    if (!file.type.match('image.*')) {
        showNotification('Please upload an image file', 'error');
        return;
    }
    
    const preview = type === 'person' ? personPreview : garmentPreview;
    const placeholder = type === 'person' ? personPlaceholder : garmentPlaceholder;
    
    const reader = new FileReader();
    reader.onload = (e) => {
        console.log('File reader loaded');
        preview.src = e.target.result;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
        
        // Upload file to server
        uploadFile(file, type);
    };
    reader.readAsDataURL(file);
}

function handleFileUpload(event, type) {
    console.log('handleFileUpload called with type:', type);
    const file = event.target.files[0];
    console.log('Selected file:', file);
    if (!file) {
        console.log('No file selected');
        return;
    }
    
    handleDroppedFile(file, type);
}

function uploadFile(file, type) {
    console.log('uploadFile called with type:', type, 'file:', file);
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show upload progress
    showUploadProgress(type);
    
    fetch(`${API_BASE_URL}/api/tryon/upload`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Upload response:', data);
        if (data.error) {
            showNotification(`Upload failed: ${data.error}`, 'error');
            resetPreview(type);
            return;
        }
        
        if (type === 'person') {
            personImageUrl = data.url;
        } else {
            garmentImageUrl = data.url;
        }
        
        showNotification('Image uploaded successfully', 'success');
        updateTryonButtonState();
    })
    .catch(error => {
        console.error('Upload error:', error);
        showNotification('An error occurred while uploading the file', 'error');
        resetPreview(type);
    });
}

function showUploadProgress(type) {
    const container = type === 'person' ? personPreviewContainer : garmentPreviewContainer;
    const progress = document.createElement('div');
    progress.className = 'upload-progress';
    progress.innerHTML = `
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        <span class="progress-text">Uploading...</span>
    `;
    
    // Add progress bar styles
    const style = document.createElement('style');
    style.textContent = `
        .upload-progress {
            position: absolute;
            bottom: 10px;
            left: 10px;
            right: 10px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .progress-bar {
            width: 100%;
            height: 4px;
            background: #e5e7eb;
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            width: 0%;
            transition: width 0.3s ease;
        }
        .progress-text {
            font-size: 12px;
            color: #6b7280;
        }
    `;
    document.head.appendChild(style);
    
    container.appendChild(progress);
    
    // Simulate progress
    let width = 0;
    const interval = setInterval(() => {
        width += Math.random() * 15;
        if (width >= 100) {
            width = 100;
            clearInterval(interval);
            setTimeout(() => {
                if (progress.parentNode) {
                    progress.parentNode.removeChild(progress);
                }
            }, 500);
        }
        progress.querySelector('.progress-fill').style.width = width + '%';
    }, 200);
}

function resetPreview(type) {
    if (type === 'person') {
        personPreview.style.display = 'none';
        personPlaceholder.style.display = 'block';
        personImageUrl = null;
    } else {
        garmentPreview.style.display = 'none';
        garmentPlaceholder.style.display = 'block';
        garmentImageUrl = null;
    }
    updateTryonButtonState();
}

function updateTryonButtonState() {
    const isReady = personImageUrl && garmentImageUrl;
    if (tryonBtn) {
        tryonBtn.disabled = !isReady;
    }
}

function showError(message) {
    if (loading) loading.style.display = 'none';
    if (errorMessage) {
        errorMessage.style.display = 'block';
        if (errorDetail) errorDetail.textContent = message;
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add notification styles
    const style = document.createElement('style');
    style.textContent = `
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
        }
        .notification-success {
            background: #10b981;
        }
        .notification-error {
            background: #ef4444;
        }
        .notification-info {
            background: #6366f1;
        }
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function downloadResult() {
    if (!resultImage || !resultImage.src) return;
    
    const link = document.createElement('a');
    link.href = resultImage.src;
    link.download = 'paida-virtual-tryon-result.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Image download started', 'success');
}

function resetAndTryAgain() {
    if (resultSection) {
        resultSection.style.display = 'none';
    }
}

function retryTask() {
    startTryOn();
}

async function startTryOn() {
    if (!personImageUrl || !garmentImageUrl) return;
    
    console.log('Starting try-on...');
    
    // Disable button to prevent multiple clicks
    if (tryonBtn) {
        tryonBtn.disabled = true;
        tryonBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Processing...</span>';
    }
    
    // Show result area and loading state
    if (resultSection) {
        resultSection.style.display = 'block';
    }
    if (loading) {
        loading.style.display = 'flex';
    }
    if (resultImageContainer) {
        resultImageContainer.style.display = 'none';
    }
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }
    
    const selectedGarmentType = garmentType ? garmentType.value : 'top';
    
    try {
        // Submit try-on request
        const response = await fetch(`${API_BASE_URL}/api/tryon/direct`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                person_image_url: personImageUrl,
                garment_image_url: garmentImageUrl,
                garment_type: selectedGarmentType
            })
        });
        
        const data = await response.json();
        console.log('Try-on response:', data);
        
        if (data.status === 'success') {
            // Display result image directly
            if (resultImage) {
                resultImage.src = data.image_url;
            }
            if (loading) {
                loading.style.display = 'none';
            }
            if (resultImageContainer) {
                resultImageContainer.style.display = 'block';
            }
            showNotification('Try-on completed!', 'success');
        } else if (data.status === 'submitted') {
            // For now, just show a message about polling
            showNotification('Try-on submitted, please wait...', 'info');
        } else if (data.status === 'error') {
            throw new Error(data.message);
        } else {
            throw new Error('Unknown response status');
        }
    } catch (error) {
        console.error('Try-on error:', error);
        showError(error.message);
        showNotification('Try-on failed, please retry', 'error');
    } finally {
        // Restore button state
        if (tryonBtn) {
            tryonBtn.disabled = false;
            tryonBtn.innerHTML = '<i class="fas fa-magic"></i><span>Start AI Try-On</span>';
        }
    }
}