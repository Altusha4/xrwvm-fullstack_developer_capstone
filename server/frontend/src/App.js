import React,{useState,useEffect} from 'react';
import {Routes,Route} from 'react-router-dom';
import {api} from './api';
import Login from './components/Login/Login';
import Register from './components/Register/Register';
import Dealers from './components/Dealers/Dealers';
import Dealer from './components/Dealers/Dealer';
import PostReview from './components/Dealers/PostReview';
import './App.css';
export default function App(){
 const [user,setUser]=useState(null);const [error,setError]=useState('');
 useEffect(()=>{api('session').then(r=>setUser(r.username)).catch(e=>setError(e.message));},[]);
 return <><nav><a className="brand" href="/">BEST CARS</a><a href="/dealers">Dealerships</a><a href="/about/">About Us</a><a href="/contact/">Contact Us</a>{user?<><span>{user}</span><button onClick={async()=>{await api('logout',{});setUser(null);window.location.href='/dealers';}}>Logout</button></>:<><a href="/login">Login</a><a href="/register">Sign up</a></>}</nav><main>{error&&<p role="alert">{error}</p>}<Routes><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/><Route path="/dealers" element={<Dealers user={user}/>}/><Route path="/dealer/:id" element={<Dealer user={user}/>}/><Route path="/postreview/:id" element={<PostReview user={user}/>}/></Routes></main></>;
}
