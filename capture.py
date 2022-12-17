import json
import os
import sys
import time
from datetime import datetime

from playwright._impl._api_types import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from get_spec import get_spec

if not len(sys.argv) == 2:
    print("Usage: {} CAPTURE_SPEC_NAME".format(os.path.basename(__file__)))
    exit(1)

capture_spec_name = sys.argv[1]
spec, capture_spec_dir = get_spec(capture_spec_name)

urls = spec["urls"]

new_capture_dirname = os.path.join(
    capture_spec_dir, datetime.now().strftime("%Y-%m-%d_%H.%M")
)
if os.path.exists(new_capture_dirname):
    print("ERROR: new capture dirname {} exists somehow".format(new_capture_dirname))
    exit(1)

os.mkdir(new_capture_dirname)


def iterate_locator(locator):
    for i in range(locator.count()):
        yield locator.nth(i)


script = """e => {
  const styles = {...window.getComputedStyle(e)};
  const parentStyles = {...window.getComputedStyle(e.parentElement)};
  Object.keys(parentStyles).forEach(k => {
    if (styles[k] == parentStyles[k]) delete styles[k];
  });
  return styles;
}
"""


def details(element):
    styles = element.evaluate(script)
    output = dict(
        tag_name=element.evaluate("e => e.tagName"),
        class_name=element.evaluate("e => e.className"),
        computed_style=styles,
        children=[],
    )
    for subelement in iterate_locator(element.locator("xpath=*")):
        output["children"].append(details(subelement))

    return output


with sync_playwright() as p:
    for i, url in enumerate(urls):
        browser = p.chromium.launch()
        page = browser.new_page()
        print("Loading {}".format(url))
        page.goto(url)

        # em_sizes = [46, 49, 39, 49, 36, 65, 81, 97]
        em_sizes = [97]

        for em_size in em_sizes:
            width = em_size * 16
            height = int(width * 0.75)
            print("Setting page size to {}x{} and waiting...".format(width, height))
            page.set_viewport_size({"width": width, "height": height})

            # TODO: make this wait for something instead
            time.sleep(10)

            print(
                "Calculating capture (mostly calling getComputedStyles on everything)"
            )
            print("Calculating for head")
            head_results = details(page.locator("head").first)
            print("Calculating for body")
            body_results = details(page.locator("body").first)
            results = {"head": head_results, "body": body_results}

            fn = "cap_{}x{}__url{}.json".format(width, height, i + 1)
            print("Done, writing file {}".format(fn))

            with open(os.path.join(new_capture_dirname, fn), "w") as file:
                json.dump(results, file, indent=4)

        browser.close()
