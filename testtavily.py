from tools.tavily_tool import tavily_search

# res = tavily_search("tell me best hotel around the newyork city")
# print(res)
from tools.flight_tool import search_flights
#res= (search_flights("Plan a 7 days Japan trip from Bangladesh"))
from backend import run_travel_agent

user_input = input("Enter travel request: ")
res= run_travel_agent(user_input= user_input,thread_id="test_use")
print(res['answer'])