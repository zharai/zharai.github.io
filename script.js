function redirect(userType) {
    // Check which checkbox was clicked
    let message = "";
    let url = "";

    if (userType === "employer") {
        message = "Redirecting you to the employer's job submission page.";
        url = "employer.html";
    } else if (userType === "student") {
        message = "Redirecting you to the job search page for students.";
        url = "student.html";
    }

    // Show a pop-up message
    if (confirm(message)) {
        window.location.href = url;
    } else {
        // Uncheck the checkbox if redirection is canceled
        document.getElementById(userType).checked = false;
    }
}
