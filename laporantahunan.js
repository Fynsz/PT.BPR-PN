
        // Deteksi perangkat mobile
        function isMobileDevice() {
            return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth <= 768;
        }

        // Script untuk toggle menu mobile
        const toggleButton = document.querySelector('.toggle-button');
        const menu = document.querySelector('.menu');

        if (toggleButton) {
            toggleButton.addEventListener('click', () => {
                menu.classList.toggle('active');
            });
        }

        // Script untuk PDF viewer dengan optimisasi mobile
        function togglePdfView(reportType) {
            const pdfSection = document.getElementById(`pdf-section-${reportType}`);
            const reportCard = document.getElementById(`report-2024-${reportType}`);

            // Sembunyikan semua bagian PDF terlebih dahulu
            document.querySelectorAll('.pdf-section').forEach(section => {
                section.classList.remove('active');
            });

            // Hapus highlight dari semua kartu laporan
            document.querySelectorAll('.report-card').forEach(card => {
                card.classList.remove('highlight');
            });

            // Tambahkan highlight ke kartu laporan yang dipilih
            reportCard.classList.add('highlight');

            // Tampilkan bagian PDF yang dipilih dengan animasi
            setTimeout(() => {
                pdfSection.classList.add('active');
            }, 100);

            // Scroll ke bagian PDF dengan efek smooth
            setTimeout(() => {
                pdfSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }, 150);

            // Efek loading
            showLoadingEffect(reportType);
        }

        function hidePdfView(reportType) {
            const pdfSection = document.getElementById(`pdf-section-${reportType}`);
            const reportCard = document.getElementById(`report-2024-${reportType}`);

            // Sembunyikan bagian PDF
            pdfSection.classList.remove('active');

            // Hapus highlight dari kartu laporan
            setTimeout(() => {
                reportCard.classList.remove('highlight');
            }, 300);

            // Scroll kembali ke laporan dengan efek smooth
            reportCard.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        }

        // Fungsi untuk tampilan fullscreen PDF
        function openFullscreen(elementId) {
            const element = document.getElementById(elementId);

            if (element.requestFullscreen) {
                element.requestFullscreen();
            } else if (element.webkitRequestFullscreen) { /* Safari */
                element.webkitRequestFullscreen();
            } else if (element.msRequestFullscreen) { /* IE11 */
                element.msRequestFullscreen();
            }
        }

        // Efek loading sebelum menampilkan PDF
        function showLoadingEffect(reportType) {
            const pdfContainer = document.querySelector(`#pdf-section-${reportType} .pdf-container`);

            // Tambahkan class loading
            pdfContainer.classList.add('loading');

            // Hapus class loading setelah PDF dimuat
            setTimeout(() => {
                pdfContainer.classList.remove('loading');
            }, 2000);
        }

        // Inisialisasi saat halaman dimuat
        document.addEventListener('DOMContentLoaded', () => {
            // Tampilkan notifikasi mobile jika diperlukan
            if (isMobileDevice()) {
                const mobileNotice = document.getElementById('mobileNotice');
                if (mobileNotice) {
                    mobileNotice.classList.add('show');
                }
            }

            // Tambahkan event listener untuk animasi hover pada kartu laporan
            const reportCards = document.querySelectorAll('.report-card');

            reportCards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    if (!isMobileDevice()) {
                        card.style.transform = 'translateY(-5px)';
                        card.style.boxShadow = '0 12px 16px rgba(0, 0, 0, 0.15)';
                    }
                });

                card.addEventListener('mouseleave', () => {
                    if (!card.classList.contains('highlight') && !isMobileDevice()) {
                        card.style.transform = 'translateY(0)';
                        card.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
                    }
                });
            });

            // Tambahkan event listener untuk resize window
            window.addEventListener('resize', () => {
                // Update mobile notice visibility berdasarkan ukuran layar
                const mobileNotice = document.getElementById('mobileNotice');
                if (mobileNotice) {
                    if (isMobileDevice()) {
                        mobileNotice.classList.add('show');
                    } else {
                        mobileNotice.classList.remove('show');
                    }
                }
            });

            // Preload iframe untuk performa yang lebih baik
            const iframes = document.querySelectorAll('.pdf-viewer');
            iframes.forEach(iframe => {
                iframe.addEventListener('load', () => {
                    console.log('PDF loaded successfully');
                });

                iframe.addEventListener('error', () => {
                    console.log('Error loading PDF, fallback to download link');
                });
            });
        });

        // Fungsi untuk membuka PDF dalam tab baru (fallback)
        function openPdfInNewTab(url) {
            window.open(url, '_blank');
        }

        // Error handling untuk iframe
        window.addEventListener('message', function (event) {
            if (event.data === 'pdf-load-error') {
                console.log('PDF viewer encountered an error');
                // Bisa tambahkan fallback logic di sini
            }
        });

        // Smooth scroll untuk navigasi
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Touch events untuk mobile
        if (isMobileDevice()) {
            let touchStartY = 0;
            let touchEndY = 0;

            document.addEventListener('touchstart', function (event) {
                touchStartY = event.changedTouches[0].screenY;
            });

            document.addEventListener('touchend', function (event) {
                touchEndY = event.changedTouches[0].screenY;
                // Bisa tambahkan gesture handling di sini jika diperlukan
            });
        }
