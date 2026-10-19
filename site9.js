function toggleView(shortId, fullId){
  var s=document.getElementById(shortId), f=document.getElementById(fullId);
  if(!s||!f) return;
  var showFull=(f.style.display==='none');
  if(showFull){ f.style.display='block'; s.style.display='none'; }
  else{ s.style.display='block'; f.style.display='none'; }
  var btns=document.querySelectorAll('button[onclick*="toggleView"]');
  btns.forEach(function(b){ b.textContent = showFull ? 'Короче' : 'Детальнее'; });
  window.scrollTo(0,0);
}
function jumpHub(id){
  var el=document.getElementById(id); if(!el) return;
  var p=el.parentElement;
  while(p){ if(p.tagName==='DETAILS') p.open=true; p=p.parentElement; }
  el.open=true;
  el.scrollIntoView({behavior:'smooth',block:'center'});
  el.style.transition='box-shadow .3s';
  el.style.boxShadow='0 0 0 3px rgba(122,107,179,.45)';
  setTimeout(function(){el.style.boxShadow='';},1400);
}
function setAll(openIt){
  document.querySelectorAll('.htree details').forEach(function(d){ d.open=openIt; });
}
