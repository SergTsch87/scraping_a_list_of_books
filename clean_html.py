from bs4 import BeautifulSoup


def op_file_write(file_path, content):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)


def clean_html_structure(html_content):
    # Parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove unwanted elements
    for tag in soup.find_all(['style', 'form', 'input']):
        tag.decompose()
    
    # Remove unwanted attributes
    unwanted_attrs = ['width', 'valign', 'border', 'bgcolor', 'class', 'align', 'color', 'type', 'name', 'value', 'enctype', 'method', 'action']
    for tag in soup.find_all():
        for attr in unwanted_attrs:
            if attr in tag.attrs:
                del tag.attrs[attr]
    
    # Function to print structure
    def print_structure(element, indent=0):
        if element.name:
            print('  ' * indent + element.name)
            for child in element.children:
                if child.name or (hasattr(child, 'strip') and child.strip()):
                    print_structure(child, indent + 1)
        elif hasattr(element, 'strip') and element.strip():
            # Print text content
            text = element.strip()
            if text:
                print('  ' * indent + repr(text))
    
    print_structure(soup)

# Read the HTML from the file
# f_path = 'untitled:Untitled-6'
f_path = 'dds.html'
with open(f_path, 'r', encoding='utf-8') as f:
    html = f.read()

clean_html_structure(html)