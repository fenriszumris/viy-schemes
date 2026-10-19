window.toggleView = function(page, full){
  var hide = 'position:absolute;visibility:hidden;pointer-events:none;top:0;left:0;width:100%';
  var pf = document.getElementById('panel-full'), ps = document.getElementById('panel-short');
  if (pf) pf.style.cssText = full ? '' : hide;
  if (ps) ps.style.cssText = full ? hide : '';
  var bf = document.getElementById('btn-full'), bs = document.getElementById('btn-short');
  if (bf) bf.classList.toggle('active', full);
  if (bs) bs.classList.toggle('active', !full);
  var l = document.getElementById('view-label');
  if (l) l.textContent = full ? 'Сейчас показана ДЕТАЛЬНАЯ схема' : 'Сейчас показана КОРОТКАЯ схема';
};
