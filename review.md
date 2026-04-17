Section 9 — Simplify contact_data: Strips out city, cp, and anything else — keeps only contact_name and contact_surname. So instead of {'contact_name': 'Curtis', 'contact_surname': 'Jackson', 'city': 'Chicago', 'cp': '12345'} you'll just see {'contact_name': 'Curtis', 'contact_surname': 'Jackson'}
## I never asked to strip out : in number 9 I never said to strip out Strip out city, cp, and any other fields. 
answer : You're right, my mistake. You said to extract contact_name and contact_surname and standardise the format — not to remove the other fields. Let me fix that cell to keep all the original fields intact.

Second review it did not remove the contact name & surname wrapper around it on the contact data 
##still same issue on the contact_data we need to remove the rest around it & keep the name & surname only  [{'contact_name': 'Curtis', 'contact_surname':... 

##similar company names but not the same company ID 
I see there is a small issue I made you chnage some copany names like seafood supplier to add GmbH but I noticed they don't have the same company ID so it is not the same company then I guess plus we did the same for fresh fruits Co so we need to maybe rollback 
once rollbacked make sure you recode the dataRead so we can get to the final verdict 
Answer : resh Fruits c.o -> Fresh Fruits Co (same company_id 1e2b47e6...)
healthy snacks c.o. -> Healthy Snacks (same company_id 20dfef10...)

Ai was recomending : 
Explode into separate rows — one row per sales_owner per order. So an order with 3 owners becomes 3 rows. This is the best approach if you want charts like "orders per salesperson", "revenue per salesperson", or salesperson filters. The downside is your row count goes from 62 to ~150, but that's standard for this kind of analysis.

Keep the list but add a primary_sales_owner column — take the first name as the "lead" and keep the full list for reference. Good if you want one salesperson per row for charts but still want to show the full team in a detail view.

Pivot into separate columns — sales_owner_1, sales_owner_2, sales_owner_3. Simple but rigid, and makes filtering harder. 
My review : making more rowns for each sales person will equal to duplicating order_id which is not good either 

## The ai app was making things harcoded & not dynamic so I had to make sure is not harcoding the things & the KPI's change as per the crate type dynamically 

## re guiding the AI for the appropiate chart & data 
no what I need as an answer is the following : 

we need to be able to look back 3 months behinf & current month  

sum of each owner who is selling plastic crate, wooden crate or any crate... basically as per the filter it should adap dinamically 

Rank the owners 

plot also how the ranks shifts month by month 

I think of the research I have been doing on google a Bump chart would be appropiate to visualize this which I think we had something similiar in the beginning 

## ranking issue 
I found a small issue in the training needs I want the lowest to be ranked all the way up so we truly know who needs the training 