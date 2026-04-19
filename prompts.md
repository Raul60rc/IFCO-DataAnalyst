## First Prompt after checking the data 
so we have the dataset currently I have explored it also there are just some issues to deal with first I need to have all columns into snake_case which currently salesowners is not later I have noticed we have the data. Also i have noticed the data is jammed into one string which we need to fix first also have seperators. We need to standarise this now, check the dataRead.ipynb file I am trying to fixt this data first later we will spec out the streamlit part with all the requirements I will give you for now we need to fix this first 

## Second Prompt to make sure to standarise data & organise plus understanding of it 
The data looks good now what I need to do now is make sure the date is DD/MM/YYYY also have a look into the contact_data I still see some contact data being like this : [{'contact_name': 'Maria', 'contact_surname': ... some of them are empty maybe we can look into the company ID & fill the NaN data if the company ID matches to fill the null data also . Also I would like to understand the sales owners we have two to three sales owner into one : [Leonard Cohen, Luke Skywalker, Ammy Winehouse] so I guess they are mutiple sales_owner selling to the same client ? 

## Third prompt 
okay we need to make some standarisation so I see the company_name Seafood Suppllier some has GmbH in the end some dont so let's make sure the Seafood Supplier is called Seafood GmbH also I see the same for "Fresh Fruits c.o & Fresh Fruits Co this will also make it two companies when I guess it is just 1 (let's try to find such cases) . also I still see a mess into the contact data so ler's do something we need the contact name after [{'contact_name': & contact surname after 'contact_surname' : that is it the rest we can remove & standarise it also in the sales_owners what could be the best practice becaue I am unable to understand how can there be more than one seller for one date & same order are they making the sale together ?? help me deep dive on this sales owner part a little 

## Fourth Prompt :
wait are you doing this into the dataRead file ? because I need to check into it also like manually review 

Fifth prompt : so we have no data for Seafood supplier like contact data ? so we can populate it ? 
Same situation for these companies that show up in the "still empty" list:
Seafood Supplier (1c4b0b50...) — 3 orders, never has contact data
Meat Packers Ltd (34538e39...) — 3 orders, never has contact data
Seafood Supplier GmbH (2e90f2b1...) — 3 orders, never has contact data
Veggies Unlimited (9b31b19f...) — 1 order, no contact data
Green World Ltd (012f20c6...) — 1 order, no contact data
Organic Foods Ltd (8347edb3...) — 1 order, no contact data
Seafood Network Ltd (0b8755d4...) — 1 order, no contact data
Fresh Veg Co (1b21f4a3...) — 1 order, no contact data

## fifth prompt : 
okay let's go with unknown  but dont you think making the the sales owners in more rows will make duplicate order_id's ? 

## Sixth prompt : 
I think we will have to individualise the sales owner since we need to know which is the sales owner doing better but this will imply to have duplicated order id's I can't do much on how this data set is being set 

# Seventh Promp : on the notebook I am perfroming some data cleaning & standarisation but I wan you to later create the streamlit app for it to visualize the data standarised we have. So currently we have to first take contact first name & last name make into one column as contact_name 

## eight prompt 
You are a Senior Data Analyst. The data is already cleaned and structured. Your job is to build a production-quality, scalable Streamlit dashboard from scratch.



# Available columns after cleaning:

order_id          # unique order identifier

date              # datetime, already parsed

company_id        # company identifier

company_name      # company name string

crate_type        # e.g. 'Plastic', 'Wood', 'Metal'

sales_owner       # sales owner full name

has_contact       # boolean — whether contact data exists

contact_name      # contact person name

sales_owner_count # number of orders per sales owner (pre-aggregated)



project/

├── app/

│   └── main.py                  ← Streamlit entry point, layout only, no business logic

├── utils/

│   ├── data_loader.py           ← loads and validates the cleaned CSV

│   ├── metrics.py               ← all business logic: ratios, rolling windows, rankings

│   └── charts.py                ← all Plotly figure builders, one function per chart

├── tests/

│   └── test_metrics.py          ← pytest tests for metrics.py functions only

├── data/

│   └── orders.csv               ← cleaned dataset, must be included

├── .streamlit/

│   └── config.toml              ← theme config

├── requirements.txt

├── Dockerfile

└── README.md



Architecture rules:

main.py only calls functions from utils/ — zero business logic in it

charts.py only builds Plotly figures — no aggregation inside it

metrics.py only does pandas computation — no Streamlit calls inside it

No for-loops for aggregations — use groupby(), rolling(), rank()

Use pathlib.Path(__file__).parent for all file paths, never hardcode



Dashboard layout (main.py)

Build the layout in this exact order:

1. Sidebar

Date range filter (min/max from dataset)

Crate type multi-select filter

Plastic ratio threshold slider (default 30%, range 10–60%)

All filters must reactively update all charts and KPIs

2. KPI row — use st.columns(4)

Total orders

Plastic orders

Overall plastic ratio %

Number of sales owners below threshold

Conditional formatting on KPIs — apply to "Overall plastic ratio %" card and "Owners below threshold" card:



# Color logic (apply via st.markdown with inline CSS):

# plastic_ratio >= threshold     → green  (#2d6a4f background, white text)

# threshold * 0.7 <= ratio < threshold → amber  (#e9c46a background, dark text)

# plastic_ratio < threshold * 0.7 → red    (#e63946 background, white text)

# Same logic per owner for Chart 2



Chart specifications

Tab 1 — Distribution of orders by crate type

Donut chart (Plotly go.Pie with hole=0.5)

Show count + percentage in labels

KPI card above: plastic share % with conditional color

Tab 2 — Sales owners who need the most training (last 12 months)

Filter: last 12 months relative to df['date'].max()

Compute: plastic_ratio = plastic_orders / total_orders per sales_owner

Horizontal bar chart, sorted ascending (worst performers at top)

Bar color per owner: green / amber / red based on threshold from sidebar slider

Add a vertical dashed line at the threshold value

X-axis: 0–100%, formatted as percentage

Tab 3 — Top 5 performers: rolling 3-month plastic crate sales

For each month, compute each owner's plastic order count over the rolling 3-month window ending that month

Identify top 5 owners per month by rolling count

Line chart (Plotly Express) with one line per owner

Tooltip: owner name, month (formatted as Mon YYYY), rolling 3-month plastic count

If an owner drops out of top 5, their line breaks — do not fill with zeros

Tests (tests/test_metrics.py)

Write real, executable pytest tests. Requirements:

Import only from utils.metrics — no placeholder imports

Use synthetic DataFrames in each test, never depend on the real CSV

Cover all of these cases:

python

def test_plastic_ratio_basic()        # correct ratio computed def test_plastic_ratio_zero_orders()  # owner with 0 orders → handled, no division error def test_plastic_ratio_null_owner()   # NaN in sales_owner → excluded from results def test_rolling_window_3months()     # rolling sum correct over 3 months def test_rolling_window_sparse()      # months with no data don't break the window def test_top5_per_month()            # returns exactly 5 per month when data allows def test_top5_ties()                 # tie-breaking is consistent (e.g. alphabetical) def test_duplicate_order_ids()       # duplicates are deduplicated before aggregation

Docker

dockerfile

FROM python:3.11-slim WORKDIR /app COPY requirements.txt . RUN pip install --no-cache-dir -r requirements.txt COPY . . EXPOSE 8501 CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

README.md (in English)

Must include exactly:

Project structure overview

Run locally: pip install -r requirements.txt → streamlit run app/main.py

Run with Docker: exact copy-pasteable docker build + docker run commands

Run tests: pytest tests/

KPI conditional formatting thresholds explained

Assumptions: how "last 12 months" is defined, how rolling window handles sparse months, how top-5 ties are broken

Quality checklist before finishing

 All chart labels and UI text in English

 No hardcoded file paths

 No business logic in main.py

 No Streamlit calls in metrics.py

 All tests pass with pytest tests/ from project root

 Docker builds and runs without errors

 Sidebar filters reactively update all three charts

 Conditional formatting uses the threshold from the sidebar slider, not hardcoded

## Ninth prompt 
the top 5 performers has an issue it has too may lines we are showing all owners when we should show top 5 for the current month but we can show all also in the ranking but mainly I am looking for the top 5 plus this line chart is making it extremely hard to read for the stakeholders. 



We need to remove the plastic share KPI which is huge  plus it is already showing it on the top KPI 



We need to maybe rename the owners below threshold of training needed so I am some are at 50% & others are below it so I think 60% is good looks like an average.. 



Another thing I don't like is when I chnage the crate types is not changing the sales owner type also on the training needs plus the KPI above on the plastics ratio like that should be all crates later when we filter to something specific as plastic then the above KPI should also chnage even the owners below threshold like it is showing 11 but I see only 9 of them what about the others are they uknown ? 

KPI colours : KPI color logic: "Owners Needing Training" → red if count > 50% of total owners, amber if 25–50%, green if <25%



Top 5 perfomers 

Instead of plotting raw rolling counts on Y axis,

plot RANK (1=best, 5=worst) on Y axis, inverted (1 at top)

Only show owners who appear in top 5 for at least one month while we need also the three consective months too plus 6 months & 12 months 

One line per owner, markers at each month they appear

If an owner is not in top 5 for a month, their line breaks (no gap fill)

Tooltip: owner name, month, rank, rolling 3-month plastic count

Y-axis: fixed 1–5, inverted, labeled "Rank"

Add annotation: "Rank 1 = highest plastic crate sales that month"

## tenth prompt making dynamic KPI's 
as mentioned when I click the crates type all the training needs should chnage & show as per the filter either is plastic, wood or metal, Plus on the top 5 performers the same it should be also the same basd on the filter which is applied it should the top sellers of the crate, also the KPI's should not show just plastic it should show all if all the crate types are selected  & if two are selected then the KPI's of two if one is selected then one, this I refer to the plastic orders, Plastic ratio & owners need training we need to make sure the ones who are doing poor in other areas they also get the respective training 


## eleventh prompt, 3 month data 
Also in the top 5 perfomers I see we barely have like consistent monthly data like we I see , help me cross check if the data is disperes fully because if it is this makes it difficult to know who is the best sller for 3 consecutive motths : 


## Twelth promt 
are you sure is chris patt & not amy winehouse ? maybe we need to chnage the top 5 perfomers visualization 


## Thirteenth prompt 
serioulsy check the sidebar this is not readable make the text inside the crate types white & improve the crate ratio either make it white also so that we have white & green contrast 

## fourteenth prompt 
why it is showing 3 owners needing training when it should show 5 no ? This is a mistake on Training needs
can we make this dynamic based on the filter of the date range also make the title dyanmic

## Fifteenth prompt 
Okay we need to containarize this project now into a docker so this project is replicable & we need to make sure this works & do the test 
