## What I caught and corrected

### 1. "All Crates" vs "Plastic" logic error
KIRO built all KPIs and charts using all crate types by default. 
The task specifically asks about plastic crates. I caught this 
when the KPI showed "All Crates Ratio: 100%" which made no sense 
for the business question. I corrected this to default to plastic 
and made the metrics plastic-specific throughout.

### 2. Top N slider — removed
KIRO added a configurable "Top N performers" slider. The requirement 
explicitly states top 5. I removed the slider and hardcoded N=5 
to stay true to the spec.

### 3. Bump chart vs line chart
KIRO initially built a line chart with raw rolling counts on Y axis. 
With only 67 rows of data, counts maxed at 3 making the chart 
unreadable. I researched alternatives and decided on a bump chart 
showing rank position instead — this tells the business story 
more clearly regardless of data volume.

### 4. Data sparsity
The dataset contains only 67 orders across 4 years. This makes the 
rolling 3-month window produce sparse and sometimes random-looking 
rankings. I filtered the bump chart to the last 12 months to make 
it more readable and added a note in the README about this limitation.

### 5. Company name standardisation — rolled back
I initially asked KIRO to standardise similar company names 
(e.g. "Seafood Supplier" → "Seafood GmbH") but then realised 
they had different company_ids meaning they are genuinely 
different companies. I rolled this back to avoid incorrect 
data manipulation.

### 6. Sales owner exploding
KIRO suggested keeping sales owners as a list. I decided to 
explode them into individual rows because the business question 
requires per-owner analysis. This creates duplicate order_ids 
which I documented as an assumption.

## What I would improve with more time
If I had more time, the first thing I would address is the data pipeline itself. The raw data has structural issues that ideally should be fixed at source rather than patched during analysis. Contact name and surname are stored together in a single nested field, which required manual parsing — in a production pipeline these would be separate columns from the start.

The multiple sales owners per order was the most confusing part of the dataset. A single order_id can have two or three different sales owners attached to it, which raises a genuine business question are they collaborating on the same sale, or is this a data quality issue? I resolved it by exploding each owner into their own row, but without clarity from the business on what this relationship actually means, that assumption could be wrong. This is something I would validate with the Data Engineering team before building any production logic on top of it.

Company naming was another area I would improve. Some companies appear under slightly different spellings but share the same company_id those are clearly the same entity and I standardised them. However others have similar names but different company_ids, which makes it impossible to know from the data alone whether they are genuinely different companies or just data entry errors. Fuzzy matching combined with a business validation step would be the right approach here.
On the training threshold the 30% default I set is arbitrary. In a real context I would work with the Sales team to define this based on historical benchmarks, team averages, or business targets. A data-driven threshold would make the training needs chart far more actionable.

Finally, the data sparsity is the biggest limitation of this analysis. 67 orders spread across four years makes the rolling 3-month window produce rankings that shift randomly rather than telling a meaningful story. In the real world this data would be far more continuous and the bump chart would be genuinely insightful. I mitigated this by filtering to the last 12 months, but the fundamental issue is the volume of data available.

## Assumptions
