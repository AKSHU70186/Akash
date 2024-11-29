// Navigation scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
        navbar.style.backdropFilter = 'blur(5px)';
    } else {
        navbar.style.backgroundColor = 'white';
        navbar.style.backdropFilter = 'none';
    }
});

// Dashboard tabs functionality
const tabs = document.querySelectorAll('.tab');
const dashboardContent = document.querySelector('.dashboard-content');

const dashboardData = {
    'Actors': `
        <div class="actors-grid">
            <div class="actor-card">
                <h4>Web Scraper</h4>
                <p>Last run: 2 hours ago</p>
                <div class="actor-stats">
                    <span>Success rate: 98%</span>
                    <span>Runs: 1,234</span>
                </div>
            </div>
            <!-- Add more actor cards as needed -->
        </div>
    `,
    'Runs': `
        <div class="runs-list">
            <div class="run-item">
                <span class="status success">Success</span>
                <span class="timestamp">Today, 14:30</span>
                <span class="duration">Duration: 5m 23s</span>
            </div>
            <!-- Add more run items as needed -->
        </div>
    `,
    'Storage': `
        <div class="storage-overview">
            <div class="storage-stats">
                <h4>Total Storage Used</h4>
                <p>234.5 GB / 500 GB</p>
                <div class="progress-bar">
                    <div class="progress" style="width: 47%"></div>
                </div>
            </div>
        </div>
    `
};

tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        // Add active class to clicked tab
        tab.classList.add('active');
        // Update dashboard content
        dashboardContent.innerHTML = dashboardData[tab.textContent];
    });
});

// Initialize with first tab content
document.querySelector('.tab.active').click();

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add animation on scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.feature-card, .dashboard-container');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            element.classList.add('animate');
        }
    });
}

window.addEventListener('scroll', animateOnScroll);

// Add smooth reveal animations
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth reveal animations
    const revealElements = document.querySelectorAll('.feature-card, .hero-content, .dashboard-container');
    
    const revealOnScroll = () => {
        revealElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementBottom = element.getBoundingClientRect().bottom;
            
            if (elementTop < window.innerHeight - 100 && elementBottom > 0) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
    };

    // Initial styles for animation
    revealElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'all 0.6s ease-out';
    });

    // Listen for scroll
    window.addEventListener('scroll', revealOnScroll);
    // Initial check
    revealOnScroll();
}); 