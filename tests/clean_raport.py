from bs4 import BeautifulSoup
import json, os

def clean_html_report(source_html_file, target_html_file=None, css_file_path=None):
    if target_html_file is None:
        target_html_file = source_html_file

    if css_file_path is None:
        css_file_path= os.path.join(os.path.dirname(source_html_file), 'assets', 'style.css')

    with open(source_html_file, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Process the JSON data for tests
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

    # Update skipped tests count
    skipped_tag = soup.find('span', class_='skipped')
    if skipped_tag:
        current_skipped = int(skipped_tag.text.split()[0])
        new_skipped = max(current_skipped - removed_count, 0)
        skipped_tag.string = f"{new_skipped} Skipped,"

    # Update report title in the <title> and <h1> tags
    title_tag = soup.find('title', id='head-title')
    if title_tag:
        title_tag.string = "RelayControl Test report"

    h1_tag = soup.find('h1', id='title')
    if h1_tag:
        h1_tag.string = "RelayControl Test report"

    # Integrate CSS file if path provided
    if css_file_path:
        with open(css_file_path, 'r') as css_file:
            css_content = css_file.read()
        style_tag = soup.new_tag('style')
        style_tag.append(css_content)
        soup.head.append(style_tag)

    # Write the modified HTML to the target file
    with open(target_html_file, 'w') as file:
        file.write(str(soup))

    os.remove(css_file_path)
    os.rmdir(os.path.dirname(css_file_path))

if __name__ == "__main__":
    html_path = r'C:\Users\andre\PycharmProjects\RelayControl\tests\test_results\2024-04-13_19-19-12\report.html'
    target_html_file = r'C:\Users\andre\PycharmProjects\RelayControl\tests\test_results\2024-04-13_19-19-12\report2.html'
    clean_html_report(html_path, target_html_file)
