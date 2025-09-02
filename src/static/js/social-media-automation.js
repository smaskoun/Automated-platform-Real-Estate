/**
 * Social Media Automation Module
 * Handles Facebook/Instagram authentication, posting, and AI image generation
 */

class SocialMediaAutomation {
    constructor() {
        this.apiBase = '/api';
        this.connectedAccounts = [];
        this.currentUser = 'default_user'; // In production, get from authentication
        this.init();
    }

    async init() {
        await this.loadConnectedAccounts();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Connect account button
        const connectBtn = document.getElementById('connect-social-account');
        if (connectBtn) {
            connectBtn.addEventListener('click', () => this.initiateConnection());
        }

        // Generate image button
        const generateImageBtn = document.getElementById('generate-image-btn');
        if (generateImageBtn) {
            generateImageBtn.addEventListener('click', () => this.generateImage());
        }

        // Create post button
        const createPostBtn = document.getElementById('create-post-btn');
        if (createPostBtn) {
            createPostBtn.addEventListener('click', () => this.createPost());
        }

        // Approve post buttons (delegated event listener)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('approve-post-btn')) {
                const postId = e.target.dataset.postId;
                this.approvePost(postId);
            }
        });

        // Publish post buttons (delegated event listener)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('publish-post-btn')) {
                const postId = e.target.dataset.postId;
                this.publishPost(postId);
            }
        });
    }

    async loadConnectedAccounts() {
        try {
            const response = await fetch(`${this.apiBase}/accounts?user_id=${this.currentUser}`);
            const data = await response.json();
            
            if (data.accounts) {
                this.connectedAccounts = data.accounts;
                this.updateAccountsUI();
            }
        } catch (error) {
            console.error('Error loading connected accounts:', error);
        }
    }

    updateAccountsUI() {
        const accountsList = document.getElementById('connected-accounts-list');
        if (!accountsList) return;

        if (this.connectedAccounts.length === 0) {
            accountsList.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <p>No social media accounts connected</p>
                    <button id="connect-first-account" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                        Connect Your First Account
                    </button>
                </div>
            `;
            
            document.getElementById('connect-first-account').addEventListener('click', () => {
                this.initiateConnection();
            });
        } else {
            accountsList.innerHTML = this.connectedAccounts.map(account => `
                <div class="flex items-center justify-between p-4 border rounded-lg">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 rounded-full bg-${account.platform === 'facebook' ? 'blue' : 'pink'}-500 flex items-center justify-center text-white font-bold">
                            ${account.platform === 'facebook' ? 'F' : 'I'}
                        </div>
                        <div>
                            <p class="font-medium">${account.account_name}</p>
                            <p class="text-sm text-gray-500">${account.platform}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <span class="px-2 py-1 text-xs rounded-full ${account.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                            ${account.is_active ? 'Active' : 'Inactive'}
                        </span>
                        <button onclick="socialMediaAutomation.disconnectAccount(${account.id})" 
                                class="text-red-500 hover:text-red-700">
                            Disconnect
                        </button>
                    </div>
                </div>
            `).join('');
        }
    }

    async initiateConnection() {
        try {
            const response = await fetch(`${this.apiBase}/auth/facebook/login`);
            const data = await response.json();
            
            if (data.auth_url) {
                // Open Facebook OAuth in a popup
                const popup = window.open(
                    data.auth_url,
                    'facebook-auth',
                    'width=600,height=600,scrollbars=yes,resizable=yes'
                );

                // Listen for the popup to close
                const checkClosed = setInterval(() => {
                    if (popup.closed) {
                        clearInterval(checkClosed);
                        // Reload accounts after authentication
                        setTimeout(() => this.loadConnectedAccounts(), 1000);
                    }
                }, 1000);
            }
        } catch (error) {
            console.error('Error initiating Facebook connection:', error);
            this.showNotification('Failed to initiate Facebook connection', 'error');
        }
    }

    async disconnectAccount(accountId) {
        if (!confirm('Are you sure you want to disconnect this account?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/accounts/${accountId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showNotification('Account disconnected successfully', 'success');
                await this.loadConnectedAccounts();
            } else {
                throw new Error('Failed to disconnect account');
            }
        } catch (error) {
            console.error('Error disconnecting account:', error);
            this.showNotification('Failed to disconnect account', 'error');
        }
    }

    async generateImage() {
        const promptInput = document.getElementById('image-prompt-input');
        const platformSelect = document.getElementById('platform-select');
        const generateBtn = document.getElementById('generate-image-btn');
        const imagePreview = document.getElementById('generated-image-preview');

        if (!promptInput || !promptInput.value.trim()) {
            this.showNotification('Please enter an image prompt', 'warning');
            return;
        }

        const prompt = promptInput.value.trim();
        const platform = platformSelect ? platformSelect.value : 'instagram';

        // Show loading state
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        
        if (imagePreview) {
            imagePreview.innerHTML = '<div class="text-center py-8">Generating image...</div>';
        }

        try {
            const response = await fetch(`${this.apiBase}/images/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    platform: platform,
                    content_type: 'post'
                })
            });

            const data = await response.json();

            if (data.success && data.image.image_url) {
                // Display generated image
                if (imagePreview) {
                    imagePreview.innerHTML = `
                        <div class="text-center">
                            <img src="${data.image.image_url}" alt="Generated image" 
                                 class="max-w-full h-auto rounded-lg shadow-lg mx-auto mb-4">
                            <p class="text-sm text-gray-600">
                                Generated in ${data.image.generation_time?.toFixed(1) || 'N/A'}s
                            </p>
                            <button onclick="socialMediaAutomation.useGeneratedImage('${data.image.image_url}')"
                                    class="mt-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
                                Use This Image
                            </button>
                        </div>
                    `;
                }
                
                this.showNotification('Image generated successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to generate image');
            }
        } catch (error) {
            console.error('Error generating image:', error);
            this.showNotification('Failed to generate image: ' + error.message, 'error');
            
            if (imagePreview) {
                imagePreview.innerHTML = '<div class="text-center py-8 text-red-500">Failed to generate image</div>';
            }
        } finally {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Image';
        }
    }

    useGeneratedImage(imageUrl) {
        const imageUrlInput = document.getElementById('post-image-url');
        if (imageUrlInput) {
            imageUrlInput.value = imageUrl;
            this.showNotification('Image added to post', 'success');
        }
    }

    async createPost() {
        const contentInput = document.getElementById('post-content-input');
        const imageUrlInput = document.getElementById('post-image-url');
        const imagePromptInput = document.getElementById('post-image-prompt');
        const accountSelect = document.getElementById('post-account-select');
        const scheduledInput = document.getElementById('post-scheduled-time');

        if (!contentInput || !contentInput.value.trim()) {
            this.showNotification('Please enter post content', 'warning');
            return;
        }

        if (!accountSelect || !accountSelect.value) {
            this.showNotification('Please select an account', 'warning');
            return;
        }

        const postData = {
            account_id: parseInt(accountSelect.value),
            content: contentInput.value.trim(),
            image_url: imageUrlInput ? imageUrlInput.value : null,
            image_prompt: imagePromptInput ? imagePromptInput.value : null,
            scheduled_at: scheduledInput ? scheduledInput.value : null,
            hashtags: this.extractHashtags(contentInput.value)
        };

        try {
            const response = await fetch(`${this.apiBase}/posts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Post created successfully!', 'success');
                this.clearPostForm();
                await this.loadPosts(); // Refresh posts list
            } else {
                throw new Error(data.error || 'Failed to create post');
            }
        } catch (error) {
            console.error('Error creating post:', error);
            this.showNotification('Failed to create post: ' + error.message, 'error');
        }
    }

    extractHashtags(content) {
        const hashtags = content.match(/#[a-zA-Z0-9_]+/g);
        return hashtags ? hashtags.map(tag => tag.substring(1)) : [];
    }

    clearPostForm() {
        const inputs = [
            'post-content-input',
            'post-image-url',
            'post-image-prompt',
            'post-scheduled-time'
        ];

        inputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.value = '';
            }
        });

        const imagePreview = document.getElementById('generated-image-preview');
        if (imagePreview) {
            imagePreview.innerHTML = '';
        }
    }

    async loadPosts() {
        try {
            const response = await fetch(`${this.apiBase}/posts?user_id=${this.currentUser}`);
            const data = await response.json();
            
            if (data.posts) {
                this.updatePostsUI(data.posts);
            }
        } catch (error) {
            console.error('Error loading posts:', error);
        }
    }

    updatePostsUI(posts) {
        const postsList = document.getElementById('posts-list');
        if (!postsList) return;

        if (posts.length === 0) {
            postsList.innerHTML = '<div class="text-center py-8 text-gray-500">No posts created yet</div>';
            return;
        }

        postsList.innerHTML = posts.map(post => `
            <div class="border rounded-lg p-4 mb-4">
                <div class="flex justify-between items-start mb-3">
                    <div>
                        <span class="px-2 py-1 text-xs rounded-full ${this.getStatusColor(post.status)}">
                            ${post.status.toUpperCase()}
                        </span>
                        <span class="ml-2 text-sm text-gray-500">
                            ${new Date(post.created_at).toLocaleDateString()}
                        </span>
                    </div>
                    <div class="flex space-x-2">
                        ${post.status === 'draft' ? `
                            <button class="approve-post-btn px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600" 
                                    data-post-id="${post.id}">
                                Approve
                            </button>
                        ` : ''}
                        ${post.status === 'approved' ? `
                            <button class="publish-post-btn px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600" 
                                    data-post-id="${post.id}">
                                Publish Now
                            </button>
                        ` : ''}
                    </div>
                </div>
                
                <div class="mb-3">
                    <p class="text-gray-800">${post.content}</p>
                    ${post.hashtags && post.hashtags.length > 0 ? `
                        <div class="mt-2">
                            ${post.hashtags.map(tag => `<span class="text-blue-500">#${tag}</span>`).join(' ')}
                        </div>
                    ` : ''}
                </div>
                
                ${post.image_url ? `
                    <div class="mb-3">
                        <img src="${post.image_url}" alt="Post image" class="max-w-xs h-auto rounded">
                    </div>
                ` : ''}
                
                ${post.scheduled_at ? `
                    <div class="text-sm text-gray-500">
                        Scheduled for: ${new Date(post.scheduled_at).toLocaleString()}
                    </div>
                ` : ''}
                
                ${post.error_message ? `
                    <div class="text-sm text-red-500 mt-2">
                        Error: ${post.error_message}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    getStatusColor(status) {
        const colors = {
            'draft': 'bg-gray-100 text-gray-800',
            'approved': 'bg-yellow-100 text-yellow-800',
            'scheduled': 'bg-blue-100 text-blue-800',
            'posted': 'bg-green-100 text-green-800',
            'failed': 'bg-red-100 text-red-800'
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    }

    async approvePost(postId) {
        try {
            const response = await fetch(`${this.apiBase}/posts/${postId}/approve`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Post approved successfully!', 'success');
                await this.loadPosts();
            } else {
                throw new Error(data.error || 'Failed to approve post');
            }
        } catch (error) {
            console.error('Error approving post:', error);
            this.showNotification('Failed to approve post: ' + error.message, 'error');
        }
    }

    async publishPost(postId) {
        if (!confirm('Are you sure you want to publish this post now?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/posts/${postId}/publish`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showNotification('Post published successfully!', 'success');
                await this.loadPosts();
            } else {
                throw new Error(data.error || 'Failed to publish post');
            }
        } catch (error) {
            console.error('Error publishing post:', error);
            this.showNotification('Failed to publish post: ' + error.message, 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${this.getNotificationColor(type)}`;
        notification.textContent = message;

        // Add to page
        document.body.appendChild(notification);

        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    getNotificationColor(type) {
        const colors = {
            'success': 'bg-green-500 text-white',
            'error': 'bg-red-500 text-white',
            'warning': 'bg-yellow-500 text-white',
            'info': 'bg-blue-500 text-white'
        };
        return colors[type] || colors.info;
    }

    // Utility method to populate account select dropdown
    populateAccountSelect() {
        const accountSelect = document.getElementById('post-account-select');
        if (!accountSelect) return;

        accountSelect.innerHTML = '<option value="">Select Account</option>' +
            this.connectedAccounts.map(account => 
                `<option value="${account.id}">${account.account_name} (${account.platform})</option>`
            ).join('');
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.socialMediaAutomation = new SocialMediaAutomation();
});

