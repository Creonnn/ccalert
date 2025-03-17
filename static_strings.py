schema = "```products table: \n\
+-------------+---------+\n\
| Column Name | Type    |\n\
+-------------+---------+\n\
| id          | int     |\n\
| model       | varchar |\n\
| gpu         | varchar |\n\
| url         | varchar |\n\
| brand       | varchar |\n\
+-------------+---------+\n\n\
locations table:\n\
+-------------+---------+\n\
| Column Name | Type    |\n\
+-------------+---------+\n\
| id          | int     |\n\
| location    | varchar |\n\
| timezone    | varchar |\n\
+-------------+---------+\n\n\
stock_data table:\n\
+-------------+---------+\n\
| Column Name | Type    |\n\
+-------------+---------+\n\
| model_id    | int     |\n\
| location    | varchar |\n\
| quantity    | int     |\n\
| price       | int     |\n\
| timestamp   | varchar |\n\
+-------------+---------+\n\
model_id is a foreign key to id from the products table.\n\n\n\
Note: if you're going to filter, please make sure the filter terms are properly spelled and capitalized.\n\
Note: a discord message can only be at most 2000 characters long. Queries that are too big will be truncated.\n\
Note: data was collected starting from Feb 17 2025. ```"

help = "```!locations: returns list of all CC locations.\n\n\
!chart: returns all GPU stock data as a chart. You can filter by passing in additional arguments for locations and/or GPUs. Make sure all spelling is correct.\n\
e.g. !chart location=Toronto Kennedy/Etobicoke, gpu=5090/5080\n\n\
!achart: returns all AMD GPU stock data as a chart. You can filter by passing in additional argument for location. Make sure all spelling is correct.\n\
e.g. !achart Etobicoke\n\n\
!nchart: returns all NVIDIA GPU stock data as a chart. You can filter by passing in additional argument for location. Make sure all spelling is correct.\n\
e.g. !nchart Etobicoke\n\n\
!instock: gives list of items that are currently in stock. You can filter by passing in additional argument for location and/or gpu. Make sure all spelling is correct.\n\
e.g. !instock location=Etobicoke, gpu=5090\n\n\
!me: gives a filtered list of all items that are currently in stock based on your Discord roles.\n\
e.g. !me\n\n\
!rank: Returns total stock received by each store. Optionally pass in GPU as parameter\n\
e.g. !rank 5090\n\n\
!topsku: gets top SKUs. Optionally pass in GPU as parameter.\n\
e.g. !topsku 5090\n\n\
!hour: gets all-time distribution of which hour that items gets scanned in. Optionally pass in location as parameter.\n\
e.g. !hour Etobicoke\n\n\
Note: Data collection started on Feb 17 2025\n\
Note: Queries that are too big will be truncated. Try filtering to limit results.```"
