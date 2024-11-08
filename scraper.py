# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time


ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'source_url']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source', 'source_url']

def csv_writer(source_field, ind_sort_by, outpath):
    targetfile = open('data/' + outpath, mode='w', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, 
                       quoting=csv.QUOTE_ALL,  # Quote all fields
                       escapechar='\\',        # Use backslash as escape character
                       doublequote=True)       # Double quotes within fields
    writer.writerow(HEADER)
    return writer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--o', type=str, default='output.csv', help='output directory')
    parser.add_argument('--sort_by', type=str, default='newest', help='most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()

    # store reviews in CSV file
    writer = csv_writer(args.source, args.sort_by, args.o)

    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:
                url = url.strip()  # Remove any whitespace or newline characters
                print(f"Processing URL: {url}")
                source_url = url  # Store the original URL
                if args.place:
                    print(scraper.get_account(url))
                else:
                    if 'cid=' in url or 'consent.google.com' in url or '/maps/place/' not in url:
                        print("CID, consent URL, or non-standard URL detected. Attempting to get full URL...")
                        url = scraper.get_full_url_from_cid(url)
                    print(f"Sorting reviews for URL: {url}")
                    error = scraper.sort_by(url, ind[args.sort_by])

                    if error == 0:
                        n = 0

                        while n < args.N:
                            print(colored(f'[Review {n}]', 'cyan'))
                            reviews = scraper.get_reviews(n)
                            if len(reviews) == 0:
                                print("No more reviews found.")
                                break

                            for r in reviews:
                                row_data = list(r.values())
                                row_data.append(source_url)  # Add the source URL to each review
                                writer.writerow(row_data)

                            n += len(reviews)
                    else:
                        print(f"Error occurred while sorting reviews. Error code: {error}")
