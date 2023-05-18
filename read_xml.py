from bs4 import BeautifulSoup
import requests

# Reading the data inside the xml file to a variable under the name  data
with open("XML Sitemap.xml", "r") as f:
    data = f.read()

# Passing the stored data inside the beautifulsoup parser
bs_data = BeautifulSoup(data, "xml")

# Finding all instances of tag
b_unique = bs_data.find_all("loc")
links = [
    elem.text for elem in b_unique if "jpg" not in elem.text and "png" not in elem.text
]
# print(b_unique)

print(links)


url = links[1]
response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")


print(soup.find_all("p"))

# # Using find() to extract attributes of the first instance of the tag
# b_name = bs_data.find("child", {"name": "Acer"})
# print(b_name)

# # Extracting the data stored in a specific attribute of the `child` tag
# value = b_name.get("qty")
# print(value)
