import json

class Library:
    def __init__(self):
        self.books = []

    def load_from_file(self,path ):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            self.books = []
            return
        
        self.books = []
        for d in data:
            self.add_book(d["name"], int(d["rating"]), d["genre"])   
        
    def save_to_file(self, path ):
        data = []
        for b in self.books:
            data.append({"name": b["name"], "rating": b["rating"], "genre": b["genre"]})
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        

    def add_book(self, name, rating, genre):
        
        if self.book_exists(name):
            return None
        
        book = {
            
            "name": name,
            "rating": int(rating),
            "genre": genre.strip().title()

        }
        
        inserted = False
        for i, tempbook in enumerate(self.books):
            if (book["rating"] > tempbook["rating"]) or (book["rating"] == tempbook["rating"] and book["name"] < tempbook["name"]):
                self.books.insert(i, book)         
                inserted = True
                break
        if not inserted:
            self.books.append(book)
        return book

    def highest_rating(self, x):
        if x <= 0:
            return []
        count = 0
        top_rated_books = []
        for book in self.books:
            top_rated_books.append(book)
            count += 1
            if count == x:
                return top_rated_books
        return top_rated_books
        

    def books_in_a_genre(self, genre):
        target = genre.strip().title()
        genre_books = []
        for book in self.books:
            if book["genre"] == target:
                genre_books.append(book)
        return genre_books
    
    def book_exists(self, name: str) -> bool:
        for b in self.books:
            if b["name"] == name:
                return True
        return False
    

def print_books(label, books):
    print(f"\n{label}:")
    if not books:
        print("None")
        return
    else:
        for book in books:
            print(f"{book['name']} - {book['rating']} - {book['genre']}")


if __name__ == "__main__":
    # Build a library and add a few books (int ratings, as per your design)
    lib = Library()

    lib.load_from_file("books.json")
    
    print("Welcome to Library")
    print("1 for Enter Add / 2 for Top Rated Books / 3 for Genre based books / X to exit: ")
    user_input = input().strip()

    if user_input == "1":
        bookname = input("Book Name:").strip()
        rating = input("Rating: ").strip()
        genre = input("Genre: ").strip()
        lib.add_book(bookname, rating, genre)
    elif user_input == "2":
        number_of_top = input("Number of Top Book: ").strip()
        top_books = lib.highest_rating(int(number_of_top))
        print_books("Top books by rating: ", top_books)
    elif user_input == "3":
        genre = input("Genre: ").strip()
        genre_books = lib.books_in_a_genre(genre)
        print_books("Top books by genre", genre_books)
    else:
        print("Good bye.")

    lib.save_to_file("books.json")

    """

    # Highest rated (top 3)
    top3 = lib.highest_rating(3)
    print_books("Top 3 by rating", top3)

    # Books in a genre (case-insensitive because you normalized on creation)
    sf = lib.books_in_a_genre("science fiction")
    print_books("Science Fiction", sf)

    # Edge cases
    print_books("Top 0 (edge case)", lib.highest_rating(0))
    print_books("Fantasy (no matches)", lib.books_in_a_genre("Fantasy")) """
