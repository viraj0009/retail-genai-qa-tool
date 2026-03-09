few_shots = [
{
    "Question": "How many t-shirts do we have left for Nike in extra small size and black color?",
    "SQLQuery": "SELECT SUM(stock_quantity) FROM t_shirts WHERE brand='Nike' AND color='Black' AND size='XS'",
    "SQLResult": "[(83,)]",
    "Answer": "83"
},
{
    "Question": "How many white color Levi's t shirts we have available?",
    "SQLQuery": "SELECT SUM(stock_quantity) FROM t_shirts WHERE brand='Levi' AND color='White'",
    "SQLResult": "[(72,), (100,), (51,)]",
    "Answer": "223"
},
{
    "Question": "What is the total price of all small-size T-shirts currently in stock?",
    "SQLQuery": "SELECT SUM(price * stock_quantity) FROM t_shirts WHERE size='S'",
    "SQLResult": "[(Decimal('386'),)]",
    "Answer": "386"
}
]