from keyword_extraction import *

def extract_mdna_and_keywords_to_add_to_db():
    #this function will automatically extract mdna sections from companies and extract keywords from them
    #keywords will be added to the local db

    extractor = Extract()
    extractor.keyword_extraction()

def stock_price_prediction():
    #this part includes actual stock price prediction procedures

    pass

def main():
    extract_mdna_and_keywords_to_add_to_db()

if __name__ == '__main__':
    main()