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