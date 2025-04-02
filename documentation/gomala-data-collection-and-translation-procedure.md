# Documentation of Ghomala Data Collection Process

This document outlines the process used for collecting and processing the Ghomala language dataset from Hugging Face, specifically the French-Ghomala-Bandjoun dataset.

## Dataset Overview

The dataset can be found at the following link:
[French-Ghomala-Bandjoun Dataset](https://huggingface.co/datasets/stfotso/french-ghomala-bandjoun)

## Steps Taken

### 1. Dataset Acquisition

- I located the dataset on Hugging Face that contains translations from French to Ghomala (Bandjoun).

### 2. Repository Cloning

- I cloned the repository to my local machine to access the dataset files.

### 3. Processing Single-Word English-French-Ghomala Dataset

For the subset of the dataset containing single-word entries, I performed the following steps:

#### 3.1. Extraction of Single-Word Entries

- I wrote a Python script to extract all entries that contained a single word in Ghomala, regardless of whether they translated to multiple words in French or Bandjoun.

#### 3.2. Translation and Merging Process

- I developed another Python script with the following functionalities:
  - **Text Extraction**: Extract the text from the French column for each entry in the dataset of single words (French-Ghomala-Bandjoun).
  - **Translation**: Utilize the DeepL API to convert the extracted French text into English.
  - **Data Merging**: Combine the translated English text, the original French text, and the corresponding Ghomala text into a single dataset named `single-word-english-french-ghomala`.
  - **File Saving**: Save the merged dataset as an Excel document.

### 4. Processing English-French-Ghomala Dataset

For the dataset that includes a mixture of single words and sentences in Ghomala, I undertook the following steps:

#### 4.1. Translation Process

- I employed the same Python script used for French to English translation to:
  - **Text Extraction**: Extract the text from the French column for each entry in the dataset.
  - **Translation**: Convert the extracted French text into English using the DeepL API.
  - **Data Merging**: Merge the translated English text, the original French text, and the corresponding Ghomala text into a dataset named `english-french-ghomala`.
  - **File Saving**: Save the completed dataset as an Excel document.

## Conclusion

The process described above details the steps taken to extract, translate, and compile the Ghomala dataset from Hugging Face. By utilizing Python scripts and the DeepL API, I was able to create two comprehensive datasets that include translations between English, French, and Ghomala.