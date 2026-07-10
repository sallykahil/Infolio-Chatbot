(function () {
  var script = document.currentScript;
  var API   = script.getAttribute('data-api')   || '';
  var TID   = script.getAttribute('data-tenant') || '';
  var TITLE = script.getAttribute('data-title')  || 'Ask Us Anything';
  var BRAND = script.getAttribute('data-brand')  || 'Chat';

  var css = [
    '.iw-bubble{position:fixed;bottom:20px;right:20px;width:56px;height:56px;border-radius:50%;',
    'background:#2F7BEE;color:#fff;display:flex;align-items:center;justify-content:center;',
    'font-size:24px;cursor:pointer;box-shadow:0 4px 16px rgba(47,123,238,.4);z-index:999999;border:none}',
    '.iw-panel{position:fixed;bottom:88px;right:20px;width:320px;max-width:90vw;height:440px;',
    'background:#fff;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.2);display:none;',
    'flex-direction:column;overflow:hidden;font-family:Inter,Arial,sans-serif;z-index:999999}',
    '.iw-panel.open{display:flex}',
    '.iw-head{background:#2F7BEE;color:#fff;padding:14px 16px;font-weight:700;font-size:14px}',
    '.iw-sub{font-size:11px;font-weight:400;opacity:.85;margin-top:2px}',
    '.iw-msgs{flex:1;overflow-y:auto;padding:12px;background:#F5F8FF;display:flex;flex-direction:column;gap:8px}',
    '.iw-msg{max-width:85%;padding:8px 11px;border-radius:10px;font-size:13px;line-height:1.4}',
    '.iw-msg.bot{background:#EEF3FC;color:#0F1C35;align-self:flex-start}',
    '.iw-msg.user{background:#2F7BEE;color:#fff;align-self:flex-end}',
    '.iw-row{display:flex;border-top:1px solid #E3EAFA;padding:8px}',
    '.iw-input{flex:1;border:none;outline:none;font-size:13px;padding:8px;font-family:inherit}',
    '.iw-send{background:#2F7BEE;color:#fff;border:none;border-radius:6px;padding:0 14px;cursor:pointer;font-size:13px}'
  ].join('');
  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  var bubble = document.createElement('button');
  bubble.className = 'iw-bubble';
  bubble.textContent = '💬';

  var panel = document.createElement('div');
  panel.className = 'iw-panel';
  panel.innerHTML =
    '<div class="iw-head">' + TITLE + '<div class="iw-sub">' + BRAND + '</div></div>' +
    '<div class="iw-msgs"></div>' +
    '<div class="iw-row">' +
      '<input class="iw-input" type="text" placeholder="Type a question…"/>' +
      '<button class="iw-send">Send</button>' +
    '</div>';

  document.body.appendChild(bubble);
  document.body.appendChild(panel);

  var msgs  = panel.querySelector('.iw-msgs');
  var input = panel.querySelector('.iw-input');
  var send  = panel.querySelector('.iw-send');

  function addMsg(text, who) {
    var m = document.createElement('div');
    m.className = 'iw-msg ' + who;
    m.textContent = text;
    msgs.appendChild(m);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function ask() {
    var q = input.value.trim();
    if (!q) return;
    addMsg(q, 'user');
    input.value = '';
    addMsg('…', 'bot');
    var thinking = msgs.lastChild;
    fetch(API + '/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tenant_id: TID, question: q })
    })
      .then(function (r) { return r.json(); })
      .then(function (d) { thinking.textContent = d.answer || "Sorry, I couldn't find an answer."; })
      .catch(function () { thinking.textContent = 'Something went wrong. Please try again.'; });
  }

  send.addEventListener('click', ask);
  input.addEventListener('keydown', function (e) { if (e.key === 'Enter') ask(); });
  bubble.addEventListener('click', function () {
    panel.classList.toggle('open');
    if (panel.classList.contains('open') && !msgs.children.length) {
      addMsg('Hi! Ask me anything about ' + BRAND + '.', 'bot');
    }
  });
})();
