import os
import pdfplumber
import logging
import multiprocessing
from docx import Document

# Set up logging to track the progress of PDF conversion
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pdf_conversion.log"),  # Save logs to a file
        logging.StreamHandler()  # Display logs in the console
    ]
)

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using the pdfplumber.

    :param pdf_path: Path to the input PDF file.
    :return: Extracted text as a string.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
    except Exception as e:
        logging.error(f"Failed to extract text from {pdf_path}: {str(e)}")
        return None

    return text.strip() if text else None

def save_text_to_word(text, output_path):
    """
    Saves extracted text to a Word document.

    :param text: Extracted text from the PDF.
    :param output_path: Path to save the generated Word file.
    """
    try:
        doc = Document()
        doc.add_paragraph(text)
        doc.save(output_path)
        logging.info(f"Word document saved: {output_path}")
    except Exception as e:
        logging.error(f"Failed to save Word file {output_path}: {str(e)}")

def process_pdf(pdf_path, output_folder):
    """
    Processes a single PDF file, extracting texts and converting it to MsWord format.

    :param pdf_path: Path to the input PDF file.
    :param output_folder: Directory where the converted Word file will be saved.
    """
    pdf_filename = os.path.basename(pdf_path)
    docx_filename = pdf_filename.replace(".pdf", ".docx")
    docx_path = os.path.join(output_folder, docx_filename)

    logging.info(f"Processing the file: {pdf_filename}")

    extracted_text = extract_text_from_pdf(pdf_path)
    if extracted_text:
        save_text_to_word(extracted_text, docx_path)
        logging.info(f"Conversion successful: {pdf_filename} -> {docx_filename}")
    else:
        logging.warning(f"No text extracted from {pdf_filename}, skipping conversion.")

def convert_pdfs_to_word(pdf_folder, output_folder, num_workers=3):
    """
    Converts all PDFs into a folder to Word format using multiprocessing.

    :param pdf_folder: Directory containing the PDF files.
    :param output_folder: Directory where Word documents will be saved.
    :param num_workers: Number of parallel processes to speed up the conversion.
    """
    os.makedirs(output_folder, exist_ok=True)  # Ensure output directory exists

    pdf_files = [
        os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith(".pdf")
    ]

    if not pdf_files:
        logging.warning("No PDF files found in the specified directory.")
        return

    # Use the multiprocessing for parallel processing of PDFs
    with multiprocessing.Pool(processes=num_workers) as pool:
        pool.starmap(process_pdf, [(pdf_file, output_folder) for pdf_file in pdf_files])

    logging.info("All PDF files have been processed successfully.")

if __name__ == "__main__":
    PDF_FOLDER = "D://pythontest//data-driven-software-engineer-evaluation//data-processing//pdfs"
    OUTPUT_FOLDER = "word_documents"
    NUM_WORKERS = multiprocessing.cpu_count()  # Uses all the available CPU cores

    convert_pdfs_to_word(PDF_FOLDER, OUTPUT_FOLDER, NUM_WORKERS)