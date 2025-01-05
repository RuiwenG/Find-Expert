<p>This repo contains one script "find_scrape.py" that collects Name and About data from the website https://intro.co/marketplace. </p>
<p>It also contains 5 CSV files that has experts info corresponding to five catogories that the website provides: Top experts, Home, Wellness, Career & Business, and Style & Beauty.</p>
<p>Note that people in the category of top experts can also be shown in other categories.</p>
<p>profiles.cvs contains only the unqiue profiles among profiles 0-4.</p>
<p>text_embedding.py converts the About section to vector form using OpenAI's text embedding module "text-embedding-ada-002", and output to output.json. </p>
