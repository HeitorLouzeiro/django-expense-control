const usernameField=document.querySelector('#usernameField');
const feedBackArea=document.querySelector('.invalid-feedback');
const emailField=document.querySelector('#emailField');
const emailFeedBackArea=document.querySelector('.emailFeedBackArea');
const usernameSuccessOutput=document.querySelector('.usernameSuccessOutput');
const passwordField=document.querySelector('#passwordField');
const showPasswordToggle=document.querySelector('.showPasswordToggle');

usernameField.addEventListener('keyup', (e) => {
    const usernameVal = e.target.value;
    usernameSuccessOutput.style.display="block";
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`;

    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display="none";


    if(usernameVal.length > 0){
        fetch("validate-username/",{
            body: JSON.stringify({username: usernameVal}),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            usernameSuccessOutput.style.display="none";
            if(data.username_error){
                usernameField.classList.add("is-invalid");
                feedBackArea.style.display="block";
                feedBackArea.innerHTML=`<p>${data.username_error}</p>`;
            }
        });
    }
});

emailField.addEventListener('keyup', (e) => {
    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display="none";

    if(emailVal.length > 0){
        fetch("validate-email/",{
            body: JSON.stringify({email: emailVal}),
            method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            if(data.email_error){
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display="block";
                emailFeedBackArea.innerHTML=`<p>${data.email_error}</p>`;
            }
        });
    }
});

const handleToggleInput = (e) => {
    if(showPasswordToggle.textContent === "SHOW"){
        showPasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type", "text");
    }else{
        showPasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type", "password");
    }
}

showPasswordToggle.addEventListener('click', handleToggleInput);