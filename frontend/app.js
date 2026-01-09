const API = "http://127.0.0.1:8000";

// REGISTER
async function register(){
    if(first.value.length<2 || last.value.length<2){
       msg.innerText="Names and username must be at least 2 characters";
        return; 
    }

    if(!validPassword(pass.value)){
        msg.innerText="Password must be 6+ chars, include number & special char";
        return;
    }

    const res = await fetch(`${API}/user-register`,{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            firstName:first.value,
            lastName:last.value,
            username:user.value,
            password:pass.value,
            role:role.value
        })
    });
    const data = await res.json();
    msg.innerText = data.message || data.detail;
}

// LOGIN
async function login(){
    const res = await fetch(`${API}/login`,{
        method:"POST",
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            username:user.value,
            password:pass.value
        })
    });
    const data = await res.json();
    if(data.access_token){
        localStorage.setItem("token", data.access_token);
        window.location="dashboard.html";
    } else {
        msg.innerText = "Login failed";
    }
}

// LOAD PRODUCTSks
async function loadProducts(){
    const res = await fetch(`${API}/get-products`,{
        headers:{
            Authorization: `Bearer ${localStorage.getItem("token")}`
        }
    });

    if(res.status == 401){
        logout();
        return;
    }

    const products = await res.json();
    productsDiv.innerHTML = "";

    products.forEach(p=>{
        productsDiv.innerHTML += `
        <div class="card">
            <img src="${p.image || 'https://via.placeholder.com/200'}">
            <h3>${p.name}</h3>
            <p>${p.description}</p>
            <span>R ${p.price}</span>
        </div>`;
    });
}

// LOGOUT
function logout(){
    localStorage.removeItem("token");
    window.location="login.html";
}

function validPassword(p){
    return p.length>=6 && /\d/.test(p) && /[!@#$%^&*()_+=\-]/.test(p);
}
