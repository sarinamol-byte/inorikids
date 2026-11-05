(function(){
  // Gallery filters + lightbox (projects page)
  var g=document.getElementById('gallery');
  if(g){
    var btns=document.querySelectorAll('.filters button');
    btns.forEach(function(b){b.addEventListener('click',function(){
      btns.forEach(function(x){x.setAttribute('aria-pressed',String(x===b))});
      g.querySelectorAll('[data-c]').forEach(function(p){p.hidden=!(b.dataset.f==='all'||p.dataset.c===b.dataset.f)});
    })});
    var lb=document.getElementById('lb'),li=document.getElementById('lb-img'),lc=document.getElementById('lb-cap'),last=null;
    g.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;last=b;var im=b.querySelector('img');li.src=im.src;li.alt=im.alt;lc.textContent=im.alt;lb.hidden=false;document.getElementById('lb-close').focus()});
    function close(){lb.hidden=true;if(last)last.focus()}
    document.getElementById('lb-close').addEventListener('click',close);
    lb.addEventListener('click',function(e){if(e.target===lb)close()});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!lb.hidden)close()});
  }
  // Enquiry form -> WhatsApp hand-off (works on any static host, no server needed)
  var f=document.getElementById('enq-form');
  if(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();
      var err=document.getElementById('q-err');
      var req=[].slice.call(f.querySelectorAll('[required]'));
      var bad=req.filter(function(i){return !i.value.trim()||!i.checkValidity()});
      if(bad.length){err.textContent='Please fill in your name, organisation, phone and a valid email.';bad[0].focus();return}
      err.textContent='';
      var v=function(id){var el=document.getElementById(id);return el?el.value.trim():''};
      var lines=[].slice.call(f.querySelectorAll('input[name=line]:checked')).map(function(c){return c.value}).join(', ');
      var msg='New enquiry from inorikids.com%0A'+
        ['Name: '+v('q-name'),'Organisation: '+v('q-org'),'Phone: '+v('q-phone'),'Email: '+v('q-email'),
         'Project type: '+v('q-type'),'City: '+v('q-city'),'Interested in: '+(lines||'-'),
         'Area (sq ft): '+(v('q-area')||'-'),'Timeline: '+v('q-when'),'Details: '+(v('q-msg')||'-')]
        .map(encodeURIComponent).join('%0A');
      var box=f.querySelector('.send');if(box)box.remove();
      box=document.createElement('div');box.className='send';box.setAttribute('role','status');
      box.innerHTML='<p><strong>Almost done.</strong> Tap below to send these details to our team on WhatsApp.</p>'+
        '<div class="acts"><a class="btn" target="_blank" rel="noopener" href="https://wa.me/'+f.dataset.wa1+'?text='+msg+'">Send to '+f.dataset.name1+' on WhatsApp</a>'+
        '<a class="btn ghost" target="_blank" rel="noopener" href="https://wa.me/'+f.dataset.wa2+'?text='+msg+'">Send to '+f.dataset.name2+'</a></div>';
      f.appendChild(box);box.querySelector('a').focus();
    });
  }
})();
