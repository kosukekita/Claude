# Humanizer Academic: AI 文体パターン検出・修正リファレンス

> Source: [matsuikentaro1/humanizer_academic](https://github.com/matsuikentaro1/humanizer_academic)
> Based on [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)

---

## CONTENT PATTERNS

### 1. Undue Emphasis on Significance, Legacy, and Broader Trends

**検出キーワード:** stands/serves as, is a testament/reminder, a vital/significant/crucial/pivotal/key role/moment, underscores/highlights its importance/significance, reflects broader, symbolizing its ongoing/enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted

**問題:** 普通の内容を壮大な言葉で誇張する。

**Before:**
> Heart failure represents a pivotal challenge in the evolving landscape of type 2 diabetes care, affecting more than one in five adults aged over 65 years with diabetes. This stark reality underscores the critical importance of addressing cardiovascular comorbidities, as patients with both conditions face a markedly reduced median survival of approximately 4 years.

**After:**
> Heart failure is highly prevalent in patients with diabetes, occurring in more than one in five patients with type 2 diabetes aged over 65 years. Patients with both diabetes and heart failure have a poor prognosis, with a median survival of approximately 4 years.

---

### 2. Undue Emphasis on Notability and Media Coverage

**検出キーワード:** independent coverage, local/regional/national media outlets, written by a leading expert, active social media presence

**問題:** 検証不可能な実績を列挙する。

**Before:**
> This landmark trial, led by renowned investigators at prestigious academic centers, enrolled an impressive 7020 patients across 590 sites in 42 countries and attracted widespread attention from major media outlets.

**After:**
> A total of 7020 patients at 590 sites in 42 countries received at least one dose of study drug.

---

### 3. Superficial Analyses with -ing Endings

**検出キーワード:** highlighting/underscoring/emphasizing..., ensuring..., reflecting/symbolizing..., contributing to..., cultivating/fostering..., encompassing..., showcasing...

**問題:** 現在分詞（-ing）で分析の深さを詐称する。

**Before:**
> Hospitalization for heart failure occurred in 2.7% of patients receiving empagliflozin compared to 4.1% with placebo (HR 0.65; P = 0.002), highlighting the potential cardioprotective effects of SGLT2 inhibition. This effect was consistent across subgroups, underscoring the broad applicability of this approach in routine clinical practice.

**After:**
> Hospitalization for heart failure occurred in 2.7% of patients receiving empagliflozin compared to 4.1% with placebo (hazard ratio 0.65; 95% CI 0.50-0.85; P = 0.002). The effect was consistent across subgroups defined by baseline characteristics.

---

### 4. Promotional and Advertisement-like Language

**検出キーワード:** boasts a, vibrant, rich (figurative), profound, enhancing its, showcasing, exemplifies, commitment to, natural beauty, nestled, in the heart of, groundbreaking (figurative), renowned, breathtaking, must-visit, stunning

**問題:** マーケティング的な言語の不適切使用。

**Before:**
> This groundbreaking study showcases the profound impact of empagliflozin and reflects a renewed commitment to improving cardiovascular care. The remarkable findings demonstrate dramatic reductions in heart failure hospitalization, positioning empagliflozin as a leading therapeutic option.

**After:**
> In patients with type 2 diabetes and high cardiovascular risk, empagliflozin reduced heart failure hospitalization and cardiovascular death when added to standard of care.

---

### 5. Vague Attributions and Weasel Words

**検出キーワード:** Industry reports, Observers have cited, Experts argue, Some critics argue, several sources/publications (when few cited)

**問題:** 具体的な出典なしの曖昧な引用。

**Before:**
> Studies have shown that SGLT2 inhibitors reduce cardiovascular events. Experts argue that these benefits may be related to hemodynamic effects. Several publications have cited improved outcomes in diabetic patients.

**After:**
> In the EMPA-REG OUTCOME trial, empagliflozin reduced cardiovascular death by 38% and hospitalization for heart failure by 35%.

---

### 6. Outline-like "Challenges and Future Prospects" Sections

**検出キーワード:** Despite its... faces several challenges..., Despite these challenges, Challenges and Legacy, Future Outlook

**問題:** 型にはまった課題セクション。

**Before:**
> Despite its rigorous methodology, this trial faces several challenges typical of large clinical studies, including the lack of objective cardiac measurements. Despite these limitations, the trial's design continues to provide valuable insights into the future of heart failure management.

**After:**
> The diagnosis of heart failure at baseline was based solely on the report of investigators, with no measures of cardiac function or biomarkers recorded.

---

## LANGUAGE AND GRAMMAR PATTERNS

### 7. Overused "AI Vocabulary" Words

**高頻度 AI 語彙:** Additionally, align with, crucial, delve, emphasizing, enduring, enhance, fostering, garner, highlight (verb), interplay, intricate/intricacies, key (adjective), landscape (abstract noun), pivotal, showcase, tapestry (abstract noun), testament, underscore (verb), valuable, vibrant

**問題:** 2023年以降のテキストで統計的に集中する語彙。

**Before:**
> Additionally, empagliflozin reduced the risk of hospitalization for heart failure or cardiovascular death by 34%, a pivotal finding in the evolving therapeutic landscape. The number needed to treat was 35 over 3 years, underscoring the crucial clinical value of this intervention.

**After:**
> Empagliflozin reduced the risk of hospitalization for heart failure or cardiovascular death by 34%. The number needed to treat to prevent one event was 35 over 3 years.

---

### 8. Avoidance of "is"/"are" (Copula Avoidance)

**検出キーワード:** serves as/stands as/marks/represents [a], boasts/features/offers [a]

**問題:** 不必要に複雑な表現で単純な「is/are」を回避。

**Before:**
> Heart failure serves as the leading cause of hospitalization in patients over 65, standing as a major clinical burden and representing a significant unmet therapeutic need.

**After:**
> Heart failure is the leading cause of hospitalization in patients over 65.

---

### 9. Negative Parallelisms

**問題:** "Not only...but also", "It's not just...it's" の過度使用。

**Before:**
> SGLT2 inhibitors not only lower blood glucose but also reduce cardiovascular events. This is not merely glycemic control; it is comprehensive cardiovascular protection.

**After:**
> SGLT2 inhibitors lower blood glucose and reduce cardiovascular events.

---

### 10. Rule of Three Overuse

**問題:** 包括性を装った強制的な3項目分類。

**Before:**
> SGLT2 inhibitors lower glucose, reduce cardiovascular events, and improve renal outcomes. These agents offer efficacy, safety, and tolerability. Benefits span metabolic, cardiovascular, and renal domains.

**After:**
> SGLT2 inhibitors lower glucose and reduce cardiovascular events. They also slow kidney disease progression.

---

### 11. Elegant Variation (Synonym Cycling)

**問題:** 反復ペナルティによる不必要な同義語置き換え。

**Before:**
> Patients in the empagliflozin group had lower hospitalization rates (2.7% vs. 4.1%). Participants also demonstrated reduced cardiovascular mortality (3.7% vs. 5.9%). Subjects experienced decreased all-cause death rates (5.7% vs. 8.3%).

**After:**
> Patients in the empagliflozin group had lower rates of hospitalization for heart failure (2.7% vs. 4.1%), cardiovascular death (3.7% vs. 5.9%), and all-cause mortality (5.7% vs. 8.3%).

---

### 12. False Ranges

**問題:** 無意味な "from X to Y" 構造。

**Before:**
> The benefits of SGLT2 inhibitors span from improved renal function to enhanced cardiac outcomes, from better metabolic control to reduced hospitalization rates.

**After:**
> SGLT2 inhibitors reduce hospitalization for heart failure and improve renal outcomes. They also lower HbA1c modestly.

---

## STYLE PATTERNS

### 13. Em Dash Overuse

**問題:** エムダッシュ（—）の過度使用。

**Before:**
> SGLT2 inhibitors—a relatively new drug class—have transformed heart failure treatment. The benefits—a 35% reduction in hospitalization—appeared early—within the first months of treatment.

**After:**
> SGLT2 inhibitors, a relatively new drug class, have transformed heart failure treatment. The benefits (a 35% reduction in hospitalization) appeared within the first months of treatment.

---

### 14. Title Case in Headings

**問題:** AI が見出しの全単語を大文字にする。

**Before:**
> ## Statistical Analysis And Primary Endpoints

**After:**
> ## Statistical analysis and primary endpoints

---

### 15. Curly Quotation Marks

**問題:** ChatGPT 標準のカーリークォート使用。

- ストレート引用符 `"..."` に統一する。

---

## FILLER AND HEDGING

### 16. Filler Phrases

| Before | After |
|--------|-------|
| In order to assess efficacy | To assess efficacy |
| Due to the fact that patients were excluded | Because patients were excluded |
| At the present time | Currently（または省略） |
| It is important to note that mortality was reduced | Mortality was reduced |
| The study has the ability to detect | The study can detect |
| With respect to safety endpoints | For safety endpoints |

---

### 17. Excessive Hedging

**問題:** 過剰な留保がデータの知見を弱める。

**Before:**
> These findings may suggest that SGLT2 inhibitors have the potential to confer beneficial effects on cardiovascular outcomes in select patient populations.

**After:**
> These findings suggest that SGLT2 inhibitors reduce cardiovascular events.

---

### 18. Generic Positive Conclusions

**問題:** 具体性のない楽観的な結論。

**Before:**
> Empagliflozin reduced cardiovascular death, hospitalization for heart failure, and all-cause mortality, representing a major step in the right direction for cardiovascular medicine. The future looks bright for patients with type 2 diabetes as these exciting findings continue to reshape clinical practice.

**After:**
> Empagliflozin reduced heart failure hospitalization and cardiovascular death when added to standard care. The benefit was consistent in patients with and without heart failure at baseline.

---

## Full Example

**Before (AI-sounding):**
> Heart failure represents a pivotal challenge in the evolving landscape of diabetes care, underscoring the critical importance of addressing cardiovascular comorbidities. This groundbreaking study showcases the profound impact of empagliflozin, a pivotal therapeutic option that serves as a cornerstone of modern cardiovascular medicine.
>
> Studies have shown that SGLT2 inhibitors reduce cardiovascular events. Additionally, empagliflozin reduced the risk of hospitalization for heart failure or cardiovascular death by 34%—a remarkable finding—highlighting the cardioprotective effects of this intervention. The number needed to treat of 35 over 3 years underscores the crucial clinical value of this therapeutic approach.
>
> Despite challenges typical of large clinical trials, including the lack of objective cardiac measurements, the trial's strategic design continues to provide valuable insights for the future outlook of heart failure management. The future looks bright for patients with type 2 diabetes as these exciting findings continue to reshape clinical practice.

**After (Humanized):**
> Heart failure is highly prevalent in patients with diabetes, occurring in more than one in five patients with type 2 diabetes aged over 65 years. In patients with type 2 diabetes and high cardiovascular risk, empagliflozin reduced heart failure hospitalization and cardiovascular death when added to standard of care.
>
> In the EMPA-REG OUTCOME trial, empagliflozin reduced the risk of hospitalization for heart failure or cardiovascular death by 34%. The number needed to treat to prevent one event was 35 over 3 years.
>
> The diagnosis of heart failure at baseline was based solely on the report of investigators, with no measures of cardiac function or biomarkers recorded. Empagliflozin reduced heart failure hospitalization and cardiovascular death when added to standard care. The benefit was consistent in patients with and without heart failure at baseline.

**修正内容:**
- エムダッシュ（—）を削除
- 重要性の誇張を削除（"pivotal challenge", "evolving landscape", "groundbreaking", "cornerstone"）
- プロモーション言語を削除（"profound impact", "remarkable finding", "exciting findings"）
- 曖昧な引用を具体的な試験名に置換（"Studies have shown" → EMPA-REG OUTCOME）
- 表面的な -ing 表現を削除（"underscoring", "highlighting"）
- コピュラ回避を修正（"serves as" → "is"）
- AI 多用語を削除（"Additionally", "crucial", "pivotal"）
- 型にはまった課題セクションを削除（"Despite challenges... future outlook"）
- 一般的ポジティブ結論を削除（"The future looks bright", "continue to reshape"）
- 簡潔な文構造と具体的データに統一

---

## Reference

- [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)
- Medical examples adapted from: Fitchett D, Inzucchi SE, Cannon CP, et al. *Circulation*. 2019;139(11):1384-1395. doi:10.1161/CIRCULATIONAHA.118.037778 (CC-BY-4.0)
