async function login(){
  let role = document.getElementById("role").value;
  let rationCard = document.getElementById("rationCard").value;
  let password = document.getElementById("password").value;

  let res = await fetch("/api/login", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({role,ration_card:rationCard,password})
  });
  let data = await res.json();
  if(data.error){
    document.getElementById("loginMsg").innerText = data.error;
  } else {
    window.user = data;
    showDashboard(data.role);
    loadStock();
    if(data.role==="admin") loadFeedback();
  }
}

function logout(){
  window.user = null;
  document.querySelectorAll(".dashboard").forEach(d=>d.style.display="none");
  document.getElementById("loginPage").style.display="block";
}

function showDashboard(role){
  document.getElementById("loginPage").style.display="none";
  document.querySelectorAll(".dashboard").forEach(d=>d.style.display="none");
  if(role==="admin") document.getElementById("adminDashboard").style.display="block";
  if(role==="dealer") document.getElementById("dealerDashboard").style.display="block";
  if(role==="beneficiary") document.getElementById("beneficiaryDashboard").style.display="block";
}

async function loadStock(){
  let res = await fetch("/api/stock");
  let data = await res.json();
  document.getElementById("adminStockList").innerHTML =
    data.map(s=>`<li class="list-group-item">${s.item}: ${s.quantity} ${s.unit}</li>`).join("");
  document.getElementById("dealerStockList").innerHTML =
    data.map(s=>`<li class="list-group-item">${s.item}: ${s.quantity} ${s.unit}</li>`).join("");
  document.getElementById("beneficiaryStockList").innerHTML =
    data.map(s=>`<li class="list-group-item">${s.item}: ${s.quantity} ${s.unit}</li>`).join("");
  document.getElementById("distItem").innerHTML =
    data.map(s=>`<option>${s.item}</option>`).join("");
}

async function addStock(e){
  e.preventDefault();
  let item=document.getElementById("stockItem").value;
  let qty=parseInt(document.getElementById("stockQty").value);
  await fetch("/api/stock",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({item,quantity:qty})});
  loadStock();
}

async function distribute(e){
  e.preventDefault();
  let ration_card=document.getElementById("beneficiaryCard").value;
  let item=document.getElementById("distItem").value;
  let qty=parseInt(document.getElementById("distQty").value);
  let res=await fetch("/api/distribute",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({ration_card,item,qty})});
  let data=await res.json();
  document.getElementById("distMsg").innerText=data.success?"Distributed!":data.error;
  loadStock();
}

async function sendFeedback(e){
  e.preventDefault();
  let rating=document.getElementById("rating").value;
  let comment=document.getElementById("comment").value;
  await fetch("/api/feedback",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({user_id:window.user.id,rating,comment})});
  alert("Feedback submitted!");
  document.getElementById("comment").value="";
  loadFeedback();
}

async function loadFeedback(){
  let res=await fetch("/api/feedback");
  let data=await res.json();
  document.getElementById("feedbackList").innerHTML=
    data.map(f=>`<li class="list-group-item">Rating: ${f.rating} - ${f.comment}</li>`).join("");
}
