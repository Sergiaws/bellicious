// Variables
var username = document.getElementById("username"),
    email = document.getElementById("email"),
    passwords = [document.getElementById("password"), document.getElementById("password2")];

// Event handlers
username.onblur = function () {
    validateUser(this);
    return false;
};
username.oninput = function () {
    clearAlert(this);
    return false;
};
email.onblur = function () {
    validateEmail(this);
    return false;
};
email.oninput = function () {
    clearAlert(this);
    return false;
};
passwords[0].onblur = function () {
    validatePassword1();
    return false;
};
passwords[0].oninput = function () {
    clearAlert(this);
    return false;
};
passwords[1].onblur = function () {
    validatePassword2();
    return false;
};
passwords[1].oninput = function () {
    clearAlert(this);
    return false;
};

// Add the onsubmit event handler to the form
document.getElementById("register").onsubmit = function (event) {
    // Check the validity of the fields
    var userValid = validateUser(username);
    var emailValid = validateEmail(email);
    var passwordValid = validatePasswords();

    // Stop the form submission if any field is invalid
    if (!userValid || !emailValid || !passwordValid) {
        // Prevent the form from submitting
        if (event.preventDefault) {
            event.preventDefault();
        }
        return false;
    }
    // Allow the form submission if all fields are valid
    return true;
};

// Function to clear error containers
function clearAlert(el) {
    var alertElement = document.getElementById(el.getAttribute("aria-describedby"));
    if (alertElement && alertElement.innerHTML !== "") {
        alertElement.innerHTML = "";
    }
}

function validateUser(el) {
    var usernameAlert = document.getElementById("usernameError");
    var usernamePattern = /^[a-zA-Z0-9]{3,50}$/;
    if (usernamePattern.test(el.value) == false) {
        usernameAlert.innerHTML = "only letters or numbers are allowed and the length must be between 3 and 50";
        return false;
    } else {
        usernameAlert.innerHTML = "";
        return true;
    }
}

function validateEmail(el) {
    var emailAlert = document.getElementById("emailError");
    var emailPattern = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    if (emailPattern.test(el.value) == false) {
        emailAlert.innerHTML = "Please write a correct email address";
        return false;
    } else {
        emailAlert.innerHTML = "";
        return true;
    }
}

function validatePassword1() {
    var passwordPattern = /[A-Za-z0-9@#$%^&+=]{6,50}/;
    var password1Alert = document.getElementById("passwordError");
    var pass1 = passwords[0].value;

    if (passwordPattern.test(pass1) == false) {
        password1Alert.innerHTML = "The password doesn't match the specified format";
        return false;
    } else {
        password1Alert.innerHTML = "";
        return true;
    }
}

function validatePassword2() {
    var password2Alert = document.getElementById("passwordMatch");
    var pass1 = passwords[0].value;
    var pass2 = passwords[1].value;

    if (pass1 !== pass2) {
        password2Alert.innerHTML = "Passwords don't match";
        return false;
    } else {
        password2Alert.innerHTML = "";
        return true;
    }
}

function validatePasswords() {
    var password1Valid = validatePassword1();
    var password2Valid = validatePassword2();

    return password1Valid && password2Valid;
}
