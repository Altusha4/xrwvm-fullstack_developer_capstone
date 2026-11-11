export async function api(path, data) {
  const options={credentials:'same-origin'};
  if(data!==undefined){options.method='POST';options.headers={'Content-Type':'application/json','X-CSRFToken':decodeURIComponent(document.cookie.split('; ').find(v=>v.startsWith('csrftoken='))?.split('=')[1]||'')};options.body=JSON.stringify(data);}
  const response=await fetch('/djangoapp/'+path,options);
  const result=await response.json();
  if(!response.ok)throw new Error(result.error||'Request failed');
  return result;
}
