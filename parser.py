from BeautifulSoup import BeautifulSoup
from collections import Counter
import csv
import sys
import requests
import argparse
import time
import logging
import operator


logger = logging.getLogger()
DEFAULT_URL = "https://twitter.com/search?f=tweets&vertical=default&q=%23{}&src=typd"


def setup_parser():
    parser = argparse.ArgumentParser(
        description="Scrape twitter for usernames in hashtag mentions"
    )
    parser.add_argument(
        'hashtag',
        metavar='TAG',
        type=str,
        help='Hashtag with or without #'
    )
    parser.add_argument(
        'time',
        metavar='TIME',
        type=int,
        help="Time in seconds to parse for"
    )
    parser.add_argument(
        '--file',
        dest='f_name',
        metavar='FILE',
        type=str,
        default='output.csv',
        help="Optional output CSV location"
    )
    parser.add_argument(
        '--period',
        dest='period',
        metavar='PER',
        type=int,
        default=15,
        help="Period in seconds between polls"
    )
    parser.add_argument(
        '-V',
        dest='verbose',
        action='store_true',
        default=False,
        help='Print debug output'
    )
    parser.add_argument(
        '-H', '--histogram',
        dest='histogram',
        action='store_true',
        help='Print histogram of results'
    )
    return parser


def setup_logger(verbose):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(levelname)s- %(message)s\n\n')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logging.getLogger("requests").setLevel(logging.DEBUG if verbose else logging.WARNING)


def parse_mentions(tweet):
    """
        Extracts all Twitter username mentions from a tweet

        Args:
            tweet (:class:`Tag`): Tag object containing tweet
        Returns:
            :class:`list`: List of usernames in string form
    """
    if not tweet:
        return []
    ment_soup = BeautifulSoup(str(tweet))
    ments = ment_soup('a', 'twitter-atreply')
    users = [user.text for user in ments]
    return users


def poll_loop(args):
    """
        Compiles frequency of username mentions in a hashtag

        Args:
            args (:class:`argparse.Namespace`) Arg list

        Returns:
            :class:`dict`: Dictionary of usernames to mention number mapping
    """
    old_tweets = []
    if args.hashtag[0] == "#":
        args.hashtag = args.hashtag[1:]
    url = DEFAULT_URL.format(args.hashtag)
    start = time.time()
    mentions = []
    while time.time() - start < args.time:
        poll_start = time.time()
        page = requests.get(url).content
        soup = BeautifulSoup(page)
        tweets = soup('p','TweetTextSize  js-tweet-text tweet-text')
        for tweet in tweets:
            if tweet in old_tweets:
                continue
            logger.debug("Adding Tweet:\n%s", tweet.text)
            old_tweets.append(tweet)
            ments = parse_mentions(tweet)
            if ments:
                for user in ments:
                    mentions.append(user)
        sleep_time = max(0, args.period - (time.time() - poll_start))
        logger.debug("Poll completed. Sleeping for %d s", sleep_time)
        time.sleep(sleep_time)
    logger.debug("Raw results: %s", mentions)
    return Counter(mentions)


def print_histogram(data):
    """
        Formats the data as a histogram and prints it

        Args:
            data (:class:`dict`): A dictionary of username to mention number mappings
    """
    if not data:
        return
    sorted_data = sorted(data.items(), key=operator.itemgetter(1))
    sorted_data.reverse()
    hist = ''
    format_spec = '\n{0: <16}:{1}'
    for name, mentions in sorted_data:
        hist += format_spec.format(name, '*'*mentions)
    logger.info("Histogram:%s", hist)

def main():
    parser = setup_parser()
    args = parser.parse_args()
    setup_logger(args.verbose)
    results = poll_loop(args)
    result_str = "Results:"
    fieldnames = ['Username', 'Number of Mentions']
    with open(args.f_name, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in results.items():
            writer.writerow({'Username': key, 'Number of Mentions': value})
            result_str += "\n%s: %d" % (key, value)
    logger.info(result_str)
    if args.histogram:
        print_histogram(results)
    return 0

if __name__ == "__main__":
    sys.exit(main())
