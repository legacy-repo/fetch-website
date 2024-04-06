import os
import time
import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request, Response
from urllib.parse import urljoin

website_name = "gtexportal"
website_baseurl = "https://gtexportal.org"


def get_website_url(gene):
    return f"{website_baseurl}/home/gene/{gene}"


# Define a blueprint for the subroutes
subroute_blueprint = Blueprint("gtex", __name__)

# Route to transfer requests to another server


@subroute_blueprint.route(
    "/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"]
)
@subroute_blueprint.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def transfer_request(path):
    # Make a request to the other server
    print(f"Transfer request: {request.method} {path}")
    response = requests.request(
        method=request.method,
        url=f"{website_baseurl}/{path}?{request.query_string.decode('utf-8')}",
        headers={key: value for (key, value) in request.headers if key != "Host"},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    if path.startswith("js/app") and "text/html" in response.headers.get("Content-Type", ""):
            soup = BeautifulSoup(response.content, "html.parser")

            # 查找所有 href 属性以 /gtex/ 开头的<a>标签
            for link in soup.find_all("a", href=True):
                if link["href"].startswith("/gtex/"):
                    link["href"] = f"https://localhost:3000{link['href']}"

            # 修改后的 HTML 作为新的响应内容
            new_content = soup.prettify()

            # 创建新的 Flask 响应对象
            return Response(new_content, response.status_code, response.headers.items())

    # Create a Flask response object with the response from the other server
    headers = [
        (key, value)
        for (key, value) in response.headers.items()
        if key.lower() != "transfer-encoding" and key.lower() != "content-encoding"
    ]
    return Response(response.content, response.status_code, headers)


def read_css_file():
    """Read the CSS contents from a file."""
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, "r") as css_file:
        return css_file.read()


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def format_url(url, prefix=None):
    if url.startswith("http") or url.startswith("https") or url.startswith("//"):
        return url

    if prefix is None:
        return url
    return f"{prefix}{url}"


# geneSymbol: must be a valid gene symbol
def fetch(req_args={}, cache_dir="cache"):
    """Fetch and convert html page."""
    website_url = get_website_url(req_args.get("geneSymbol"))
    print(f"Fetching website: {website_url}")
    response = requests.get(website_url, headers=headers)
    text = response.text

    soup = BeautifulSoup(text, "html.parser")

    css_contents = read_css_file()
    # Create a new `style` element and insert the CSS contents
    style_tag = soup.new_tag("style")
    style_tag.string = css_contents
    soup.head.append(style_tag)

    # Find all <a> tags and add the `target` attribute
    for a in soup.find_all("a"):
        a.attrs["target"] = "_blank"
        if "href" in a.attrs:
            # Resolve relative links
            a.attrs["href"] = urljoin(website_baseurl, format_url(a["href"], "/gtex"))

    for link in soup.find_all("link"):
        if "href" in link.attrs:
            # Resolve relative links
            link.attrs["href"] = urljoin(
                website_baseurl, format_url(link["href"], "/gtex")
            )

    for script in soup.find_all("script"):
        if "src" in script.attrs:
            # Resolve relative links
            script.attrs["src"] = urljoin(
                website_baseurl, format_url(script["src"], "/gtex")
            )

    for img in soup.find_all("img"):
        if "src" in img.attrs:
            # Resolve relative links
            img.attrs["src"] = urljoin(website_baseurl, format_url(img["src"], "/gtex"))

    # Write the modified HTML back to a file
    output_dir = os.path.join(cache_dir, website_name)
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, time.strftime("%Y%m%d-%H%M%S") + ".html")
    with open(output_file, "w") as f:
        f.write(str(soup))

    return output_file
