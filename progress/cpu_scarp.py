import re
import pandas as pd

# Membaca konten file HTML
with open('cpu_list.php', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Cari bagian tbody untuk menghindari header/footer
tbody_match = re.search(r'<tbody>(.*?)</tbody>', html_content, re.DOTALL)
if tbody_match:
    tbody_content = tbody_match.group(1)
else:
    tbody_content = html_content

# Regex untuk mengekstrak baris (tr) dan kolom (td)
row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
col_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
tag_cleaner = re.compile(r'<.*?>') # Pembersih tag HTML

data = []

# Iterasi setiap baris untuk mengambil data
for row_match in row_pattern.finditer(tbody_content):
    cols = col_pattern.findall(row_match.group(1))
    
    if len(cols) >= 5:
        data.append({
            'CPU Name': re.sub(tag_cleaner, '', cols[0]).strip(),
            'CPU Mark': re.sub(tag_cleaner, '', cols[1]).strip(),
            'Rank': re.sub(tag_cleaner, '', cols[2]).strip(),
            'CPU Value': re.sub(tag_cleaner, '', cols[3]).strip(),
            'Price': re.sub(tag_cleaner, '', cols[4]).strip()
        })

# Membuat DataFrame dan menyimpannya ke CSV
df = pd.DataFrame(data)
df.to_csv('cpu_bm.csv', index=False)