'use strict';
const button=document.getElementById('prepare-download');
const status=document.getElementById('download-status');
const progress=document.getElementById('download-progress');
let objectUrl;
button.onclick=async()=>{
 button.disabled=true;progress.hidden=false;progress.value=0;
 try {
  const response=await fetch('downloads/manifest.json');if(!response.ok)throw new Error('Não foi possível acessar o instalador.');
  const manifest=await response.json();const chunks=[];let received=0;
  for(const part of manifest.parts){
   status.textContent='Baixando o instalador… '+Math.round(received/manifest.size*100)+'%';
   const r=await fetch('downloads/'+part.name);if(!r.ok)throw new Error('O download foi interrompido. Tente novamente.');
   const data=await r.arrayBuffer();const digest=await crypto.subtle.digest('SHA-256',data);const hash=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
   if(data.byteLength!==part.size||hash!==part.sha256)throw new Error('O arquivo recebido está incompleto. Tente baixar novamente.');
   chunks.push(data);received+=data.byteLength;progress.value=Math.round(received/manifest.size*100);
  }
  if(received!==manifest.size)throw new Error('Tamanho do instalador incorreto.');
  if(objectUrl)URL.revokeObjectURL(objectUrl);objectUrl=URL.createObjectURL(new Blob(chunks,{type:'application/octet-stream'}));
  const save=document.getElementById('save-installer');save.href=objectUrl;save.download=manifest.filename;save.hidden=false;save.click();
  status.textContent='Instalador verificado. Se o download não começou, clique em Salvar abaixo.';
 }catch(e){status.textContent=e.message;}finally{button.disabled=false;}
};
window.addEventListener('pagehide',()=>{if(objectUrl)URL.revokeObjectURL(objectUrl);});
