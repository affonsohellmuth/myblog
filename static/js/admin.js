// static/js/admin.js

document.addEventListener('DOMContentLoaded', function() {
    // Check if we have a token before loading admin content
    const token = localStorage.getItem('access_token');
    
    if (!token) {
        // No token found, redirect to login
        window.location.href = '/admin/login';
        return;
    }
    
    // Add token to all requests as Authorization header
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Don't add auth header to the login request
        if (url.includes('/token')) {
            return originalFetch(url, options);
        }
        
        // Create headers if they don't exist
        options.headers = options.headers || {};
        
        // Add the Authorization header with the token
        options.headers['Authorization'] = `Bearer ${token}`;
        
        return originalFetch(url, options);
    };
    
    // Function to check if token is valid
    async function validateToken() {
        try {
            const response = await fetch('/api/admin/validate-token', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                // Token invalid, redirect to login
                localStorage.removeItem('access_token');
                window.location.href = '/admin/login';
                return false;
            }
            
            const userData = await response.json();
            displayUserInfo(userData);
            return true;
        } catch (error) {
            console.error('Token validation error:', error);
            window.location.href = '/admin/login';
            return false;
        }
    }
    
    // Display user info in the header
    function displayUserInfo(user) {
        const userInfoEl = document.querySelector('.user-info span');
        if (userInfoEl && user) {
            userInfoEl.textContent = `Usuário: ${user.username}`;
        }
    }
    
    // For admin-specific AJAX requests
    async function fetchAdminData(url, options = {}) {
        // Always include the auth token in admin requests
        const headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };
        
        try {
            const response = await fetch(url, {
                ...options,
                headers
            });
            
            if (response.status === 401) {
                // Token expired or invalid
                localStorage.removeItem('access_token');
                window.location.href = '/admin/login';
                return null;
            }
            
            return response;
        } catch (error) {
            console.error('Request failed:', error);
            return null;
        }
    }
    
    // Make the function available globally
    window.fetchAdminData = fetchAdminData;
    
    // Load posts for the admin dashboard
    async function loadPosts() {
        const postsContainer = document.getElementById('posts-list');
        if (!postsContainer) return;
        
        postsContainer.innerHTML = '<p class="loading">Loading posts...</p>';
        
        try {
            const response = await fetchAdminData('/api/admin/posts');
            if (!response || !response.ok) {
                postsContainer.innerHTML = '<p class="error">Failed to load posts</p>';
                return;
            }
            
            const posts = await response.json();
            
            if (posts.length === 0) {
                postsContainer.innerHTML = '<p>No posts found. Create your first post!</p>';
                return;
            }
            
            const postsList = posts.map(post => `
                <div class="list-item">
                    <div class="list-item-info">
                        <h3 class="list-item-title"><a href="/post/${post.id}" target="_blank">${post.title}</a></h3>
                        <div class="post-meta">
                            <span>Last updated: ${new Date(post.updated_at).toLocaleDateString()}</span>
                            <span>${post.is_published ? '<span class="badge success">Published</span>' : '<span class="badge warning">Draft</span>'}</span>
                        </div>
                    </div>
                    <div class="list-item-actions">
                        <button class="btn btn-secondary edit-post" data-id="${post.id}">Edit</button>
                        <button class="btn btn-danger delete-post" data-id="${post.id}">Delete</button>
                    </div>
                </div>
            `).join('');
            
            postsContainer.innerHTML = postsList;
            
            // Add event listeners to edit and delete buttons
            document.querySelectorAll('.edit-post').forEach(btn => {
                btn.addEventListener('click', () => editPost(btn.dataset.id));
            });
            
            document.querySelectorAll('.delete-post').forEach(btn => {
                btn.addEventListener('click', () => deletePost(btn.dataset.id));
            });
            
        } catch (error) {
            console.error('Error loading posts:', error);
            postsContainer.innerHTML = '<p class="error">An error occurred while loading posts</p>';
        }
    }
    
    // Load drafts
    async function loadDrafts() {
        const draftsContainer = document.getElementById('drafts-list');
        if (!draftsContainer) return;
        
        draftsContainer.innerHTML = '<p class="loading">Loading drafts...</p>';
        
        try {
            const response = await fetchAdminData('/api/admin/drafts');
            if (!response || !response.ok) {
                draftsContainer.innerHTML = '<p class="error">Failed to load drafts</p>';
                return;
            }
            
            const drafts = await response.json();
            
            if (drafts.length === 0) {
                draftsContainer.innerHTML = '<p>No drafts found.</p>';
                return;
            }
            
            const draftsList = drafts.map(draft => `
                <div class="list-item">
                    <div class="list-item-info">
                        <h3 class="list-item-title">${draft.title}</h3>
                        <div class="post-meta">
                            <span>Last updated: ${new Date(draft.updated_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="list-item-actions">
                        <button class="btn btn-secondary edit-post" data-id="${draft.id}">Edit</button>
                        <button class="btn btn-primary publish-post" data-id="${draft.id}">Publish</button>
                        <button class="btn btn-danger delete-post" data-id="${draft.id}">Delete</button>
                    </div>
                </div>
            `).join('');
            
            draftsContainer.innerHTML = draftsList;
            
            // Add event listeners to edit, publish and delete buttons
            document.querySelectorAll('.edit-post').forEach(btn => {
                btn.addEventListener('click', () => editPost(btn.dataset.id));
            });
            
            document.querySelectorAll('.publish-post').forEach(btn => {
                btn.addEventListener('click', () => publishPost(btn.dataset.id));
            });
            
            document.querySelectorAll('.delete-post').forEach(btn => {
                btn.addEventListener('click', () => deletePost(btn.dataset.id));
            });
            
        } catch (error) {
            console.error('Error loading drafts:', error);
            draftsContainer.innerHTML = '<p class="error">An error occurred while loading drafts</p>';
        }
    }
    
    // Handle sidebar navigation
    function setupNavigation() {
        const navLinks = document.querySelectorAll('.sidebar nav a');
        
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all links and sections
                navLinks.forEach(l => l.classList.remove('active'));
                document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
                
                // Add active class to clicked link
                this.classList.add('active');
                
                // Show corresponding section
                const sectionId = this.dataset.section;
                document.getElementById(sectionId).classList.add('active');
                
                // Load content if needed
                if (sectionId === 'posts') {
                    loadPosts();
                } else if (sectionId === 'drafts') {
                    loadDrafts();
                }
            });
        });
    }
    
    // Function to edit a post
    function editPost(postId) {
        // Redirect to edit page with token in URL
        const token = localStorage.getItem('access_token');
        window.location.href = `/admin/edit-post/${postId}`;
    }
    
    // Function to publish a draft
    async function publishPost(postId) {
        try {
            const response = await fetchAdminData(`/api/admin/posts/${postId}`, {
                method: 'PUT',
                body: JSON.stringify({
                    is_published: true
                })
            });
            
            if (response && response.ok) {
                // Reload drafts list
                loadDrafts();
                // Also reload posts since we have a new published post
                loadPosts();
            } else {
                alert('Failed to publish post. Please try again.');
            }
        } catch (error) {
            console.error('Error publishing post:', error);
            alert('An error occurred while publishing the post.');
        }
    }
    
    // Function to delete a post
    async function deletePost(postId) {
        if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetchAdminData(`/api/admin/posts/${postId}`, {
                method: 'DELETE'
            });
            
            if (response && response.ok) {
                // Reload both lists to ensure they're up to date
                loadPosts();
                loadDrafts();
            } else {
                alert('Failed to delete post. Please try again.');
            }
        } catch (error) {
            console.error('Error deleting post:', error);
            alert('An error occurred while deleting the post.');
        }
    }
    
    // Handle logout
    function setupLogout() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function() {
                localStorage.removeItem('access_token');
                window.location.href = '/admin/login';
            });
        }
    }
    
    // Handle new post form submission
    function setupNewPostForm() {
        const postForm = document.getElementById('post-form');
        if (postForm) {
            postForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const postData = {
                    title: document.getElementById('post-title').value,
                    content: document.getElementById('post-content').value,
                    is_published: document.getElementById('publish').checked
                };
                
                try {
                    const response = await fetchAdminData('/api/admin/posts', {
                        method: 'POST',
                        body: JSON.stringify(postData)
                    });
                    
                    if (response && response.ok) {
                        // Clear form
                        this.reset();
                        
                        // Show success message
                        alert('Post created successfully!');
                        
                        // Navigate to posts section
                        document.querySelector('.sidebar nav a[data-section="posts"]').click();
                    } else {
                        const error = await response.json();
                        alert(`Failed to create post: ${error.detail || 'Unknown error'}`);
                    }
                } catch (error) {
                    console.error('Error creating post:', error);
                    alert('An error occurred while creating the post.');
                }
            });
        }
    }
    
    // Initialize admin panel
    async function initAdminPanel() {
        const isValid = await validateToken();
        if (!isValid) return;
        
        setupNavigation();
        setupLogout();
        setupNewPostForm();
        loadPosts(); // Load posts initially
    }
    
    // Start initialization
    initAdminPanel();
});