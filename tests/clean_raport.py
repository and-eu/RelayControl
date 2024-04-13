from bs4 import BeautifulSoup
import json


def clean_html_report(source_html_file, target_html_file=None):
    if target_html_file is None:
        target_html_file = source_html_file

    with open(source_html_file, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    data_container = soup.find(id="data-container")
    json_data = json.loads(data_container['data-jsonblob'])

    tests = json_data["tests"]
    filtered_tests = {}
    removed_count = 0
    for test_name, results in tests.items():
        if any("Skipped: Runs only" in result["log"] for result in results):
            removed_count += 1
        else:
            filtered_tests[test_name] = results

    json_data["tests"] = filtered_tests
    data_container['data-jsonblob'] = json.dumps(json_data)

    skipped_tag = soup.find('span', class_='skipped')
    if skipped_tag:
        current_skipped = int(skipped_tag.text.split()[0])
        new_skipped = max(current_skipped - removed_count, 0)
        skipped_tag.string = f"{new_skipped} Skipped,"

    with open(target_html_file, 'w') as file:
        file.write(str(soup))


if __name__ == "__main__":
    clean_html_report(r'C:\Users\andre\PycharmProjects\RelayControl\tests\test_results\2024-04-13_10-01-26\report.html')
