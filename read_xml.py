from bs4 import BeautifulSoup
import bs4
import requests
import pandas as pd


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


def save_html_content(links: list, file_path: str = "xml_content.csv"):
    documents = []

    for link in links:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")

        content = soup.find_all(["h1", "h2", "h3", "p"])
        cnt = 0
        while cnt < len(content):
            chunck = content[cnt]

            if chunck.name in ["h1", "h2", "h3"]:
                header = chunck.text
                temp_idx = cnt + 1
                while temp_idx < len(content) and content[temp_idx].name == "p":
                    paragraph = content[temp_idx].text
                    documents.append(
                        {"header": header, "paragraph": paragraph, "source": link}
                    )
                    temp_idx += 1
                cnt = temp_idx

            else:
                cnt += 1

    df = pd.DataFrame.from_dict(documents)
    df.to_csv(file_path, ";")


if __name__ == "__main__":
    links = read_xml()
    save_html_content(links[3:])
