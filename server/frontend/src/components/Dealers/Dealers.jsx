import React,{useEffect,useState} from 'react';
import {api} from '../../api';
export default function Dealers({user}){
 const [all,setAll]=useState([]),[dealers,setDealers]=useState([]),[error,setError]=useState('');
 useEffect(()=>{api('get_dealers').then(r=>{setAll(r.dealers);setDealers(r.dealers);}).catch(e=>setError(e.message));},[]);
 async function filter(state){try{setDealers((await api('get_dealers/'+encodeURIComponent(state))).dealers);setError('');}catch(e){setError(e.message);}}
 return <><h1>Find a dealership</h1><label>State <select aria-label="State" onChange={e=>filter(e.target.value)}><option value="All">All States</option>{[...new Set(all.map(d=>d.state))].sort().map(s=><option key={s}>{s}</option>)}</select></label>{error&&<p role="alert">{error}</p>}<table><thead><tr><th>Dealer</th><th>City</th><th>Address</th><th>State</th>{user&&<th>Review</th>}</tr></thead><tbody>{dealers.map(d=><tr key={d.id}><td><a href={'/dealer/'+d.id}>{d.full_name}</a></td><td>{d.city}</td><td>{d.address}, {d.zip}</td><td>{d.state}</td>{user&&<td><a href={'/postreview/'+d.id}>Post Review</a></td>}</tr>)}</tbody></table></>;
}
