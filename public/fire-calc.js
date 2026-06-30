(function () {
  var cfg = document.getElementById('fire-config');
  if (!cfg) return;
  var COUNTRY_FIRE = Number(cfg.dataset.countryFire);
  var US_FIRE = Number(cfg.dataset.usFire);

  function yearsTo(savings, monthly, target, annualReturn) {
    if (savings >= target) return 0;
    var r = annualReturn / 12;
    if (monthly <= 0) return Infinity;
    if (r === 0) return (target - savings) / monthly / 12;
    var top = target * r + monthly;
    var bot = savings * r + monthly;
    if (bot <= 0 || top <= 0) return Infinity;
    return Math.max(0, Math.log(top / bot) / Math.log(1 + r) / 12);
  }

  function update() {
    var age     = Math.min(60, Math.max(18, parseInt(document.getElementById('fc-age').value) || 35));
    var savings = Math.min(10000000, Math.max(0, parseFloat(document.getElementById('fc-savings').value) || 0));
    var monthly = Math.min(50000,    Math.max(0, parseFloat(document.getElementById('fc-monthly').value) || 0));
    var ret     = parseFloat(document.getElementById('fc-return').value) / 100;

    document.getElementById('fc-return-display').textContent = (ret * 100).toFixed(1) + '%';
    document.querySelector('.fire-calc-disclaimer').textContent =
      'Assumes ' + (ret * 100).toFixed(1) + '% annual investment return and 4% withdrawal rate. ' +
      'Actual returns vary. This is a planning illustration, not financial advice. ' +
      'Consult a qualified financial planner before making relocation decisions.';

    var yCo = yearsTo(savings, monthly, COUNTRY_FIRE, ret);
    var yUS = yearsTo(savings, monthly, US_FIRE, ret);

    var ageCo = Math.round(age + yCo);
    var ageUS = Math.round(age + yUS);
    var diff  = yUS - yCo;

    document.getElementById('fc-age-country').textContent =
      isFinite(yCo) ? 'Age ' + ageCo : '> 100 yrs';
    document.getElementById('fc-age-us').textContent =
      isFinite(yUS) ? 'Age ' + ageUS : '> 100 yrs';

    if (isFinite(diff)) {
      var abs = Math.abs(diff);
      var yrs = Math.floor(abs);
      var mos = Math.round((abs - yrs) * 12);
      var label;
      if (diff > 0.5) {
        label = (yrs > 0 ? yrs + ' yr' + (yrs !== 1 ? 's' : '') : '') +
                (mos > 0 ? (yrs > 0 ? ' ' : '') + mos + ' mo' : '') + ' earlier';
      } else if (diff < -0.5) {
        label = Math.ceil(Math.abs(diff)) + ' yrs later';
      } else {
        label = 'Same timeline';
      }
      document.getElementById('fc-diff').textContent = label;
    } else {
      document.getElementById('fc-diff').textContent = '—';
    }

    var rawPct = savings / COUNTRY_FIRE * 100;
    var pct = Math.min(100, Math.round(rawPct));
    document.getElementById('fc-pct').textContent = rawPct > 0 && pct === 0 ? '< 1%' : pct + '%';
    document.getElementById('fc-fill').style.width = (rawPct > 0 ? Math.max(1, pct) : 0) + '%';

    var hint = document.getElementById('fc-hint');
    if (hint) {
      var hintMsg = '';
      if (!isFinite(yCo) || ageCo >= 65) {
        var targetYears = Math.max(1, 55 - age);
        var n = targetYears * 12;
        var mr = ret / 12;
        var factor = Math.pow(1 + mr, n);
        var needed = mr > 0
          ? (COUNTRY_FIRE - savings * factor) * mr / (factor - 1)
          : (COUNTRY_FIRE - savings) / n;
        needed = Math.max(0, Math.ceil(needed / 50) * 50);
        hintMsg = 'At this savings rate you’ll reach FIRE at traditional retirement age. ' +
          'Saving $' + needed.toLocaleString() + '/month would get you there by age 55.';
      } else if (ageCo >= 55) {
        var targetYears2 = Math.max(1, 50 - age);
        var n2 = targetYears2 * 12;
        var factor2 = Math.pow(1 + ret / 12, n2);
        var needed2 = ret > 0
          ? (COUNTRY_FIRE - savings * factor2) * (ret / 12) / (factor2 - 1)
          : (COUNTRY_FIRE - savings) / n2;
        needed2 = Math.max(0, Math.ceil(needed2 / 50) * 50);
        if (needed2 > monthly && targetYears2 > 0) {
          hintMsg = 'You’re close. Bumping monthly savings to $' + needed2.toLocaleString() +
            ' could move your FIRE date to age 50.';
        }
      }
      hint.textContent = hintMsg;
      hint.style.display = hintMsg ? 'block' : 'none';
    }
  }

  ['fc-age', 'fc-savings', 'fc-monthly', 'fc-return'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('input', update);
  });

  var clampRules = {
    'fc-age':     { min: 18, max: 60,       errMin: 'Minimum age is 18.', errMax: 'FIRE targets retirement before 60. Above that it\'s regular retirement, not early retirement.' },
    'fc-savings': { min: 0,  max: 10000000, errMin: 'Savings cannot be negative.', errMax: 'Maximum supported value is $10,000,000.' },
    'fc-monthly': { min: 0,  max: 50000,    errMin: 'Monthly savings cannot be negative.', errMax: 'Maximum supported value is $50,000/month.' }
  };

  function validateAll() {
    var hasError = false;
    Object.keys(clampRules).forEach(function (id) {
      var el = document.getElementById(id);
      var errEl = document.getElementById(id + '-err');
      if (!el) return;
      var rule = clampRules[id];
      var val = parseFloat(el.value);
      var msg = '';
      if (isNaN(val) || val < rule.min) msg = rule.errMin;
      else if (val > rule.max)          msg = rule.errMax;
      if (errEl) errEl.textContent = msg;
      if (msg) { el.classList.add('fire-input-error'); hasError = true; }
      else       el.classList.remove('fire-input-error');
    });
    var overlay = document.getElementById('fc-overlay');
    if (overlay) overlay.style.display = hasError ? 'flex' : 'none';
    return !hasError;
  }

  Object.keys(clampRules).forEach(function (id) {
    var el = document.getElementById(id);
    if (!el) return;

    el.addEventListener('input', function () {
      validateAll();
      update();
    });

    el.addEventListener('blur', function () {
      var rule = clampRules[id];
      var val = parseFloat(el.value);
      if (isNaN(val) || val < rule.min) el.value = rule.min;
      else if (val > rule.max)          el.value = rule.max;
      validateAll();
      update();
    });
  });

  update();
})();
