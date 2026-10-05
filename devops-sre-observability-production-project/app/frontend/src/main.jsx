import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";

const API="/api";

function App(){
  const [restaurants,setRestaurants]=useState([]);
  const [selected,setSelected]=useState(null);
  const [token,setToken]=useState(localStorage.getItem("token")||"");
  const [email,setEmail]=useState("demo@example.com");
  const [password,setPassword]=useState("Passw0rd!123");
  const [name,setName]=useState("Demo User");
  const [message,setMessage]=useState("");
  const [cart,setCart]=useState([]);
  const [orders,setOrders]=useState([]);

  useEffect(()=>{fetch(`${API}/restaurants`).then(r=>r.json()).then(setRestaurants)},[]);

  async function register(){
    const r=await fetch(`${API}/users/register`,{
      method:"POST",headers:{"content-type":"application/json"},
      body:JSON.stringify({email,password,name})
    });
    const d=await r.json(); setMessage(d.detail||"Registration successful");
  }
  async function login(){
    const r=await fetch(`${API}/users/login`,{
      method:"POST",headers:{"content-type":"application/json"},
      body:JSON.stringify({email,password})
    });
    const d=await r.json();
    if(d.access_token){setToken(d.access_token);localStorage.setItem("token",d.access_token);setMessage("Logged in")}
    else setMessage(d.detail||"Login failed");
  }
  async function loadOrders(){
    const r=await fetch(`${API}/orders`,{headers:{authorization:`Bearer ${token}`}});
    if(r.ok)setOrders(await r.json());
  }
  async function createOrder(){
    if(!token||!selected||!cart.length){setMessage("Login, choose a restaurant and add an item");return}
    const r=await fetch(`${API}/orders`,{
      method:"POST",
      headers:{"content-type":"application/json","authorization":`Bearer ${token}`},
      body:JSON.stringify({
        restaurant_id:selected.id,
        items:cart.map(x=>({menu_item_id:x.id,quantity:x.quantity}))
      })
    });
    const d=await r.json();
    setMessage(d.message||d.detail||"Order created");
    if(r.ok){setCart([]);loadOrders()}
  }

  return <main>
    <header><h1>OrderFlow</h1><span>DevOps/SRE Production Lab</span></header>
    <section className="auth">
      <input value={name} onChange={e=>setName(e.target.value)} placeholder="Name"/>
      <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email"/>
      <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password"/>
      <button onClick={register}>Register</button><button onClick={login}>Login</button>
      <button onClick={loadOrders}>My Orders</button>
    </section>
    <p className="message">{message}</p>

    <h2>Restaurants</h2>
    <section className="grid">
      {restaurants.map(r=><article key={r.id} onClick={()=>
        fetch(`${API}/restaurants/${r.id}`).then(x=>x.json()).then(setSelected)}>
        <h3>{r.name}</h3><p>{r.cuisine} · ⭐ {r.rating}</p><small>{r.address}</small>
      </article>)}
    </section>

    {selected&&<section>
      <h2>{selected.name} Menu</h2>
      <div className="grid">
        {selected.menu.map(m=><article key={m.id}>
          <h3>{m.name}</h3><p>{m.description}</p><b>₹{m.price}</b>
          <button onClick={()=>setCart(c=>{
            const found=c.find(x=>x.id===m.id);
            return found
              ? c.map(x=>x.id===m.id?{...x,quantity:x.quantity+1}:x)
              : [...c,{...m,quantity:1}]
          })}>Add</button>
        </article>)}
      </div>
      <button className="primary" onClick={createOrder}>
        Create Order ({cart.reduce((a,x)=>a+x.quantity,0)})
      </button>
    </section>}

    <h2>Order History</h2>
    {orders.map(o=><div className="order" key={o.id}>
      #{o.id} · ₹{o.total_amount} · {o.status}
    </div>)}
  </main>
}
createRoot(document.getElementById("root")).render(<App/>);
