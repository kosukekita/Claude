# Slide Templates — slide-making

8 種のスライド種別別 HTML スニペット。  
各スニペットは `assets/template.html` の `<section class="slide">` 内にコピーして使う。  
**テキストは最大 3 行。** `{{...}}` はプレースホルダ。

---

## 1. タイトルスライド

```html
<section class="slide">
  <div class="center" style="height:100%;">
    <p class="slide-body" style="margin-bottom:0.3em; opacity:0.6;">{{CONFERENCE_NAME}} | {{DATE}}</p>
    <h1 class="slide-title" style="text-align:center; max-width:1400px;">{{PRESENTATION_TITLE}}</h1>
    <p class="slide-body" style="margin-top:0.6em;">{{AUTHOR_NAME}} — {{AFFILIATION}}</p>
  </div>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```

---

## 2. 目次スライド

```html
<section class="slide">
  <h1 class="slide-title">目次</h1>
  <hr class="slide-divider">
  <div class="row" style="margin-top:1em; gap:80px;">
    <div class="col slide-body">
      <p>1. {{SECTION_1}}</p>
      <p>2. {{SECTION_2}}</p>
      <p>3. {{SECTION_3}}</p>
    </div>
    <div class="col slide-body">
      <p>4. {{SECTION_4}}</p>
      <p>5. {{SECTION_5}}</p>
      <p>6. {{SECTION_6}}</p>
    </div>
  </div>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```

---

## 3. 箇条書き（最大 3 行）

```html
<section class="slide">
  <h1 class="slide-title">{{SLIDE_TITLE}}</h1>
  <hr class="slide-divider">
  <ul class="slide-body" style="list-style:none; margin-top:0.8em; display:flex; flex-direction:column; gap:0.6em;">
    <li>▶ <span class="emp-u">{{KEY_TERM_1}}</span> — {{BRIEF_DESCRIPTION_1}}</li>
    <li>▶ <span class="emp-u">{{KEY_TERM_2}}</span> — {{BRIEF_DESCRIPTION_2}}</li>
    <li>▶ <span class="emp-u">{{KEY_TERM_3}}</span> — {{BRIEF_DESCRIPTION_3}}</li>
  </ul>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```

---

## 4. 比較（2 列）

```html
<section class="slide">
  <h1 class="slide-title">{{SLIDE_TITLE}}</h1>
  <hr class="slide-divider">
  <div class="row" style="margin-top:1em; flex:1;">
    <div class="col" style="border-right: 2px solid var(--text-color); padding-right:40px;">
      <h2 class="slide-heading" style="margin-bottom:0.4em;">{{LEFT_LABEL}}</h2>
      <p class="slide-body">{{LEFT_POINT_1}}</p>
      <p class="slide-body">{{LEFT_POINT_2}}</p>
    </div>
    <div class="col" style="padding-left:40px;">
      <h2 class="slide-heading" style="margin-bottom:0.4em;">{{RIGHT_LABEL}}</h2>
      <p class="slide-body">{{RIGHT_POINT_1}}</p>
      <p class="slide-body">{{RIGHT_POINT_2}}</p>
    </div>
  </div>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```

---

## 5. 横線のみの表

```html
<section class="slide">
  <h1 class="slide-title">{{SLIDE_TITLE}}</h1>
  <hr class="slide-divider">
  <div style="margin-top:0.8em;">
    <table>
      <thead>
        <tr>
          <th>{{HEADER_1}}</th>
          <th>{{HEADER_2}}</th>
          <th>{{HEADER_3}}</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{{ROW1_COL1}}</td>
          <td>{{ROW1_COL2}}</td>
          <td><span class="emp-inv">{{ROW1_COL3_HIGHLIGHT}}</span></td>
        </tr>
        <tr>
          <td>{{ROW2_COL1}}</td>
          <td>{{ROW2_COL2}}</td>
          <td>{{ROW2_COL3}}</td>
        </tr>
        <tr>
          <td>{{ROW3_COL1}}</td>
          <td>{{ROW3_COL2}}</td>
          <td>{{ROW3_COL3}}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```

---

## 6. グラフ（Chart.js 折れ線）

```html
<section class="slide">
  <h1 class="slide-title">{{SLIDE_TITLE}}</h1>
  <hr class="slide-divider">
  <div style="flex:1; display:flex; align-items:center; justify-content:center; margin-top:0.5em;">
    <canvas id="chart" style="max-height:720px; max-width:1600px;"></canvas>
  </div>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
  <script>
    new Chart(document.getElementById('chart'), {
      type: 'line',
      data: {
        labels: ['{{LABEL_1}}', '{{LABEL_2}}', '{{LABEL_3}}', '{{LABEL_4}}', '{{LABEL_5}}'],
        datasets: [{
          label: '{{SERIES_1}}',
          data: [{{DATA_1}}],
          borderColor: '#0071BC',
          backgroundColor: 'rgba(0,113,188,0.08)',
          borderWidth: 4, pointRadius: 6, tension: 0.3,
        }, {
          label: '{{SERIES_2}}',
          data: [{{DATA_2}}],
          borderColor: '#1A1A1A',
          borderWidth: 3, borderDash: [8, 4], pointRadius: 5, tension: 0.3,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: { legend: { labels: { font: { size: 22, family: "'Noto Sans JP','Inter',sans-serif" } } } },
        scales: {
          x: { ticks: { font: { size: 20 } }, grid: { color: 'rgba(26,26,26,0.1)' } },
          y: { ticks: { font: { size: 20 } }, grid: { color: 'rgba(26,26,26,0.1)' } }
        }
      }
    });
  </script>
</section>
```

---

## 7. 図解（アイコン横並び、矢印フロー）

```html
<section class="slide">
  <h1 class="slide-title">{{SLIDE_TITLE}}</h1>
  <hr class="slide-divider">
  <div class="row" style="flex:1; align-items:center; justify-content:center; gap:60px; margin-top:0.5em;">

    <div class="center" style="flex:1;">
      <img src="../cache/icons/{{ICON_SLUG_1}}/default.svg" alt="" class="icon icon-lg">
      <p class="slide-body" style="margin-top:0.4em; text-align:center;"><span class="emp-u">{{STEP_LABEL_1}}</span></p>
    </div>

    <div class="center" style="flex:0 0 auto;">
      <span style="font-size:60pt; color:var(--text-color);">→</span>
    </div>

    <div class="center" style="flex:1;">
      <img src="../cache/icons/{{ICON_SLUG_2}}/default.svg" alt="" class="icon icon-lg">
      <p class="slide-body" style="margin-top:0.4em; text-align:center;"><span class="emp-u">{{STEP_LABEL_2}}</span></p>
    </div>

    <div class="center" style="flex:0 0 auto;">
      <span style="font-size:60pt; color:var(--text-color);">→</span>
    </div>

    <div class="center" style="flex:1;">
      <img src="../cache/icons/{{ICON_SLUG_3}}/default.svg" alt="" class="icon icon-lg">
      <p class="slide-body" style="margin-top:0.4em; text-align:center;"><span class="emp-u">{{STEP_LABEL_3}}</span></p>
    </div>

    <div class="center" style="flex:0 0 auto;">
      <span style="font-size:60pt; color:var(--text-color);">→</span>
    </div>

    <div class="center" style="flex:1;">
      <img src="../cache/icons/{{ICON_SLUG_4}}/default.svg" alt="" class="icon icon-lg">
      <p class="slide-body" style="margin-top:0.4em; text-align:center;"><span class="emp-u">{{STEP_LABEL_4}}</span></p>
    </div>

  </div>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```

---

## 8. まとめスライド

```html
<section class="slide">
  <h1 class="slide-title">まとめ</h1>
  <hr class="slide-divider">
  <div class="slide-body" style="margin-top:0.8em; display:flex; flex-direction:column; gap:0.8em;">
    <p>① <span class="emp-u">{{KEY_FINDING_1}}</span></p>
    <p>② <span class="emp-u">{{KEY_FINDING_2}}</span></p>
    <p>③ <span class="emp-u">{{KEY_FINDING_3}}</span></p>
  </div>
  <div class="spacer"></div>
  <p class="slide-body" style="opacity:0.5; font-size:20pt;">{{CONTACT_OR_NEXT_STEP}}</p>
  <div class="slide-number">{{SLIDE_NUMBER}}</div>
</section>
```
