# Corpus of Russian Folk Tales
This corpus consists of **120 Russian folk tales** collected from the website https://skazki-pesni.ru.

## Main Libraries Used

- **fake_useragent** – for bypassing website protection and parsing  
- **nltk** – for tokenization  
- **pymorphy2** – for lemmatization  
- **Natasha** – for POS-tagging and lemmatization  
- **pandas** – for building dataframes  
- **re** – for working with regular expressions  

## Corpus Workflow

The program is divided into several functional blocks:

### 1. Parsing

- `fake_useragent` is used to bypass website protection.  
- The function `get_nth_page` processes a single page from the site (extracts text, title, and fairy tale URL).  
- The function `run_all` takes the number of pages to process and runs them one by one.

### 2. Building the Database

- All texts are split into sentences. Columns are created for: sentences, fairy tale titles, source links, and punctuation-free sentences.  
- Data is saved to the file `fairy_tales_razdel_full.csv`.

### 3. Query Processing and Sentence Search

#### 3.1. Lemmatization, Tokenization, POS-tagging

- POS-tagging, tokenization, and lemmatization are performed using **Natasha** and **pymorphy2**.  
- Results are saved to `corpus.csv`.

#### 3.2. Word Matching Functions

- `check_word_form`: checks all forms of a word, case-insensitive.  
- `check_exact_form`: checks the exact form, case-insensitive.  
- `check_lemma_and_pos`: checks lemma and POS tag.  
- `check_pos`: checks POS tag only.  
- `word_fits_request_part`: calls one of the four functions above based on the query type.

#### 3.3. Main Search Function

- `search`: the main function that accepts a word, quoted word, lemma+POS, or POS only.  
- Returns matched sentences along with the source title and link.

### 4. Collocation Search

- `get_collocations`: takes a word and returns its collocations with frequencies.

### 5. Final Output Program

#### 5.1. Displaying Results

- `pretty_line`: formats a sentence context for display.  
- `get_all_pretty_lines`: outputs all matching results in a formatted way.

#### 5.2. User Interaction  
(see next section)

## User Interaction with the Corpus

1. The user inputs a query:  
   - a single word  
   - a quoted word  
   - lemma+POS  
   - POS only  

2. The program returns:  
   - **All sentences** containing the query, displayed with left/center/right context, source title and link.  
   - **Collocations** of the query with their frequencies.

### Example: user input – `лисичка`

*Забралась | лисичка | в теремок.*  
_Example from "Teremok" – https://skazki-pesni.ru/teremok/_

*Жили-были в лесу | лисичка | и зайка.*  
_Example from "Zayushkina izba" – https://skazki-pesni.ru/zayushkina-izbushka/_

**Collocations:**  
*с лисичкой – 3*  
*лисичкой близко – 3*  
*пришла лисичка – 3*

### Example: user input – `ADV NOUN`

*Бежит | мимо мышка-норушка.*  
_Example from "Teremok" – https://skazki-pesni.ru/teremok/_

*Бежит | мимо зайчик-побегайчик.*  
_Example from "Teremok" – https://skazki-pesni.ru/teremok/_
