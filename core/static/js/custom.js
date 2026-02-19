function changePage(page_number) {
    let current_url_params = new URLSearchParams(window.location.search)
    current_url_params.set("page", page_number)
    let new_url = window.location.pathname + "?" + current_url_params.toString()
    window.location.href = new_url
}

function formatPriceInToman(element) {
    let rawPrice = parseFloat(element.innerText);
    let formatter = new Intl.NumberFormat('fa-IR');
    let formattedPrice = formatter.format(rawPrice);
    element.innerText = `${formattedPrice} تومان`;
}

document.addEventListener("DOMContentLoaded", function() {
    let priceElements = document.querySelectorAll('.formatted-price');
    priceElements.forEach(element => formatPriceInToman(element));
    
    /**
     * Header Scroll Behavior - Intelligent Hide/Show System
     * 
     * Features:
     * - Hide on scroll down
     * - Show on scroll up
     * - Sticky after scroll threshold
     * - Smooth transform-based animations
     * - Performance optimized with requestAnimationFrame
     */
    
    const header = document.querySelector('.header');
    const contentElement = document.querySelector('#content');
    
    if (header) {
        let lastScrollTop = 0;
        let isScrolling = false;
        let scrollTimeout = null;
        const scrollThreshold = 100; // Threshold for sticky state
        const scrollDelta = 5; // Minimum scroll delta to trigger hide/show
        
        /**
         * Handle scroll events with intelligent hide/show behavior
         */
        function handleScroll() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollDirection = scrollTop > lastScrollTop ? 'down' : 'up';
            const scrollDistance = Math.abs(scrollTop - lastScrollTop);
            
            // Only process if scroll distance is significant
            if (scrollDistance < scrollDelta) {
                lastScrollTop = scrollTop;
                return;
            }
            
            // Sticky state - after threshold
            if (scrollTop > scrollThreshold) {
                if (!header.classList.contains('header--sticky')) {
                    header.classList.add('header--sticky');
                    document.body.classList.add('header-sticky-active');
                    
                    // Calculate header height and add padding to content
                    if (contentElement) {
                        const headerHeight = header.offsetHeight;
                        contentElement.style.paddingTop = headerHeight + 'px';
                    }
                }
                
                // Hide on scroll down, show on scroll up
                if (scrollDirection === 'down' && !header.classList.contains('header--hidden')) {
                    header.classList.add('header--hidden');
                } else if (scrollDirection === 'up' && header.classList.contains('header--hidden')) {
                    header.classList.remove('header--hidden');
                }
            } else {
                // Reset to normal state when at top
                if (header.classList.contains('header--sticky')) {
                    header.classList.remove('header--sticky');
                    header.classList.remove('header--hidden');
                    document.body.classList.remove('header-sticky-active');
                    
                    if (contentElement) {
                        contentElement.style.paddingTop = '0';
                    }
                }
            }
            
            lastScrollTop = scrollTop;
            isScrolling = true;
            
            // Clear existing timeout
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            // Reset scrolling flag after scroll ends
            scrollTimeout = setTimeout(function() {
                isScrolling = false;
            }, 150);
        }
        
        /**
         * Throttled scroll handler using requestAnimationFrame
         */
        let ticking = false;
        window.addEventListener('scroll', function() {
            if (!ticking) {
                window.requestAnimationFrame(function() {
                    handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
        
        // Initial check on page load
        setTimeout(function() {
            handleScroll();
        }, 100);
    }
});