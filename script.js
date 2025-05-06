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

//kirim email 
 document.getElementById('contactForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Mengambil nilai dari form
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const subject = document.getElementById('subject').value;
            const message = document.getElementById('message').value;
            
            // Dalam implementasi nyata, Anda akan menggunakan layanan email seperti EmailJS, 
            // FormSubmit, atau API backend khusus
            
            // Simulasi pengiriman email (dalam produksi, ganti dengan kode pengiriman email yang sebenarnya)
            // Berikut adalah contoh kode yang akan mengirim ke bpr_pn@yahoo.com
            
            console.log("Mengirim email ke: bpr_pn@yahoo.com");
            console.log("Dari: " + fullName + " (" + email + ")");
            console.log("Subjek: " + subject);
            console.log("Pesan: " + message);
            
            // Tampilkan alert "Terkirim"
            const successAlert = document.getElementById('successAlert');
            successAlert.style.display = 'block';
            
            // Reset formulir
            this.reset();
            
            // Sembunyikan alert setelah 5 detik
            setTimeout(function() {
                successAlert.style.display = 'none';
            }, 5000);
            
            // Untuk implementasi nyata dengan EmailJS (memerlukan akun EmailJS):
            /*
            emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', {
                to_email: 'bpr_pn@yahoo.com',
                from_name: fullName,
                from_email: email,
                subject: subject,
                message: message
            })
            .then(function() {
                document.getElementById('successAlert').style.display = 'block';
                document.getElementById('contactForm').reset();
                setTimeout(function() {
                    document.getElementById('successAlert').style.display = 'none';
                }, 5000);
            }, function(error) {
                console.error('Gagal mengirim email', error);
                alert('Gagal mengirim pesan. Silakan coba lagi.');
            });
            */
        });
