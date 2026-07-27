/* ===================================
   HELP & SUPPORT PAGE - COMPLETE JAVASCRIPT
   FacTora Help Center Functionality
   =================================== */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Help & Support page loaded');

    // ===== HELP SEARCH FUNCTIONALITY =====
    const helpSearch = document.getElementById('helpSearch');
    
    if (helpSearch) {
        helpSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase().trim();
            
            if (searchTerm.length === 0) {
                // Show all content
                showAllContent();
                return;
            }
            
            // Search through all help cards, FAQ items, and accordion items
            searchContent(searchTerm);
        });
    }

    function searchContent(term) {
        // Search in help cards
        const helpCards = document.querySelectorAll('.help-card');
        let foundResults = false;
        
        helpCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(term)) {
                card.style.display = 'block';
                highlightText(card, term);
                foundResults = true;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Search in FAQ cards
        const faqCards = document.querySelectorAll('.faq-card');
        faqCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(term)) {
                card.style.display = 'block';
                highlightText(card, term);
                foundResults = true;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Search in accordion items
        const accordionItems = document.querySelectorAll('.accordion-item');
        accordionItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(term)) {
                item.style.display = 'block';
                item.classList.add('active'); // Auto-expand matching items
                highlightText(item, term);
                foundResults = true;
            } else {
                item.style.display = 'none';
            }
        });
        
        // Show "no results" message if nothing found
        showNoResultsMessage(!foundResults, term);
    }

    function highlightText(element, term) {
        // This is a simple highlight - you can enhance it further
        // For production, consider using a library like mark.js
    }

    function showAllContent() {
        // Show all help cards
        document.querySelectorAll('.help-card').forEach(card => {
            card.style.display = 'block';
        });
        
        // Show all FAQ cards
        document.querySelectorAll('.faq-card').forEach(card => {
            card.style.display = 'block';
        });
        
        // Show all accordion items and collapse them
        document.querySelectorAll('.accordion-item').forEach(item => {
            item.style.display = 'block';
            item.classList.remove('active');
        });
        
        // Remove no results message
        const noResults = document.querySelector('.no-results-message');
        if (noResults) noResults.remove();
    }

    function showNoResultsMessage(show, term) {
        const existingMessage = document.querySelector('.no-results-message');
        
        if (show) {
            if (!existingMessage) {
                const message = document.createElement('div');
                message.className = 'no-results-message';
                message.innerHTML = `
                    <div style="text-align: center; padding: 3rem; background: white; border-radius: 1rem; margin: 2rem 0;">
                        <i class="fas fa-search" style="font-size: 3rem; color: #B67C62; margin-bottom: 1rem;"></i>
                        <h3 style="color: #4A4845; margin-bottom: 0.5rem;">No results found for "${term}"</h3>
                        <p style="color: #706B66;">Try different keywords or <a href="#contact" style="color: #B67C62;">contact support</a></p>
                    </div>
                `;
                
                const container = document.querySelector('.help-container');
                if (container) {
                    container.appendChild(message);
                }
            }
        } else {
            if (existingMessage) {
                existingMessage.remove();
            }
        }
    }

    // ===== ACCORDION FUNCTIONALITY =====
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const accordionItem = this.parentElement;
            const isActive = accordionItem.classList.contains('active');
            
            // Close all accordion items
            document.querySelectorAll('.accordion-item').forEach(item => {
                item.classList.remove('active');
            });
            
            // Open clicked item if it wasn't active
            if (!isActive) {
                accordionItem.classList.add('active');
            }
        });
    });

    // ===== SMOOTH SCROLL FOR ANCHOR LINKS =====
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Skip if href is just "#"
            if (href === '#') return;
            
            e.preventDefault();
            
            const target = document.querySelector(href);
            if (target) {
                const offset = 100; // Offset for fixed header
                const targetPosition = target.offsetTop - offset;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // ===== CONTACT FORM SUBMISSION =====
    const contactForm = document.getElementById('contactForm');
    
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('contactName').value;
            const email = document.getElementById('contactEmail').value;
            const subject = document.getElementById('contactSubject').value;
            const message = document.getElementById('contactMessage').value;
            
            // Validate form
            if (!name || !email || !subject || !message) {
                showNotification('Please fill in all required fields', 'error');
                return;
            }
            
            // Validate email
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showNotification('Please enter a valid email address', 'error');
                return;
            }
            
            // Get submit button
            const submitBtn = this.querySelector('.btn-submit');
            const originalText = submitBtn.innerHTML;
            
            // Show loading state
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitBtn.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                submitBtn.innerHTML = '<i class="fas fa-check"></i> Sent!';
                
                showNotification('Message sent successfully! We\'ll get back to you soon.', 'success');
                
                // Reset form
                contactForm.reset();
                
                // Reset button after 3 seconds
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }, 2000);
        });
    }

    // ===== LIVE CHAT FUNCTIONALITY =====
    window.openLiveChat = function() {
        showNotification('Live chat will open here. Currently in demo mode.', 'info');
        
        // In production, you would integrate a chat service like:
        // - Intercom
        // - Drift
        // - Zendesk Chat
        // - Custom WebSocket chat
        
        console.log('Live chat opened');
    };

    // ===== QUICK HELP CARD ANALYTICS =====
    const quickHelpCards = document.querySelectorAll('.quick-help-card');
    
    quickHelpCards.forEach(card => {
        card.addEventListener('click', function() {
            const cardTitle = this.querySelector('h3').textContent;
            console.log('Quick help card clicked:', cardTitle);
            
            // In production, send analytics event
            // trackEvent('help_card_click', { card: cardTitle });
        });
    });

    // ===== FAQ CARD ANALYTICS =====
    const faqCards = document.querySelectorAll('.faq-card');
    
    faqCards.forEach(card => {
        card.addEventListener('click', function() {
            const question = this.querySelector('h3').textContent;
            console.log('FAQ viewed:', question);
            
            // Add visual feedback
            this.style.transform = 'scale(0.98)';
            setTimeout(() => {
                this.style.transform = '';
            }, 200);
        });
    });

    // ===== COPY CODE SNIPPETS (if any) =====
    const codeBlocks = document.querySelectorAll('code');
    
    codeBlocks.forEach(code => {
        code.style.cursor = 'pointer';
        code.title = 'Click to copy';
        
        code.addEventListener('click', function() {
            const text = this.textContent;
            
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Code copied to clipboard!', 'success');
                
                // Visual feedback
                const originalBg = this.style.background;
                this.style.background = 'rgba(127, 166, 134, 0.2)';
                
                setTimeout(() => {
                    this.style.background = originalBg;
                }, 500);
            }).catch(() => {
                showNotification('Failed to copy code', 'error');
            });
        });
    });

    // ===== TROUBLESHOOTING CARD INTERACTIONS =====
    const troubleshootingCards = document.querySelectorAll('.troubleshooting-card');
    
    troubleshootingCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateX(5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // ===== HELP SECTION VISIBILITY TRACKING =====
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Track which section is viewed
                const sectionId = entry.target.id;
                console.log('Help section viewed:', sectionId);
            }
        });
    }, observerOptions);
    
    // Observe all help sections
    document.querySelectorAll('.help-section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        sectionObserver.observe(section);
    });

    // ===== KEYBOARD SHORTCUTS =====
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('helpSearch');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('helpSearch');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });

    // ===== PRINT FUNCTIONALITY =====
    window.printHelpPage = function() {
        window.print();
    };

    // ===== NOTIFICATION SYSTEM =====
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.help-notification');
        existingNotifications.forEach(notif => notif.remove());
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `help-notification notification-${type}`;
        
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
        if (!document.getElementById('help-notification-styles')) {
            const style = document.createElement('style');
            style.id = 'help-notification-styles';
            style.textContent = `
                .help-notification {
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
                
                .notification-success { border-left: 4px solid #7FA686; }
                .notification-error { border-left: 4px solid #C66B6B; }
                .notification-warning { border-left: 4px solid #D4A574; }
                .notification-info { border-left: 4px solid #B67C62; }
                
                .help-notification i:first-child {
                    font-size: 1.25rem;
                }
                
                .notification-success i:first-child { color: #7FA686; }
                .notification-error i:first-child { color: #C66B6B; }
                .notification-warning i:first-child { color: #D4A574; }
                .notification-info i:first-child { color: #B67C62; }
                
                .help-notification span {
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
                    .help-notification {
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

    // ===== HELPFUL/NOT HELPFUL FEEDBACK =====
    function addFeedbackButtons() {
        const helpCards = document.querySelectorAll('.help-card, .faq-card');
        
        helpCards.forEach(card => {
            if (!card.querySelector('.feedback-buttons')) {
                const feedbackDiv = document.createElement('div');
                feedbackDiv.className = 'feedback-buttons';
                feedbackDiv.style.cssText = 'margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(182, 124, 98, 0.1);';
                feedbackDiv.innerHTML = `
                    <p style="font-size: 0.875rem; color: #706B66; margin-bottom: 0.5rem;">Was this helpful?</p>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="feedback-btn helpful" style="padding: 0.5rem 1rem; border: 2px solid rgba(182, 124, 98, 0.2); background: white; border-radius: 0.5rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-thumbs-up"></i> Yes
                        </button>
                        <button class="feedback-btn not-helpful" style="padding: 0.5rem 1rem; border: 2px solid rgba(182, 124, 98, 0.2); background: white; border-radius: 0.5rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem;">
                            <i class="fas fa-thumbs-down"></i> No
                        </button>
                    </div>
                `;
                
                card.appendChild(feedbackDiv);
                
                // Add click handlers
                feedbackDiv.querySelectorAll('.feedback-btn').forEach(btn => {
                    btn.addEventListener('click', function() {
                        const isHelpful = this.classList.contains('helpful');
                        const cardTitle = card.querySelector('h3')?.textContent || 'Unknown';
                        
                        console.log(`Feedback: ${isHelpful ? 'Helpful' : 'Not Helpful'} - ${cardTitle}`);
                        
                        // Visual feedback
                        this.style.background = 'rgba(127, 166, 134, 0.15)';
                        this.style.borderColor = '#7FA686';
                        this.disabled = true;
                        
                        showNotification('Thank you for your feedback!', 'success');
                        
                        // Disable other button
                        const otherBtn = feedbackDiv.querySelector(`.feedback-btn:not(.${this.classList[1]})`);
                        if (otherBtn) otherBtn.disabled = true;
                    });
                });
            }
        });
    }

    // Add feedback buttons after a delay
    setTimeout(addFeedbackButtons, 1000);

    console.log('Help & Support page initialized successfully');
    console.log('Keyboard shortcuts: Ctrl/Cmd + K (Search), Esc (Clear search)');
});
