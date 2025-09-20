document.addEventListener('DOMContentLoaded', function() {
    // Helper function to clear all validation errors
    function clearAllErrors() {
        const errorFields = document.querySelectorAll('.error');
        errorFields.forEach(field => {
            field.classList.remove('error');
        });
        
        const errorGroups = document.querySelectorAll('.form-group.error, .form-group.success');
        errorGroups.forEach(group => {
            group.classList.remove('error', 'success');
        });
        
        const errorMessages = document.querySelectorAll('.error-message');
        errorMessages.forEach(message => {
            message.textContent = '';
        });
    }

    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            console.log('Tab clicked:', targetTab); // Debug log
            console.log('Current button:', this);
            
            // Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Hide all tab contents
            tabContents.forEach(content => {
                content.classList.add('hidden');
                console.log('Hiding tab:', content.id); // Debug log
                if (content.id === 'phone-tab') {
                    console.log('Phone tab hidden.');
                }
            });
            
            // Show target tab content
            const targetElement = document.getElementById(targetTab + '-tab');
            if (targetElement) {
                targetElement.classList.remove('hidden');
                console.log('Showing tab:', targetElement.id); // Debug log
                if (targetElement.id === 'phone-tab') {
                    console.log('Phone tab shown.');
                }
            } else {
                console.error('Target tab not found:', targetTab + '-tab');
            }
            
            // Clear any existing validation errors
            clearAllErrors();
        });
    });

    // Password visibility toggle
    const togglePasswordButtons = document.querySelectorAll('.toggle-password');
    togglePasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this;
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            }
        });
    });

    // OTP generation and timer
    let otpTimer = null;
    let timeLeft = 120; // 2 minutes in seconds
    
    const generateOtpButton = document.getElementById('generate-otp');
    const phoneInput = document.getElementById('login-phone');
    const otpGroup = document.querySelector('.otp-group');
    const otpSubmitButton = document.querySelector('.otp-submit');
    const timerElement = document.getElementById('timer');
    
    generateOtpButton.addEventListener('click', function() {
        const phone = phoneInput.value.trim();
        
        if (!validatePhone(phone)) {
            showError(phoneInput, 'Please enter a valid phone number');
            return;
        }
        
        // Generate OTP (in real app, this would be sent to server)
        const otp = generateOTP();
        console.log('Generated OTP:', otp); // For testing purposes
        
        // Show OTP field
        otpGroup.classList.remove('hidden');
        otpSubmitButton.classList.remove('hidden');
        
        // Disable generate button and start timer
        this.disabled = true;
        this.textContent = 'OTP Sent';
        this.classList.add('loading');
        
        // Start timer
        startTimer();
        
        // Show success message
        showSuccess(phoneInput, 'OTP sent successfully');
    });
    
    function generateOTP() {
        return Math.floor(100000 + Math.random() * 900000).toString();
    }
    
    function startTimer() {
        timeLeft = 120;
        updateTimerDisplay();
        
        otpTimer = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();
            
            if (timeLeft <= 0) {
                clearInterval(otpTimer);
                generateOtpButton.disabled = false;
                generateOtpButton.textContent = 'Resend OTP';
                generateOtpButton.classList.remove('loading');
            }
        }, 1000);
    }
    
    function updateTimerDisplay() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    // Form validation
    const kinderIdForm = document.getElementById('kinder-id-form');
    const phoneForm = document.getElementById('phone-form');
    
    // Kinder ID form validation
    kinderIdForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const kinderId = document.getElementById('kinder-id').value.trim();
        const password = document.getElementById('login-password').value;
        
        let isValid = true;
        
        // Clear previous errors
        clearAllErrors();
        
        // Validate Kinder ID
        if (!kinderId) {
            showError(document.getElementById('kinder-id'), 'Kinder ID is required');
            isValid = false;
        } else if (kinderId.length < 3) {
            showError(document.getElementById('kinder-id'), 'Kinder ID must be at least 3 characters');
            isValid = false;
        }
        
        // Validate password
        if (!password) {
            showError(document.getElementById('login-password'), 'Password is required');
            isValid = false;
        } else if (password.length < 6) {
            showError(document.getElementById('login-password'), 'Password must be at least 6 characters');
            isValid = false;
        }
        
        if (isValid) {
            // Simulate login process
            simulateLogin();
        }
    });
    
    // Phone form validation
    phoneForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const phone = document.getElementById('login-phone').value.trim();
        const otp = document.getElementById('otp').value.trim();
        
        let isValid = true;
        
        // Clear previous errors
        clearAllErrors();
        
        // Validate phone
        if (!phone) {
            showError(document.getElementById('login-phone'), 'Phone number is required');
            isValid = false;
        } else if (!validatePhone(phone)) {
            showError(document.getElementById('login-phone'), 'Please enter a valid phone number');
            isValid = false;
        }
        
        // Validate OTP
        if (!otp) {
            showError(document.getElementById('otp'), 'OTP is required');
            isValid = false;
        } else if (!validateOTP(otp)) {
            showError(document.getElementById('otp'), 'Please enter a valid 6-digit OTP');
            isValid = false;
        }
        
        if (isValid) {
            // Simulate login process
            simulateLogin();
        }
    });

    // Real-time validation
    const inputs = document.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            // Clear error on input
            if (this.classList.contains('error')) {
                clearError(this);
            }
        });
    });

    // Validation functions
    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.getAttribute('id');
        
        switch(fieldName) {
            case 'kinder-id':
                if (!value) {
                    showError(field, 'Kinder ID is required');
                } else if (value.length < 3) {
                    showError(field, 'Kinder ID must be at least 3 characters');
                } else {
                    showSuccess(field, '');
                }
                break;
                
            case 'login-password':
                if (!value) {
                    showError(field, 'Password is required');
                } else if (value.length < 6) {
                    showError(field, 'Password must be at least 6 characters');
                } else {
                    showSuccess(field, '');
                }
                break;
                
            case 'login-phone':
                if (!value) {
                    showError(field, 'Phone number is required');
                } else if (!validatePhone(value)) {
                    showError(field, 'Please enter a valid phone number');
                } else {
                    showSuccess(field, '');
                }
                break;
                
            case 'otp':
                if (!value) {
                    showError(field, 'OTP is required');
                } else if (!validateOTP(value)) {
                    showError(field, 'Please enter a valid 6-digit OTP');
                } else {
                    showSuccess(field, '');
                }
                break;
        }
    }
    
    function validatePhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/\s/g, ''));
    }
    
    function validateOTP(otp) {
        const otpRegex = /^\d{6}$/;
        return otpRegex.test(otp);
    }
    
    function showError(field, message) {
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        field.classList.add('error');
        formGroup.classList.add('error');
        formGroup.classList.remove('success');
        errorElement.textContent = message;
    }
    
    function showSuccess(field, message) {
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        field.classList.remove('error');
        formGroup.classList.remove('error');
        formGroup.classList.add('success');
        errorElement.textContent = message;
    }
    
    function clearError(field) {
        const formGroup = field.closest('.form-group');
        const errorElement = formGroup.querySelector('.error-message');
        
        field.classList.remove('error');
        formGroup.classList.remove('error', 'success');
        errorElement.textContent = '';
    }
    
    function simulateLogin() {
        const submitButton = document.querySelector('.primary-button:not(.hidden)');
        const originalText = submitButton.textContent;
        
        // Show loading state
        submitButton.classList.add('loading');
        submitButton.disabled = true;
        
        // Simulate API call
        setTimeout(() => {
            // Hide loading state
            submitButton.classList.remove('loading');
            submitButton.disabled = false;
            submitButton.textContent = originalText;
            
            // Show success animation
            showSuccessAnimation();
        }, 2000);
    }
    
    function showSuccessAnimation() {
        const successAnimation = document.querySelector('.success-animation');
        if (successAnimation) {
            successAnimation.style.display = 'flex';
            
            setTimeout(() => {
                successAnimation.style.display = 'none';
                // In a real app, redirect to dashboard
                console.log('Login successful! Redirecting to dashboard...');
            }, 3000);
        }
    }
});