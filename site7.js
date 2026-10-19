window.toggleView = function(page, full){
  var hide = 'position:absolute;visibility:hidden;pointer-events:none;top:0;left:0;width:100%';
  if (page === 'start'){
    document.getElementById('panel-full').style.cssText = full ? '' : hide;
    document.getElementById('panel-short').style.cssText = full ? hide : '';
  } else if (page === 'less'){
    document.getElementById('less-details').style.display = full ? '' : 'none';
  }
  var bf = document.getElementById('btn-full'), bs = document.getElementById('btn-short');
  if (bf) bf.classList.toggle('active', full);
  if (bs) bs.classList.toggle('active', !full);
  var l = document.getElementById('view-label');
  if (l) l.textContent = full ? 'Сейчас показана ДЕТАЛЬНАЯ схема' : 'Сейчас показана КОРОТКАЯ схема';
};
