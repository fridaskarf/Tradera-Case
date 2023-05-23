from bs4 import BeautifulSoup
import bs4
import requests


# Reading the data inside the xml file to a variable under the name  data
def read_xml(xml_path="XML Sitemap.xml"):
    with open(xml_path, "r") as f:
        data = f.read()

    # Passing the stored data inside the beautifulsoup parser
    bs_data = BeautifulSoup(data, "xml")

    # Finding all instances of tag
    b_unique = bs_data.find_all("loc")
    links = [
        elem.text
        for elem in b_unique
        if "jpg" not in elem.text and "png" not in elem.text
    ]

    return links
