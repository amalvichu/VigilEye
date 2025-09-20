function validateName(name) {
    if (name.trim() === '') return "Name cannot be empty.";
    if (name.length < 2) return "Name must be at least 2 characters.";
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

document.addEventListener('DOMContentLoaded', () => {
    const mobileInput = document.getElementById('mobile');
    const sendOtpBtn = document.getElementById('send-otp-btn');
    const otpGroup = document.getElementById('otp-group');
    const verifyOtpBtn = document.getElementById('verify-otp-btn');
    const otpInput = document.getElementById('otp');
    const registrationForm = document.getElementById('registration-form');
    const submitBtn = document.getElementById('submit-btn');

    let isMobileVerified = false;

    sendOtpBtn.addEventListener('click', async () => {
        const mobile = mobileInput.value;
        const mobileError = validateMobile(mobile);
        document.getElementById('mobile-error').textContent = mobileError;

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
                    document.getElementById('mobile-error').textContent = data.error;
                }
            } catch (e) {
                document.getElementById('mobile-error').textContent = 'An error occurred. Please try again.';
            }
        }
    });

  
    verifyOtpBtn.addEventListener('click', async () => {
        const mobile = mobileInput.value;
        const otp = otpInput.value;

        if (otp.length !== 6) {
            document.getElementById('otp-error').textContent = 'Please enter a 6-digit OTP.';
            return;
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
                document.getElementById('otp-error').textContent = data.error;
                isMobileVerified = false;
            }
        } catch (e) {
            document.getElementById('otp-error').textContent = 'An error occurred. Please try again.';
            isMobileVerified = false;
        }
    });

    
    registrationForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const name = document.getElementById('name').value;
        const mobile = document.getElementById('mobile').value;
        const password = document.getElementById('password').value;

        const nameError = validateName(name);
        const mobileError = validateMobile(mobile);
        const passwordError = validatePassword(password);

        document.getElementById('name-error').textContent = nameError;
        document.getElementById('mobile-error').textContent = mobileError;
        document.getElementById('password-error').textContent = passwordError;

        if (nameError || mobileError || passwordError || !isMobileVerified) {
   
            return;
        }


        try {
            const response = await fetch('/api/register/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, mobile, password }),
            });
            const data = await response.json();
            if (response.ok) {
                alert('Registration successful!');
                window.location.href = '/success_page/';
            } else {
                alert('Registration failed: ' + data.error);
            }
        } catch (e) {
            alert('An error occurred during registration.');
        }
    });
});