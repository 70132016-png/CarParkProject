// Global variables
let selectedSpot = null;
let bookingModal, waitlistModal, feedbackModal;
let currentRating = 0;
let allSpots = [];
let currentFilter = 'all';
let searchTerm = '';
let isFirstVisit = !localStorage.getItem('parkease_visited');

// Initialize modals on page load
document.addEventListener('DOMContentLoaded', function() {
    bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));
    waitlistModal = new bootstrap.Modal(document.getElementById('waitlistModal'));
    feedbackModal = new bootstrap.Modal(document.getElementById('feedbackModal'));
    
    // Initialize star rating
    initStarRating();
    
    // Load parking spots
    loadParkingSpots();
    
    // Auto-refresh every 3 seconds
    setInterval(loadParkingSpots, 3000);
    
    // Set minimum arrival time to now
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('arrival_time').min = now.toISOString().slice(0, 16);
    
    // Show tutorial for first-time visitors
    if (isFirstVisit) {
        setTimeout(showTutorial, 1000);
    }
});

// Load and display parking spots
function loadParkingSpots() {
    // Animate refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        const icon = refreshBtn.querySelector('i');
        icon.style.animation = 'spin 1s linear';
        setTimeout(() => {
            icon.style.animation = '';
        }, 1000);
    }
    
    fetch('/api/spots')
        .then(response => response.json())
        .then(data => {
            allSpots = data.spots;
            updateStats(data.stats);
            renderParkingDiagram(filterSpotsList(data.spots));
        })
        .catch(error => {
            console.error('Error loading spots:', error);
        });
}

// Add spin animation for refresh button
const spinStyle = document.createElement('style');
spinStyle.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(spinStyle);

// Filter spots based on search and filter
function filterSpotsList(spots) {
    let filtered = spots;
    
    // Apply status filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(spot => spot.status === currentFilter);
    }
    
    // Apply search term
    if (searchTerm) {
        filtered = filtered.filter(spot => 
            spot.spot_label.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }
    
    // Update filtered count
    if (document.getElementById('filtered-count')) {
        document.getElementById('filtered-count').textContent = `${filtered.length} spots`;
    }
    
    return filtered;
}

// Set filter with animation
function setFilter(filter) {
    currentFilter = filter;
    
    // Update button states with animation
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
            // Add pulse animation
            btn.style.animation = 'none';
            setTimeout(() => {
                btn.style.animation = 'pulse 0.5s ease';
            }, 10);
        }
    });
    
    // Re-render diagram with fade effect
    const diagram = document.getElementById('parking-diagram');
    diagram.style.opacity = '0.5';
    
    setTimeout(() => {
        renderParkingDiagram(filterSpotsList(allSpots));
        diagram.style.opacity = '1';
    }, 200);
}

// Filter spots by search input with highlighting
function filterSpots() {
    searchTerm = document.getElementById('searchSpot').value;
    renderParkingDiagram(filterSpotsList(allSpots));
    
    // Highlight matching spots
    if (searchTerm) {
        setTimeout(() => {
            document.querySelectorAll('.parking-spot').forEach(spot => {
                if (spot.dataset.spot.toLowerCase().includes(searchTerm.toLowerCase())) {
                    spot.style.animation = 'pulse 1s ease-in-out 3';
                }
            });
        }, 100);
    }
}

// Update statistics display with animation
function updateStats(stats) {
    animateCounter('total-spots', stats.total);
    animateCounter('available-spots', stats.available);
    animateCounter('occupied-spots', stats.occupied);
    animateCounter('reserved-spots', stats.reserved);
    
    // Update status text
    const statusText = document.getElementById('status-text');
    if (stats.available > 20) {
        statusText.innerHTML = '<i class="fas fa-check-circle me-2"></i>Plenty of spaces available!';
        statusText.parentElement.className = 'alert alert-success mt-3';
    } else if (stats.available > 10) {
        statusText.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Limited spaces available';
        statusText.parentElement.className = 'alert alert-warning mt-3';
    } else if (stats.available > 0) {
        statusText.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i>Very few spaces left!';
        statusText.parentElement.className = 'alert alert-danger mt-3';
    } else {
        statusText.innerHTML = '<i class="fas fa-times-circle me-2"></i>No spaces available - Join waitlist!';
        statusText.parentElement.className = 'alert alert-danger mt-3';
    }
}

// Animate counter with smooth transition
function animateCounter(elementId, targetValue) {
    const element = document.getElementById(elementId);
    
    // Remove spinner if present
    const spinner = element.querySelector('.spinner-border');
    if (spinner) {
        spinner.remove();
    }
    
    const currentValue = parseInt(element.textContent) || 0;
    
    if (currentValue === targetValue) return;
    
    element.classList.add('updating');
    
    const duration = 500;
    const steps = 20;
    const stepValue = (targetValue - currentValue) / steps;
    const stepDuration = duration / steps;
    let currentStep = 0;
    
    const interval = setInterval(() => {
        currentStep++;
        const newValue = Math.round(currentValue + (stepValue * currentStep));
        element.textContent = newValue;
        
        if (currentStep >= steps) {
            element.textContent = targetValue;
            element.classList.remove('updating');
            clearInterval(interval);
        }
    }, stepDuration);
}

// Render parking diagram with staggered animation
function renderParkingDiagram(spots) {
    const diagram = document.getElementById('parking-diagram');
    
    // Group spots by column (A, B, C)
    const columns = { A: [], B: [], C: [] };
    spots.forEach(spot => {
        const column = spot.spot_label[0];
        if (columns[column]) {
            columns[column].push(spot);
        }
    });
    
    // Sort each column by number
    Object.keys(columns).forEach(col => {
        columns[col].sort((a, b) => {
            const numA = parseInt(a.spot_label.slice(1));
            const numB = parseInt(b.spot_label.slice(1));
            return numA - numB;
        });
    });
    
    // Clear and rebuild diagram
    diagram.innerHTML = '';
    
    let delayIndex = 0;
    
    // Create three columns
    ['A', 'B', 'C'].forEach(col => {
        const columnDiv = document.createElement('div');
        columnDiv.className = 'parking-column';
        
        columns[col].forEach(spot => {
            const spotDiv = document.createElement('div');
            spotDiv.className = `parking-spot ${spot.status}`;
            spotDiv.style.position = 'relative';
            spotDiv.style.animationDelay = `${delayIndex * 0.03}s`;
            delayIndex++;
            
            // Add tooltip
            const tooltip = document.createElement('div');
            tooltip.className = 'spot-tooltip';
            const statusEmoji = spot.status === 'available' ? '✅' : spot.status === 'reserved' ? '🔒' : '🚗';
            tooltip.innerHTML = `${statusEmoji} Spot ${spot.spot_label}<br><small>${spot.status.toUpperCase()}</small>`;
            spotDiv.appendChild(tooltip);
            
            // Add favorite icon
            const favoriteIcon = document.createElement('i');
            favoriteIcon.className = 'fas fa-heart favorite-icon';
            const favorites = JSON.parse(localStorage.getItem('parkease_favorites') || '[]');
            if (favorites.includes(spot.spot_label)) {
                favoriteIcon.classList.add('favorited');
            }
            favoriteIcon.onclick = (e) => {
                e.stopPropagation();
                toggleFavorite(spot.spot_label, favoriteIcon);
            };
            spotDiv.appendChild(favoriteIcon);
            
            // Add spot label
            const labelSpan = document.createElement('span');
            labelSpan.textContent = spot.spot_label;
            spotDiv.appendChild(labelSpan);
            
            spotDiv.dataset.spot = spot.spot_label;
            spotDiv.dataset.status = spot.status;
            
            if (spot.status === 'available') {
                spotDiv.onclick = (e) => {
                    createRipple(e, spotDiv);
                    setTimeout(() => openBookingModal(spot.spot_label), 300);
                };
            }
            
            columnDiv.appendChild(spotDiv);
        });
        
        diagram.appendChild(columnDiv);
    });
}

// Toggle favorite spot
function toggleFavorite(spotLabel, iconElement) {
    iconElement.classList.toggle('favorited');
    
    // Save to localStorage
    let favorites = JSON.parse(localStorage.getItem('parkease_favorites') || '[]');
    const index = favorites.indexOf(spotLabel);
    
    if (index === -1) {
        favorites.push(spotLabel);
        showNotification('Added to Favorites', `Spot ${spotLabel} added to your favorites!`, 'success');
    } else {
        favorites.splice(index, 1);
        showNotification('Removed from Favorites', `Spot ${spotLabel} removed from favorites`, 'info');
    }
    
    localStorage.setItem('parkease_favorites', JSON.stringify(favorites));
}

// Open booking modal
function openBookingModal(spotLabel) {
    selectedSpot = spotLabel;
    document.getElementById('selected-spot').textContent = spotLabel;
    document.getElementById('bookingForm').reset();
    
    // Set default arrival time to current time
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('arrival_time').value = now.toISOString().slice(0, 16);
    
    bookingModal.show();
}

// Confirm booking
function confirmBooking() {
    const form = document.getElementById('bookingForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const bookingData = {
        spot_label: selectedSpot,
        user_name: document.getElementById('user_name').value,
        user_phone: document.getElementById('user_phone').value,
        user_email: document.getElementById('user_email').value,
        car_type: document.getElementById('car_type').value,
        arrival_time: document.getElementById('arrival_time').value,
        duration: document.getElementById('duration').value
    };
    
    fetch('/api/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            bookingModal.hide();
            celebrateBooking();
            showNotification('🎉 Success!', 'Your parking spot has been reserved!', 'success');
            loadParkingSpots();
        } else {
            showNotification('Error', data.message, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error', 'Failed to create booking. Please try again.', 'danger');
        console.error('Booking error:', error);
    });
}

// Show waitlist modal
function showWaitlistModal() {
    document.getElementById('waitlistForm').reset();
    waitlistModal.show();
}

// Join waitlist
function joinWaitlist() {
    const form = document.getElementById('waitlistForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    const waitlistData = {
        user_name: document.getElementById('wl_name').value,
        user_phone: document.getElementById('wl_phone').value,
        user_email: document.getElementById('wl_email').value,
        car_type: document.getElementById('wl_car_type').value
    };
    
    fetch('/api/waitlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(waitlistData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            waitlistModal.hide();
            showNotification('Added to Waitlist', "We'll notify you when a spot becomes available!", 'info');
        } else {
            showNotification('Error', data.message, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error', 'Failed to join waitlist. Please try again.', 'danger');
        console.error('Waitlist error:', error);
    });
}

// Show feedback modal
function showFeedbackModal() {
    document.getElementById('feedbackForm').reset();
    currentRating = 0;
    document.getElementById('fb_rating').value = 0;
    document.querySelectorAll('.star-rating i').forEach(star => {
        star.classList.remove('active');
    });
    feedbackModal.show();
}

// Initialize star rating
function initStarRating() {
    const stars = document.querySelectorAll('.star-rating i');
    stars.forEach(star => {
        star.addEventListener('click', function() {
            currentRating = parseInt(this.dataset.rating);
            document.getElementById('fb_rating').value = currentRating;
            
            stars.forEach(s => {
                const rating = parseInt(s.dataset.rating);
                if (rating <= currentRating) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });
}

// Submit feedback
function submitFeedback() {
    const form = document.getElementById('feedbackForm');
    
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }
    
    if (currentRating === 0) {
        showNotification('Rating Required', 'Please select a star rating', 'warning');
        return;
    }
    
    const feedbackData = {
        user_name: document.getElementById('fb_name').value,
        rating: currentRating,
        comment: document.getElementById('fb_comment').value
    };
    
    fetch('/api/feedback', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            feedbackModal.hide();
            showNotification('Thank You!', 'Your feedback has been submitted!', 'success');
        } else {
            showNotification('Error', data.message, 'danger');
        }
    })
    .catch(error => {
        showNotification('Error', 'Failed to submit feedback. Please try again.', 'danger');
        console.error('Feedback error:', error);
    });
}

// Show notification
function showNotification(title, message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        <strong>${title}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Create ripple effect on click
function createRipple(event, element) {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    
    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
}

// Show confetti celebration
function celebrateBooking() {
    const colors = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6', '#ec4899'];
    const confettiContainer = document.createElement('div');
    confettiContainer.className = 'confetti-container';
    document.body.appendChild(confettiContainer);
    
    for (let i = 0; i < 100; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.background = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.animationDelay = Math.random() * 0.5 + 's';
        confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';
        confettiContainer.appendChild(confetti);
    }
    
    setTimeout(() => confettiContainer.remove(), 4000);
}

// Show tutorial overlay for first-time visitors
function showTutorial() {
    const overlay = document.createElement('div');
    overlay.className = 'tutorial-overlay';
    overlay.innerHTML = `
        <div class="tutorial-box">
            <h2>🚗 Welcome to PARKEASE!</h2>
            <p>Let us show you how easy it is to find and book your perfect parking spot</p>
            <div class="tutorial-steps">
                <div class="tutorial-step">
                    <i class="fas fa-search"></i>
                    <h4>Find</h4>
                    <p>Green spots are available to book</p>
                </div>
                <div class="tutorial-step">
                    <i class="fas fa-mouse-pointer"></i>
                    <h4>Click</h4>
                    <p>Click on any available spot</p>
                </div>
                <div class="tutorial-step">
                    <i class="fas fa-check-circle"></i>
                    <h4>Book</h4>
                    <p>Fill details and confirm!</p>
                </div>
            </div>
            <button class="tutorial-close-btn" onclick="closeTutorial()">
                <i class="fas fa-rocket me-2"></i>Get Started
            </button>
        </div>
    `;
    document.body.appendChild(overlay);
    
    // Save that user has visited
    localStorage.setItem('parkease_visited', 'true');
}

// Close tutorial
function closeTutorial() {
    const overlay = document.querySelector('.tutorial-overlay');
    if (overlay) {
        overlay.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => overlay.remove(), 300);
    }
}

// Reset tutorial (for help button)
function resetTutorial() {
    showTutorial();
}

// Add fadeOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
`;
document.head.appendChild(style);
