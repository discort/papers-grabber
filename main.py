from datetime import datetime
from typing import NamedTuple

import click
import requests
import xmltodict


class Paper(NamedTuple):
    source: str
    posted: str
    title: str
    summary: str
    link: str


class Source:
    source_name = None
    url = None


class Arxiv(Source):
    """
    https://arxiv.org/help/api/user-manual
    """
    source_name = "arxiv.org"
    url = "http://export.arxiv.org/api"

    def search(self, query, date):
        """
        Top 10 the most recent interesting Papers
        """
        resp = requests.get(
            f"{self.url}/query?search_query=all:{query}&sortBy=submittedDate"
            "&sortOrder=descending&start=0&max_results=10"
        )
        assert resp.status_code == 200, f"Error: {resp.text}"

        data = xmltodict.parse(resp.text)
        result = []
        for paper in data['feed'].get('entry'):
            result.append(
                Paper(source=self.source_name,
                      posted=paper["published"],
                      title=paper["title"],
                      summary=paper["summary"],
                      link=paper["id"])
            )
        return result


class Biorxiv(Source):
    """
    https://www.rxivist.org/docs#Preprints-Search
    """
    source_name = "biorxiv.org"
    url = "https://api.rxivist.org/v1/papers"

    def search(self, query, date):
        """
        Top 10 the most interesting papers on a day based on twitter data (from Crossref)
        """
        resp = requests.get(f"{self.url}?q={query}&metric=twitter&timeframe=day&page_size=10")
        assert resp.status_code == 200, f"Error: {resp.text}"

        data = resp.json()
        result = []
        for paper in data['results']:
            result.append(
                Paper(source=self.source_name,
                      posted=paper["first_posted"],
                      title=paper["title"],
                      summary=paper["abstract"],
                      link=paper["biorxiv_url"])
            )
        return result


def print_paper(paper):
    print(f"####**{paper.title}**")
    print(f"(Submitted on {paper.posted})")
    print("\n")
    print(paper.summary)
    print(paper.link)
    print("---")


@click.command()
@click.option("-d", "--date", default=datetime.today().date().strftime("%Y-%m-%d"),
              help="Paper posted date. (Currently not supported for arxiv, biorxiv)")
@click.option("-q", "--query", required=True)
def main(date, query):
    """
    Simple script to fetch papers on provided date
    from arxiv.org, biorxiv.org
    """
    sources = [Arxiv(), Biorxiv()]
    for source in sources:
        papers = source.search(query, date)
        for p in papers:
            print_paper(p)


if __name__ == '__main__':
    main()
