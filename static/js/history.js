/* ===================================
   HISTORY PAGE JAVASCRIPT
   FacTora - Interactive Functions
   =================================== */

// Apply Filter
function applyFilter() {
    const filterType = document.getElementById('filterType').value;
    const searchQuery = new URLSearchParams(window.location.search).get('search') || '';
    const sortBy = document.getElementById('sortBy').value;
    const perPage = document.getElementById('perPage').value;
    
    const url = new URL(window.location.href);
    url.searchParams.set('filter_type', filterType);
    url.searchParams.set('search', searchQuery);
    url.searchParams.set('sort_by', sortBy);
    url.searchParams.set('per_page', perPage);
    url.searchParams.set('page', '1'); // Reset to first page
    
    window.location.href = url.toString();
}

// Apply Sort
function applySort() {
    const sortBy = document.getElementById('sortBy').value;
    const searchQuery = new URLSearchParams(window.location.search).get('search') || '';
    const filterType = document.getElementById('filterType').value;
    const perPage = document.getElementById('perPage').value;
    
    const url = new URL(window.location.href);
    url.searchParams.set('sort_by', sortBy);
    url.searchParams.set('search', searchQuery);
    url.searchParams.set('filter_type', filterType);
    url.searchParams.set('per_page', perPage);
    url.searchParams.set('page', '1'); // Reset to first page
    
    window.location.href = url.toString();
}

// Change Per Page
function changePerPage() {
    const perPage = document.getElementById('perPage').value;
    const searchQuery = new URLSearchParams(window.location.search).get('search') || '';
    const filterType = document.getElementById('filterType').value;
    const sortBy = document.getElementById('sortBy').value;
    
    const url = new URL(window.location.href);
    url.searchParams.set('per_page', perPage);
    url.searchParams.set('search', searchQuery);
    url.searchParams.set('filter_type', filterType);
    url.searchParams.set('sort_by', sortBy);
    url.searchParams.set('page', '1'); // Reset to first page
    
    window.location.href = url.toString();
}

// Export History as CSV
function exportHistory() {
    window.location.href = '/export/history';
}

// View Prediction Details
async function viewDetails(predictionId) {
    const modal = document.getElementById('detailsModal');
    const modalBody = document.getElementById('modalBody');
    
    // Show loading state
    modalBody.innerHTML = `
        <div class="modal-loading">
            <div class="spinner"></div>
            <p>Loading details...</p>
        </div>
    `;
    modal.style.display = 'block';
    
    try {
        const response = await fetch(`/api/prediction/${predictionId}`);
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Display prediction details
        const isReal = data.prediction.toUpperCase() === 'REAL';
        const confidenceClass = data.confidence >= 80 ? 'high' : data.confidence >= 60 ? 'medium' : 'low';
        
        modalBody.innerHTML = `
            <div class="modal-details">
                <div class="modal-header">
                    <div class="modal-result ${isReal ? 'real' : 'fake'}">
                        <i class="fas fa-${isReal ? 'check-circle' : 'times-circle'}"></i>
                        <span>${data.prediction}</span>
                    </div>
                    <div class="modal-confidence ${confidenceClass}">
                        <i class="fas fa-chart-line"></i>
                        ${data.confidence.toFixed(1)}% Confidence
                    </div>
                </div>
                
                <div class="modal-section">
                    <h4><i class="fas fa-newspaper"></i> Headline</h4>
                    <p class="modal-headline">${data.headline}</p>
                </div>
                
                <div class="modal-section">
                    <h4><i class="fas fa-info-circle"></i> Analysis Details</h4>
                    <div class="details-grid">
                        <div class="detail-item">
                            <span class="detail-label">Prediction:</span>
                            <span class="detail-value">${data.prediction}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Confidence:</span>
                            <span class="detail-value">${data.confidence.toFixed(1)}%</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Timestamp:</span>
                            <span class="detail-value">${data.timestamp}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Source:</span>
                            <span class="detail-value">${data.source || 'User Input'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="modal-section">
                    <h4><i class="fas fa-chart-bar"></i> Confidence Breakdown</h4>
                    <div class="confidence-bar-modal">
                        <div class="confidence-fill ${isReal ? 'real' : 'fake'}" style="width: ${data.confidence}%"></div>
                    </div>
                    <div class="confidence-labels">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                    </div>
                </div>
                
                ${data.analysis ? `
                <div class="modal-section">
                    <h4><i class="fas fa-brain"></i> AI Analysis</h4>
                    <p class="modal-analysis">${data.analysis}</p>
                </div>
                ` : ''}
                
                <div class="modal-actions">
                    <button class="modal-btn secondary" onclick="closeModal()">
                        <i class="fas fa-times"></i> Close
                    </button>
                    <button class="modal-btn primary" onclick="reanalyze('${data.headline.replace(/'/g, "\\'")}')">
                        <i class="fas fa-redo"></i> Re-analyze
                    </button>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading prediction details:', error);
        modalBody.innerHTML = `
            <div class="modal-error">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>Error Loading Details</h4>
                <p>${error.message}</p>
                <button class="modal-btn secondary" onclick="closeModal()">Close</button>
            </div>
        `;
    }
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('detailsModal');
    modal.style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('detailsModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Re-analyze Headline
function reanalyze(headline) {
    // Store headline in sessionStorage
    sessionStorage.setItem('reanalyze_headline', headline);
    
    // Redirect to home page
    window.location.href = '/';
}

// Check if there's a headline to reanalyze on home page
document.addEventListener('DOMContentLoaded', function() {
    const headlineToReanalyze = sessionStorage.getItem('reanalyze_headline');
    if (headlineToReanalyze && document.getElementById('headline')) {
        document.getElementById('headline').value = headlineToReanalyze;
        sessionStorage.removeItem('reanalyze_headline');
        
        // Scroll to form
        document.getElementById('headline').scrollIntoView({ behavior: 'smooth', block: 'center' });
        document.getElementById('headline').focus();
    }
});

// Delete Prediction
async function deletePrediction(predictionId) {
    if (!confirm('Are you sure you want to delete this prediction? This action cannot be undone.')) {
        return;
    }
    
    const card = document.querySelector(`[data-prediction-id="${predictionId}"]`);
    
    try {
        const response = await fetch(`/api/prediction/${predictionId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Animate card removal
            card.style.opacity = '0';
            card.style.transform = 'scale(0.9)';
            
            setTimeout(() => {
                card.remove();
                
                // Check if there are no more cards
                const remainingCards = document.querySelectorAll('.prediction-card').length;
                if (remainingCards === 0) {
                    location.reload(); // Reload to show empty state
                }
            }, 300);
            
            // Show success message
            showNotification('Prediction deleted successfully', 'success');
        } else {
            throw new Error(data.error || 'Failed to delete prediction');
        }
    } catch (error) {
        console.error('Error deleting prediction:', error);
        showNotification('Error deleting prediction: ' + error.message, 'error');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Close modal with Escape key
    if (event.key === 'Escape') {
        closeModal();
    }
    
    // Focus search with Ctrl+K or Cmd+K
    if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
});

// Add loading animation to buttons
document.addEventListener('DOMContentLoaded', function() {
    const actionButtons = document.querySelectorAll('.action-btn');
    
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.classList.contains('delete')) {
                this.style.opacity = '0.7';
                this.style.pointerEvents = 'none';
                
                setTimeout(() => {
                    this.style.opacity = '1';
                    this.style.pointerEvents = 'auto';
                }, 1000);
            }
        });
    });
});

// Smooth scroll to top when pagination changes
window.addEventListener('load', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const page = urlParams.get('page');
    
    if (page && page !== '1') {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
});

// Auto-save scroll position
window.addEventListener('scroll', function() {
    sessionStorage.setItem('historyScrollPosition', window.scrollY);
});

// Restore scroll position
window.addEventListener('load', function() {
    const scrollPosition = sessionStorage.getItem('historyScrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
    }
});

// Clear scroll position when leaving page
window.addEventListener('beforeunload', function() {
    const currentPage = new URLSearchParams(window.location.search).get('page') || '1';
    if (currentPage === '1') {
        sessionStorage.removeItem('historyScrollPosition');
    }
});

console.log('History.js loaded successfully');
