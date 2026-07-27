/* ===================================
   SETTINGS PAGE - COMPLETE JAVASCRIPT
   FacTora Settings Functionality
   =================================== */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Settings page loaded');

    // ===== SECTION NAVIGATION =====
    const navItems = document.querySelectorAll('.settings-nav-item');
    const sections = document.querySelectorAll('.settings-section');

    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            
            // Remove active class from all nav items and sections
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked nav item and corresponding section
            this.classList.add('active');
            const targetSection = document.getElementById(`${sectionId}-section`);
            if (targetSection) {
                targetSection.classList.add('active');
                
                // Smooth scroll to top of section
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // ===== PASSWORD VISIBILITY TOGGLE =====
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // ===== PASSWORD STRENGTH METER =====
    const newPasswordInput = document.getElementById('newPassword');
    
    if (newPasswordInput) {
        newPasswordInput.addEventListener('input', function() {
            const password = this.value;
            const strengthBar = document.querySelector('.strength-fill');
            const strengthText = document.querySelector('.strength-text');
            
            if (!strengthBar || !strengthText) return;
            
            let strength = 0;
            let feedback = 'Weak';
            
            // Check password strength
            if (password.length >= 8) strength += 25;
            if (password.length >= 12) strength += 25;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength += 25;
            if (/[0-9]/.test(password)) strength += 15;
            if (/[^a-zA-Z0-9]/.test(password)) strength += 10;
            
            // Update strength bar
            strengthBar.style.width = `${Math.min(strength, 100)}%`;
            
            // Update text
            if (strength < 30) {
                feedback = 'Weak';
                strengthBar.style.background = 'var(--color-error)';
            } else if (strength < 60) {
                feedback = 'Fair';
                strengthBar.style.background = 'var(--color-warning)';
            } else if (strength < 80) {
                feedback = 'Good';
                strengthBar.style.background = 'var(--color-success)';
            } else {
                feedback = 'Strong';
                strengthBar.style.background = 'var(--color-success)';
            }
            
            strengthText.textContent = `Password strength: ${feedback}`;
        });
    }

    // ===== PASSWORD VALIDATION =====
    const updatePasswordBtn = document.querySelector('.btn-primary');
    
    if (updatePasswordBtn) {
        updatePasswordBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const currentPassword = document.getElementById('currentPassword');
            const newPassword = document.getElementById('newPassword');
            const confirmPassword = document.getElementById('confirmPassword');
            
            // Validate inputs
            if (!currentPassword.value) {
                showNotification('Please enter your current password', 'error');
                currentPassword.focus();
                return;
            }
            
            if (!newPassword.value) {
                showNotification('Please enter a new password', 'error');
                newPassword.focus();
                return;
            }
            
            if (newPassword.value.length < 6) {
                showNotification('New password must be at least 6 characters', 'error');
                newPassword.focus();
                return;
            }
            
            if (newPassword.value !== confirmPassword.value) {
                showNotification('Passwords do not match', 'error');
                confirmPassword.focus();
                return;
            }
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
            this.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
                
                showNotification('Password updated successfully!', 'success');
                
                // Clear fields
                currentPassword.value = '';
                newPassword.value = '';
                confirmPassword.value = '';
                
                // Reset strength meter
                const strengthBar = document.querySelector('.strength-fill');
                const strengthText = document.querySelector('.strength-text');
                if (strengthBar) strengthBar.style.width = '0%';
                if (strengthText) strengthText.textContent = 'Password strength';
            }, 1500);
        });
    }

    // ===== DELETE ACCOUNT CONFIRMATION =====
    const deleteAccountBtn = document.getElementById('deleteAccountBtn');
    
    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', function() {
            const confirmDelete = confirm(
                '⚠️ WARNING: This action cannot be undone!\n\n' +
                'Are you sure you want to permanently delete your account?\n\n' +
                'This will remove:\n' +
                '• All your predictions\n' +
                '• All your feedback\n' +
                '• All your personal data\n\n' +
                'Type "DELETE" to confirm.'
            );
            
            if (confirmDelete) {
                const confirmText = prompt('Type "DELETE" to confirm account deletion:');
                
                if (confirmText === 'DELETE') {
                    // Show loading state
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
                    this.disabled = true;
                    
                    // Simulate API call
                    setTimeout(() => {
                        showNotification('Account deleted. Redirecting...', 'success');
                        
                        // Redirect to home page
                        setTimeout(() => {
                            window.location.href = '/';
                        }, 2000);
                    }, 1500);
                } else {
                    showNotification('Account deletion cancelled', 'info');
                }
            }
        });
    }

    // ===== SAVE ALL SETTINGS =====
    const saveAllBtn = document.getElementById('saveAllSettings');
    
    if (saveAllBtn) {
        saveAllBtn.addEventListener('click', function() {
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
            this.disabled = true;
            
            // Collect all settings
            const settings = {
                email: document.getElementById('email')?.value,
                fullName: document.getElementById('fullName')?.value,
                bio: document.getElementById('bio')?.value,
                fontSize: document.getElementById('fontSize')?.value,
                theme: document.querySelector('input[name="theme"]:checked')?.id,
                // Add more settings as needed
            };
            
            console.log('Saving settings:', settings);
            
            // Simulate API call
            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-check"></i> Saved!';
                
                showNotification('All settings saved successfully!', 'success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                }, 2000);
            }, 1500);
        });
    }

    // ===== THEME SELECTION =====
    const themeOptions = document.querySelectorAll('.theme-option');
    
    themeOptions.forEach(option => {
        option.addEventListener('click', function() {
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
                
                // Remove active class from all options
                themeOptions.forEach(opt => opt.classList.remove('active'));
                
                // Add active class to selected option
                this.classList.add('active');
                
                // Apply theme (you can implement actual theme switching here)
                const selectedTheme = radio.id.replace('Theme', '');
                console.log('Selected theme:', selectedTheme);
                
                showNotification(`Theme changed to ${selectedTheme}`, 'info');
            }
        });
    });

    // ===== TOGGLE SWITCHES =====
    const toggleSwitches = document.querySelectorAll('.toggle-switch input[type="checkbox"]');
    
    toggleSwitches.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const settingName = this.closest('.toggle-setting')?.querySelector('h4')?.textContent;
            const status = this.checked ? 'enabled' : 'disabled';
            
            console.log(`${settingName}: ${status}`);
            
            // You can add API calls here to save the setting
        });
    });

    // ===== ENABLE PUSH NOTIFICATIONS =====
    const enablePushBtn = document.getElementById('enablePushBtn');
    
    if (enablePushBtn) {
        enablePushBtn.addEventListener('click', function() {
            if ('Notification' in window) {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        showNotification('Push notifications enabled!', 'success');
                        this.innerHTML = '<i class="fas fa-check"></i> Enabled';
                        this.disabled = true;
                        
                        // Show a test notification
                        new Notification('FacTora', {
                            body: 'You will now receive notifications from FacTora',
                            icon: '/static/images/favicon-32x32.png'
                        });
                    } else if (permission === 'denied') {
                        showNotification('Push notifications blocked. Please enable in browser settings.', 'error');
                    }
                });
            } else {
                showNotification('Push notifications not supported in this browser', 'error');
            }
        });
    }

    // ===== API KEY ACTIONS =====
    const copyApiBtn = document.querySelector('.btn-icon[title="Copy API Key"]');
    const regenerateApiBtn = document.querySelector('.btn-icon[title="Regenerate API Key"]');
    
    if (copyApiBtn) {
        copyApiBtn.addEventListener('click', function() {
            // In production, you'd copy the actual API key
            const dummyKey = 'sk-factora-1234567890abcdef';
            
            navigator.clipboard.writeText(dummyKey).then(() => {
                showNotification('API key copied to clipboard!', 'success');
                
                const icon = this.querySelector('i');
                icon.classList.remove('fa-copy');
                icon.classList.add('fa-check');
                
                setTimeout(() => {
                    icon.classList.remove('fa-check');
                    icon.classList.add('fa-copy');
                }, 2000);
            }).catch(() => {
                showNotification('Failed to copy API key', 'error');
            });
        });
    }
    
    if (regenerateApiBtn) {
        regenerateApiBtn.addEventListener('click', function() {
            const confirm = window.confirm(
                'Are you sure you want to regenerate your API key?\n\n' +
                'Your current API key will stop working immediately.'
            );
            
            if (confirm) {
                const icon = this.querySelector('i');
                icon.classList.add('fa-spin');
                
                setTimeout(() => {
                    icon.classList.remove('fa-spin');
                    showNotification('API key regenerated successfully!', 'success');
                }, 1500);
            }
        });
    }

    // ===== CLEAR DATA ACTIONS =====
    const clearHistoryBtn = document.querySelector('.btn-danger-outline:contains("Clear History")');
    const clearAllBtn = document.querySelector('.btn-danger-outline:contains("Clear All")');
    
    // Clear History
    document.querySelectorAll('.btn-danger-outline').forEach(btn => {
        if (btn.textContent.includes('Clear History')) {
            btn.addEventListener('click', function() {
                const confirm = window.confirm(
                    'Are you sure you want to clear your prediction history?\n\n' +
                    'This action cannot be undone.'
                );
                
                if (confirm) {
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
                    this.disabled = true;
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                        this.disabled = false;
                        showNotification('Prediction history cleared', 'success');
                    }, 1500);
                }
            });
        }
        
        if (btn.textContent.includes('Clear All')) {
            btn.addEventListener('click', function() {
                const confirm = window.confirm(
                    '⚠️ WARNING: This will delete ALL your data!\n\n' +
                    'Are you absolutely sure?'
                );
                
                if (confirm) {
                    const doubleConfirm = window.confirm(
                        'Last chance! This cannot be undone.\n\n' +
                        'Click OK to permanently delete all your data.'
                    );
                    
                    if (doubleConfirm) {
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';
                        this.disabled = true;
                        
                        setTimeout(() => {
                            this.innerHTML = originalText;
                            this.disabled = false;
                            showNotification('All data cleared', 'success');
                        }, 1500);
                    }
                }
            });
        }
    });

    // ===== FORM VALIDATION =====
    const emailInput = document.getElementById('email');
    
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value;
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = 'var(--color-error)';
                showNotification('Please enter a valid email address', 'error');
            } else {
                this.style.borderColor = '';
            }
        });
    }

    // ===== NOTIFICATION SYSTEM =====
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.settings-notification');
        existingNotifications.forEach(notif => notif.remove());
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `settings-notification notification-${type}`;
        
        const icon = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        }[type] || 'fa-info-circle';
        
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
            <button class="notification-close"><i class="fas fa-times"></i></button>
        `;
        
        document.body.appendChild(notification);
        
        // Add styles if not already present
        if (!document.getElementById('notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                .settings-notification {
                    position: fixed;
                    top: 100px;
                    right: 2rem;
                    background: white;
                    padding: 1rem 1.5rem;
                    border-radius: 0.75rem;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    z-index: 10000;
                    animation: slideInRight 0.3s ease;
                    max-width: 400px;
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
                
                .notification-success { border-left: 4px solid #7FA686; }
                .notification-error { border-left: 4px solid #C66B6B; }
                .notification-warning { border-left: 4px solid #D4A574; }
                .notification-info { border-left: 4px solid #B67C62; }
                
                .settings-notification i:first-child {
                    font-size: 1.25rem;
                }
                
                .notification-success i:first-child { color: #7FA686; }
                .notification-error i:first-child { color: #C66B6B; }
                .notification-warning i:first-child { color: #D4A574; }
                .notification-info i:first-child { color: #B67C62; }
                
                .settings-notification span {
                    flex: 1;
                    font-weight: 500;
                    color: #4A4845;
                }
                
                .notification-close {
                    background: none;
                    border: none;
                    color: #706B66;
                    cursor: pointer;
                    padding: 0.25rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .notification-close:hover {
                    color: #4A4845;
                }
                
                @media (max-width: 768px) {
                    .settings-notification {
                        right: 1rem;
                        left: 1rem;
                        max-width: calc(100% - 2rem);
                    }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        });
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 5000);
    }

    // Add slideOut animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    console.log('Settings page initialized successfully');
});
