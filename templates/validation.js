function validateName(name) {
    if (name.trim() === '') return "Name cannot be empty.";
    if (name.length < 2) return "Name must be at least 2 characters.";
    return '';
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        return "Please enter a valid email address.";
    }
    return '';
}

function validateMobile(mobile) {
    const mobileRegex = /^[0-9]{10}$/;
    if (!mobileRegex.test(mobile)) {
        return "Please enter a valid 10-digit mobile number.";
    }
    return '';
}

function validatePassword(password) {
    const minLength = 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[^A-Za-z0-9]/.test(password);

    if (password.length < minLength) {
        return "Password must be at least 8 characters long.";
    }
    if (!hasUppercase) return "Password must contain an uppercase letter.";
    if (!hasLowercase) return "Password must contain a lowercase letter.";
    if (!hasNumber) return "Password must contain a number.";
    if (!hasSpecialChar) return "Password must contain a special character.";

    return '';
}

function validateConfirmPassword(password, confirmPassword) {
    if (password !== confirmPassword) {
        return "Passwords do not match.";
    }
    return '';
}

function validateDOB(dob) {
    if (!dob) return "Date of Birth is required.";
    const dobDate = new Date(dob);
    const today = new Date();

    let age = today.getFullYear() - dobDate.getFullYear();
    const m = today.getMonth() - dobDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < dobDate.getDate())) {
        age--;
    }

    if (age > 18) {
        return "You must be 18 years old or younger to register.";
    }
    if (age < 0) {
        return "Invalid Date of Birth.";
    }
    return '';
}

document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById('phone');
    const sendOtpBtn = document.getElementById('send-otp-btn');
    const otpGroup = document.getElementById('otp-group');
    const verifyOtpBtn = document.getElementById('verify-otp-btn');
    const otpInput = document.getElementById('otp');
    const registrationForm = document.getElementById('registration-form');
    const submitBtn = registrationForm.querySelector('button[type="submit"]');

    const nameInput = document.getElementById('parent-name');
    const emailInput = document.getElementById('email');
    const dobInput = document.getElementById('dob');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const termsCheckbox = document.getElementById('terms');

    let isMobileVerified = false;

    // Set max attribute for DOB input to today (to prevent future dates)
    dobInput.max = new Date().toISOString().split("T")[0];

    sendOtpBtn.addEventListener('click', async () => {
        const mobile = phoneInput.value.trim();
        const mobileError = validateMobile(mobile);
        document.getElementById('phone-error').textContent = mobileError;

        if (mobileError === '') {
            try {
                const response = await fetch('/api/send_otp/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mobile }),
                });
                const data = await response.json();
                if (response.ok) {
                    alert(data.message);
                    otpGroup.style.display = 'block';
                } else {
                    document.getElementById('phone-error').textContent = data.error || 'Failed to send OTP.';
                }
            } catch (e) {
                document.getElementById('phone-error').textContent = 'An error occurred. Please try again.';
            }
        }
    });

    verifyOtpBtn.addEventListener('click', async () => {
        const mobile = phoneInput.value.trim();
        const otp = otpInput.value.trim();

        if (otp.length !== 6) {
            document.getElementById('otp-error').textContent = 'Please enter a 6-digit OTP.';
            return;
        } else {
            document.getElementById('otp-error').textContent = '';
        }

        try {
            const response = await fetch('/api/verify_otp/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mobile, otp }),
            });
            const data = await response.json();
            if (response.ok) {
                alert(data.message);
                isMobileVerified = true;
                submitBtn.disabled = false;
            } else {
                document.getElementById('otp-error').textContent = data.error || 'OTP verification failed.';
                isMobileVerified = false;
                submitBtn.disabled = true;
            }
        } catch (e) {
            document.getElementById('otp-error').textContent = 'An error occurred. Please try again.';
            isMobileVerified = false;
            submitBtn.disabled = true;
        }
    });

    // Toggle password visibility
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', () => {
            const input = icon.previousElementSibling;
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

    // Password strength meter
    const strengthMeterFill = document.querySelector('.strength-meter-fill');
    const strengthText = document.querySelector('.strength-text');

    passwordInput.addEventListener('input', () => {
        const val = passwordInput.value;
        let strength = 0;

        if (val.length >= 8) strength++;
        if (/[A-Z]/.test(val)) strength++;
        if (/[a-z]/.test(val)) strength++;
        if (/[0-9]/.test(val)) strength++;
        if (/[^A-Za-z0-9]/.test(val)) strength++;

        const strengthPercent = (strength / 5) * 100;
        strengthMeterFill.style.width = strengthPercent + '%';

        if (strength <= 2) {
            strengthMeterFill.style.backgroundColor = '#dc3545'; // red
            strengthText.textContent = 'Weak';
        } else if (strength === 3 || strength === 4) {
            strengthMeterFill.style.backgroundColor = '#ffc107'; // yellow
            strengthText.textContent = 'Medium';
        } else if (strength === 5) {
            strengthMeterFill.style.backgroundColor = '#28a745'; // green
            strengthText.textContent = 'Strong';
        } else {
            strengthMeterFill.style.backgroundColor = '#e0e0e0';
            strengthText.textContent = 'Password strength';
        }
    });

    registrationForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Clear previous errors
        document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
        document.querySelectorAll('input').forEach(input => input.classList.remove('error'));

        const name = nameInput.value.trim();
        const email = emailInput.value.trim();
        const mobile = phoneInput.value.trim();
        const dob = dobInput.value;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        const termsChecked = termsCheckbox.checked;

        const nameError = validateName(name);
        const emailError = validateEmail(email);
        const mobileError = validateMobile(mobile);
        const dobError = validateDOB(dob);
        const passwordError = validatePassword(password);
        const confirmPasswordError = validateConfirmPassword(password, confirmPassword);
        const termsError = termsChecked ? '' : 'You must agree to the Terms & Conditions.';

        // Show errors
        if (nameError) {
            nameInput.classList.add('error');
            nameInput.nextElementSibling.nextElementSibling.textContent = nameError;
        }
        if (emailError) {
            emailInput.classList.add('error');
            emailInput.nextElementSibling.nextElementSibling.textContent = emailError;
        }
        if (mobileError) {
            phoneInput.classList.add('error');
            document.getElementById('phone-error').textContent = mobileError;
        }
        if (dobError) {
            dobInput.classList.add('error');
            document.getElementById('dob-error').textContent = dobError;
        }
        if (passwordError) {
            passwordInput.classList.add('error');
            passwordInput.nextElementSibling.nextElementSibling.textContent = passwordError;
        }
        if (confirmPasswordError) {
            confirmPasswordInput.classList.add('error');
            confirmPasswordInput.nextElementSibling.nextElementSibling.textContent = confirmPasswordError;
        }
        if (termsError) {
            termsCheckbox.classList.add('error');
            termsCheckbox.nextElementSibling.nextElementSibling.textContent = termsError;
        }

        if (nameError || emailError || mobileError || dobError || passwordError || confirmPasswordError || termsError) {
            return;
        }

        if (!isMobileVerified) {
            alert('Please verify your phone number with OTP before submitting.');
            return;
        }

        try {
            const response = await fetch('/api/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, mobile, dob, password }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Registration successful!');
                window.location.href = '/success_page/';
            } else {
                alert('Registration failed: ' + (data.error || 'Unknown error'));
            }
        } catch (e) {
            alert('An error occurred during registration.');
        }
    });

    // Initially disable submit button until OTP verified
    submitBtn.disabled = true;
});
