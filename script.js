// Menu Bar Tab Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get all tabs and content containers
    const tabs = document.querySelectorAll('.toggle-button');
// Toggle menu for mobile view
    document.querySelector('.toggle-button').addEventListener('click', function () {
        document.querySelector('.menu').classList.toggle('active');
    });
    // Add click event to each tab
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Get the tab's data attribute
            const tabId = this.getAttribute('data-tab');
            
            // Hide all content sections
            const allContent = document.querySelectorAll('.menucontent-items');
            allContent.forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the corresponding content section
            const activeContent = document.getElementById(`${tabId}-content`);
            if (activeContent) {
                activeContent.style.display = 'grid';
                
                // Optional: Add a fade-in animation
                activeContent.style.opacity = '0';
                setTimeout(() => {
                    activeContent.style.transition = 'opacity 0.3s ease';
                    activeContent.style.opacity = '1';
                }, 50);
            }
        });
    });
    
    // Optional: Add hover animation for cards
    const cards = document.querySelectorAll('.menucontent-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.12)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.08)';
        });
    });
});
// Menu Bar Tab Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get all tabs and content containers
    const tabs = document.querySelectorAll('.menucontent-tab');
    
    // Add click event to each tab
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Get the tab's data attribute
            const tabId = this.getAttribute('data-tab');
            
            // Hide all content sections
            const allContent = document.querySelectorAll('.menucontent-items');
            allContent.forEach(content => {
                content.style.display = 'none';
            });
            
            // Show the corresponding content section
            const activeContent = document.getElementById(`${tabId}-content`);
            if (activeContent) {
                activeContent.style.display = 'grid';
                
                // Optional: Add a fade-in animation
                activeContent.style.opacity = '0';
                setTimeout(() => {
                    activeContent.style.transition = 'opacity 0.3s ease';
                    activeContent.style.opacity = '1';
                }, 50);
            }
        });
    });
    
    // Optional: Add hover animation for cards
    const cards = document.querySelectorAll('.menucontent-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.12)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.08)';
        });
    });
});

