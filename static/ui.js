/* Custom SVG icon system and Anime.js 4.5.0 interaction layer. No network calls. */
(() => {
  'use strict';
  const paths = {
    heart:'M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z',
    calendar:'M4 5h16v16H4zM8 3v4m8-4v4M4 10h16M8 14h2m4 0h2m-8 4h2',
    card:'M3 5h18v14H3zM3 10h18M6 15h4',
    bank:'m3 9 9-6 9 6H3Zm2 3v7m7-7v7m7-7v7M2 22h20',
    phone:'M6 2h12v20H6zM10 18h4M6 6h12',
    grid:'M3 3h7v7H3zM14 3h7v7h-7zM3 14h7v7H3zM14 14h7v7h-7z',
    book:'M12 5c-3-2-6-2-9-1v15c3-1 6-1 9 1 3-2 6-2 9-1V4c-3-1-6-1-9 1Zm0 0v15',
    books:'M3 4h4v16H3zM10 4h4v16h-4zM16 5l4-1 3 15-4 1z',
    chart:'M4 20V10h4v10m4 0V4h4v16m4 0V7h2v13M2 20h21',
    swap:'M3 7h17m-4-4 4 4-4 4M21 17H4m4-4-4 4 4 4',
    clock:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9-5v5l4 2',
    arrow:'M5 19 19 5M5 5h14v14',
    down:'M12 3v17m-6-6 6 6 6-6',
    plus:'M12 4v16M4 12h16',
    search:'M20 20l-5-5m2-5a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z',
    users:'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m18 0v-2a4 4 0 0 0-3-4M13 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm4-4a4 4 0 0 1 0 8',
    spark:'m12 2 2.6 7.4L22 12l-7.4 2.6L12 22l-2.6-7.4L2 12l7.4-2.6L12 2Z',
    wallet:'M20 8V5a2 2 0 0 0-2-2H5a3 3 0 0 0 0 6h15v11H5a3 3 0 0 1-3-3V6m18 6h-5v5h5m-3-2.5h.01',
    globe:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM3 12h18M12 3c-5 5-5 13 0 18 5-5 5-13 0-18Z',
    shield:'m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6',
    check:'m5 12 4 4L19 6',
    close:'m6 6 12 12M6 18 18 6',
    edit:'m15 4 5 5M4 20l5-1L21 7a2 2 0 0 0-5-5L4 14v6Z',
    trash:'M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7',
    download:'M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5',
    info:'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM12 11v6m0-10h.01',
    award:'M16 8a4 4 0 1 1-8 0 4 4 0 0 1 8 0Zm-7 4-2 9 5-3 5 3-2-9',
    logout:'M9 4H4v16h5m5-13 5 5-5 5m-6-5h13',
    lock:'M6 10h12v11H6zM8 10V6a4 4 0 0 1 8 0v4',
    mail:'M3 5h18v14H3zM3 5l9 8 9-8'
  };
  function icon(name) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 24 24'); svg.setAttribute('fill','none');
    svg.setAttribute('stroke','currentColor'); svg.setAttribute('stroke-width','1.7');
    svg.setAttribute('stroke-linecap','round'); svg.setAttribute('stroke-linejoin','round');
    svg.setAttribute('aria-hidden','true'); svg.classList.add('ui-icon');
    const path = document.createElementNS(svg.namespaceURI,'path');
    path.setAttribute('d',paths[name] || paths.spark); svg.append(path); return svg;
  }
  const glyphs = {'◫':'grid','▤':'book','⌑':'books','◷':'clock','▥':'chart','⇄':'swap','◎':'globe','⌘':'grid','✳':'spark','↗':'arrow','↘':'down','↓':'down','＋':'plus','⌕':'search','∿':'chart','◈':'wallet','✓':'check','×':'close'};
  const decoration = {
    '#load-sample':'users','#add-student':'plus','#export':'download',
    '[data-edit]':'edit','[data-delete]':'trash','#sign-out':'logout',
    '#entry-register':'users','.note-icon':'info',
    '.count-card .summary-icon':'users','.average-card .summary-icon':'chart',
    '.pass-card .summary-icon':'award'
  };
  function hydrate() {
    document.querySelectorAll('[data-icon]').forEach(el => {
      if (!el.querySelector('svg')) el.replaceChildren(icon(el.dataset.icon));
    });
    document.querySelectorAll('button, nav a, .search>span, .summary-icon, .activity-icon, .empty>span, .small-star, .orbit-icon, .graph-star, .wallet-glyph, .highlight-mark, .role-icon, .sidebar-card>span, .tiny-star, .entry-book>span, .art-star, .cover-flower, .entry-story-footer>span').forEach(el => {
      const walker = document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
      const nodes = []; while (walker.nextNode()) if (!walker.currentNode.parentElement.closest('svg')) nodes.push(walker.currentNode);
      nodes.forEach(node => {
        if (![...node.textContent].some(char => glyphs[char])) return;
        const fragment = document.createDocumentFragment();
        node.textContent.split(/([◫▤⌑◷▥⇄◎⌘✳↗↘↓＋⌕∿◈✓×])/).forEach(part => fragment.append(glyphs[part] ? icon(glyphs[part]) : document.createTextNode(part)));
        node.replaceWith(fragment);
      });
    });
    Object.entries(decoration).forEach(([selector,name]) => document.querySelectorAll(selector).forEach(el => {
      if (!el.querySelector('svg')) el.prepend(icon(name));
    }));
  }
  const media = matchMedia('(prefers-reduced-motion: reduce)');
  const active = new Set();
  function run(targets,options) {
    if (media.matches || !window.anime) return;
    const elements = typeof targets === 'string' ? [...document.querySelectorAll(targets)] : [...targets];
    const visible = elements.filter(el => el.getClientRects().length);
    if (!visible.length) return;
    const animation = anime.animate(visible,{
      ...options,onComplete:self => { self.revert(); active.delete(self); }
    });
    active.add(animation);
  }
  function reveal(selector) {
    run(typeof selector === 'string' ? document.querySelectorAll(selector) : selector,
      {opacity:[0,1],translateY:[18,0],duration:650,delay:window.anime?.stagger(65),ease:'out(3)'});
  }
  function feedback(selector) {
    run(document.querySelectorAll(selector),{scale:[.97,1],duration:480,ease:'out(4)'});
  }
  media.addEventListener('change',() => {
    if (media.matches) { active.forEach(animation => animation.revert()); active.clear(); }
  });
  let pending = false;
  document.addEventListener('DOMContentLoaded',() => {
    hydrate();
    reveal('.entry-story-copy,.entry-login-inner,.page-heading,.balance-card,.transaction-card,.summary-card,.feature-ribbon');
    new MutationObserver(() => {
      if (pending) return; pending = true;
      requestAnimationFrame(() => { pending = false; hydrate(); });
    }).observe(document.body,{childList:true,subtree:true});
    document.addEventListener('click',event => {
      const button = event.target.closest('button');
      if (button && !button.disabled) run([button],{opacity:[.65,1],duration:260,ease:'out(3)'});
    });
  });
  window.AppUI = {icon,hydrate,reveal,feedback};
})();
