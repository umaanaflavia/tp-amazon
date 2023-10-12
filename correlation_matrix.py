import pandas as pd

book_data = pd.read_csv('livros.csv')
titles = book_data['title']
frequently_bought_together = book_data['frequently bought togheter']
num_books = len(titles)
correlation_matrix = [[0 for _ in range(num_books)] for _ in range(num_books)]
line_counter = 0
for i in range(num_books):
    for j in range(num_books):
        if titles[j] in eval(frequently_bought_together[i]):
            correlation_matrix[i][j] = 1

for row in correlation_matrix:
    print(row)